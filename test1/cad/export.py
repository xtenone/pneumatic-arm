"""Exporteer de CAD van test 1 naar out/cad/.

- STEP per zelfgemaakt onderdeel en voor de hele samenstelling (arm horizontaal)
- STL per zelfgemaakt onderdeel (bijv. voor 3D-printen of bekijken)
- DXF-profielen van de te zagen en te boren delen (wang, arm, grondplaat)
- GLB van de samenstelling (te bekijken in de browser)
- STL-meshes in lokale assenstelsels voor de MuJoCo-simulatie (out/meshes/)
"""
import os
import sys

import cadquery as cq

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import parts  # noqa: E402

ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "out", "cad")
MESH = os.path.join(ROOT, "out", "meshes")


def main():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(MESH, exist_ok=True)
    for name, fn in parts.MADE_PARTS.items():
        shape = fn()
        cq.exporters.export(shape, os.path.join(OUT, f"{name}.step"))
        cq.exporters.export(shape, os.path.join(OUT, f"{name}.stl"), tolerance=0.1, angularTolerance=0.1)
    # 2D-profielen voor zagen en boren (zijaanzicht, x-z-vlak)
    export_profiles()
    assy = parts.assemble(0.0)
    assy.save(os.path.join(OUT, "test1_samenstelling.step"))
    assy.save(os.path.join(OUT, "test1_samenstelling.glb"))
    export_sim_meshes()
    print("CAD geëxporteerd naar", OUT)


def export_profiles():
    """Zijaanzicht-profielen als DXF (mm): omtrek + gaten, zoals je ze aftekent."""
    import math
    P = parts.P
    jobs = {
        "wang_profiel": dict(rect=(P.CHEEK_X[0], 0.0, P.CHEEK_X[1], P.CHEEK["height"]),
                             holes=[(P.HINGE, 22.0), (P.HINGE, 10.0), (P.REAR_PIVOT, 8.5),
                                    ((P.CHEEK_X[0] + 30, 20.0), 5.0), ((P.CHEEK_X[0] + 30, 45.0), 5.0)]),
        "arm_profiel": dict(rect=(-P.ARM_BEHIND, -P.ARM["height"] / 2,
                                  P.ARM["length"] - P.ARM_BEHIND, P.ARM["height"] / 2),
                            holes=[((x, 0.0), P.ARM_HOLE) for x in (0.0, P.ARM_ATTACH, P.ARM_TIP)]),
        "grondplaat_profiel": dict(rect=(P.BASE_X[0], -P.BASE["width"] / 2, P.BASE_X[1], P.BASE["width"] / 2),
                                   holes=[]),
    }
    for name, j in jobs.items():
        x0, y0, x1, y1 = j["rect"]
        lines = ["0", "SECTION", "2", "ENTITIES"]

        def line(a, b):
            lines.extend(["0", "LINE", "8", "0", "10", f"{a[0]:.3f}", "20", f"{a[1]:.3f}",
                          "11", f"{b[0]:.3f}", "21", f"{b[1]:.3f}"])
        pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        for i in range(4):
            line(pts[i], pts[(i + 1) % 4])
        for (cx, cy), d in j["holes"]:
            lines.extend(["0", "CIRCLE", "8", "GATEN", "10", f"{cx:.3f}", "20", f"{cy:.3f}", "40", f"{d / 2:.3f}"])
        lines.extend(["0", "ENDSEC", "0", "EOF"])
        with open(os.path.join(OUT, f"{name}.dxf"), "w") as f:
            f.write("\n".join(lines) + "\n")


def export_sim_meshes():
    """Meshes in het lokale assenstelsel van elk simulatielichaam."""
    P = parts.P
    statics = (parts.base_plate().union(parts.cheek().translate((0, P.CHEEK_GAP / 2, 0)))
               .union(parts.cheek().mirror("XZ").translate((0, -P.CHEEK_GAP / 2, 0)))
               .union(parts.spacer_block()))
    meshes = {
        "staander": statics,
        "arm": parts.arm(),
        "cilinder": parts.cylinder_body(),
        "potmeter": parts.pot_body(),
        "stang": parts.rod_assembly().union(parts.pot_rod()).union(
            parts.pot_bracket().translate((-P.CYL["rear_pin_from_end"] + P.CYL["overall_retracted"] + 1.5, 0, 0))),
        "fles": parts.bottle(),
    }
    for name, shape in meshes.items():
        cq.exporters.export(shape, os.path.join(MESH, f"{name}.stl"), tolerance=0.2, angularTolerance=0.2)


if __name__ == "__main__":
    main()
