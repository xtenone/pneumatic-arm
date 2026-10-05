"""Generate everything for test 1 from params.py and build the bundle.

    python build.py            # regenerate everything
    python build.py --bundle   # plus a zip in dist/ and a copy to the shared web folder
    python build.py --fast     # without the simulation (CAD, config, drawings, docs only)

Steps: firmware/config.py, CAD export, drawings, simulation (+ renders), bill of
materials, HTML version of the docs, firmware test, bundle.
"""
import csv
import html
import json
import os
import shutil
import subprocess
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
PY = sys.executable
HOSTED = os.path.join(REPO, "..", "..", "hosted", "pneumatic-arm", "test1")


def run(*args, env=None):
    print("→", " ".join(args))
    e = dict(os.environ, **(env or {}))
    subprocess.run([PY, *args], cwd=HERE, check=True, env=e)


def bom():
    """docs/bom.md and .csv from the project order list."""
    d = json.load(open(os.path.join(REPO, "docs", "order-list.json")))
    rows = []
    for b in d["orders"]:
        if b.get("status") == "alternative":
            continue
        for r in b["items"]:
            link = r.get("url") or (f"https://www.aliexpress.com/item/{r['id']}.html" if r.get("id") else "")
            rows.append(dict(order=b["name"], part=r["what"], variant=r.get("variant", ""),
                             qty=r["qty"], price=r["price"], estimate=bool(r.get("estimate")),
                             link=link, note=r.get("note", ""), status=b.get("status", "")))
    with open(os.path.join(HERE, "docs", "bom.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    lines = ["# Bill of materials — test 1", "",
             "Generated from `docs/order-list.json` (repository root) by `build.py`. Prices in euro, "
             "* = estimate. Also as [CSV](bom.csv).", ""]
    total = 0.0
    current = None
    for r in rows:
        if r["order"] != current:
            current = r["order"]
            lines += ["", f"## {current}", "", f"Status: {r['status']}", "",
                      "| # | Part | Variant | Price | Link |", "|---|---|---|---|---|"]
        sub = r["qty"] * r["price"]
        total += sub
        link = f"[link]({r['link']})" if r["link"] else ""
        note = f" — {r['note']}" if r["note"] else ""
        lines.append(f"| {r['qty']} | {r['part']}{note} | {r['variant']} | "
                     f"€{sub:.2f}{'*' if r['estimate'] else ''} | {link} |")
    lines += ["", f"**Total approx. €{total:.0f}** (excluding shipping and import duty).", "",
              "## Tools", ""] + [f"- {g}" for g in d.get("tools", [])]
    with open(os.path.join(HERE, "docs", "bom.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("→ bom:", len(rows), "lines, total", round(total))


CSS = """body{font-family:system-ui,sans-serif;max-width:980px;margin:2rem auto;padding:0 1rem;line-height:1.5;color:#222}
table{border-collapse:collapse;margin:1rem 0}td,th{border:1px solid #ccc;padding:.3rem .5rem;vertical-align:top}
th{background:#f3f3f3}img{max-width:100%}code,pre{background:#f5f5f5}pre{padding:.6rem;overflow:auto}
nav a{margin-right:1rem}"""


def to_html(md_path, out_path, title, nav):
    import markdown
    text = open(md_path, encoding="utf-8").read()
    # Python-Markdown needs a blank line before a list and 4-space indentation for
    # nested lists; GitHub does not. Convert the text accordingly.
    import re
    item = re.compile(r"^(\s*)([-*]|\d+\.)\s")
    out, prev_item_indent, prev = [], None, ""
    for line in text.split("\n"):
        m = item.match(line)
        if m:
            ind = len(m.group(1))
            level = 0 if ind == 0 else (1 if ind <= 4 else 2)
            line = " " * (4 * level) + line.lstrip()
            if prev.strip() and prev_item_indent is None and level == 0 and not prev.startswith("|"):
                out.append("")
            prev_item_indent = level
        elif line.strip() == "":
            prev_item_indent = None
        elif line.startswith((" ", "\t")) and prev_item_indent is not None:
            line = " " * (4 * (prev_item_indent + 1)) + line.lstrip()
        else:
            prev_item_indent = None
        out.append(line)
        prev = line
    text = "\n".join(out)
    body = markdown.markdown(text, extensions=["tables", "fenced_code", "sane_lists"])
    body = body.replace('.md"', '.html"')
    page = (f"<!doctype html><html lang='en'><head><meta charset='utf-8'><title>{html.escape(title)}</title>"
            f"<style>{CSS}</style></head><body><nav>{nav}</nav>{body}</body></html>")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(page)


def html_docs(dest):
    """HTML version of the README, manual, design, BOM and simulation results in `dest`."""
    os.makedirs(os.path.join(dest, "docs"), exist_ok=True)
    os.makedirs(os.path.join(dest, "out", "sim"), exist_ok=True)
    nav_root = ("<a href='index.html'>Test 1</a><a href='docs/manual.html'>Manual</a>"
                "<a href='docs/design.html'>Design</a><a href='docs/bom.html'>BOM</a>"
                "<a href='out/sim/results.html'>Simulation</a><a href='out/drawings/'>Drawings</a>"
                "<a href='out/cad/'>CAD</a><a href='test1-package.zip'>Bundle (zip)</a>")
    nav_docs = nav_root.replace("href='", "href='../").replace("href='../http", "href='http")
    nav_sim = nav_root.replace("href='", "href='../../")
    to_html(os.path.join(HERE, "README.md"), os.path.join(dest, "index.html"), "Test 1", nav_root)
    for name in ("manual", "design", "bom"):
        to_html(os.path.join(HERE, "docs", f"{name}.md"), os.path.join(dest, "docs", f"{name}.html"), name, nav_docs)
    to_html(os.path.join(HERE, "out", "sim", "results.md"), os.path.join(dest, "out", "sim", "results.html"),
            "Simulation", nav_sim)


INCLUDE = ["README.md", "params.py", "gen_config.py", "drawings.py", "build.py", "requirements.txt",
           "docs", "cad", "sim", "firmware", "host", "tests", "out"]
EXCLUDE_DIRS = {"__pycache__", "results", "meshes"}


def bundle():
    dist = os.path.join(REPO, "dist")
    os.makedirs(dist, exist_ok=True)
    zpath = os.path.join(dist, "test1-package.zip")
    stage = os.path.join(dist, "test1_html")
    shutil.rmtree(stage, ignore_errors=True)
    html_docs(stage)
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for item in INCLUDE:
            p = os.path.join(HERE, item)
            if os.path.isfile(p):
                z.write(p, os.path.join("test1", item))
                continue
            for root, dirs, files in os.walk(p):
                dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
                for fn in files:
                    full = os.path.join(root, fn)
                    z.write(full, os.path.join("test1", os.path.relpath(full, HERE)))
        for root, _, files in os.walk(stage):
            for fn in files:
                full = os.path.join(root, fn)
                z.write(full, os.path.join("test1", "html", os.path.relpath(full, stage)))
    print("→ bundle:", zpath, round(os.path.getsize(zpath) / 1e6, 1), "MB")
    # shared web folder: HTML + drawings, CAD, sim images and the zip
    if os.path.isdir(os.path.dirname(os.path.dirname(HOSTED))):
        shutil.rmtree(HOSTED, ignore_errors=True)
        shutil.copytree(stage, HOSTED)
        for sub in ("out/drawings", "out/cad", "out/sim"):
            shutil.copytree(os.path.join(HERE, sub), os.path.join(HOSTED, sub), dirs_exist_ok=True)
        shutil.copy(zpath, HOSTED)
        print("→ web folder:", os.path.abspath(HOSTED))


def main():
    fast = "--fast" in sys.argv
    run("gen_config.py")
    run("cad/export.py")
    run("drawings.py")
    if not fast:
        run("sim/run.py", "--render", env={"MUJOCO_GL": "egl"})
    bom()
    run("tests/test_firmware.py")
    cal = os.path.join(HERE, "out", "cal.json")
    if os.path.exists(cal):
        os.remove(cal)
    if "--bundle" in sys.argv:
        bundle()


if __name__ == "__main__":
    main()
