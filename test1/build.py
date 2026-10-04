"""Genereer alles voor test 1 uit params.py en maak de bundel.

    python build.py            # alles opnieuw genereren
    python build.py --bundel   # plus zip in dist/ en kopie naar de gedeelde webmap
    python build.py --snel     # zonder simulatie (alleen CAD, config, tekeningen, docs)

Stappen: firmware/config.py, CAD-export, tekeningen, simulatie (+ renders),
stuklijst, HTML-versie van de documentatie, firmwaretest, bundel.
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


def stuklijst():
    """docs/stuklijst.md en .csv uit de bestellijst van het project."""
    d = json.load(open(os.path.join(REPO, "docs", "bestellijst.json")))
    rows = []
    for b in d["bestellingen"]:
        if b.get("status") == "alternatief":
            continue
        for r in b["regels"]:
            link = r.get("url") or (f"https://nl.aliexpress.com/item/{r['id']}.html" if r.get("id") else "")
            rows.append(dict(bestelling=b["naam"], onderdeel=r["wat"], variant=r.get("variant", ""),
                             aantal=r["aantal"], prijs=r["prijs"], schatting=bool(r.get("schatting")),
                             link=link, opmerking=r.get("noot", ""), status=b.get("status", "")))
    with open(os.path.join(HERE, "docs", "stuklijst.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    lines = ["# Stuklijst test 1", "",
             "Gegenereerd uit `docs/bestellijst.json` (hoofdmap) door `build.py`. Prijzen in euro, "
             "* = schatting. Ook als [CSV](stuklijst.csv).", ""]
    total = 0.0
    current = None
    for r in rows:
        if r["bestelling"] != current:
            current = r["bestelling"]
            lines += ["", f"## {current}", "", f"Status: {r['status']}", "",
                      "| # | Onderdeel | Variant | Prijs | Link |", "|---|---|---|---|---|"]
        sub = r["aantal"] * r["prijs"]
        total += sub
        link = f"[link]({r['link']})" if r["link"] else ""
        note = f" — {r['opmerking']}" if r["opmerking"] else ""
        lines.append(f"| {r['aantal']} | {r['onderdeel']}{note} | {r['variant']} | "
                     f"€{sub:.2f}{'*' if r['schatting'] else ''} | {link} |")
    lines += ["", f"**Totaal ca. €{total:.0f}** (exclusief verzending en invoerheffing).", "",
              "## Gereedschap", ""] + [f"- {g}" for g in d.get("gereedschap", [])]
    with open(os.path.join(HERE, "docs", "stuklijst.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("→ stuklijst:", len(rows), "regels, totaal", round(total))


CSS = """body{font-family:system-ui,sans-serif;max-width:980px;margin:2rem auto;padding:0 1rem;line-height:1.5;color:#222}
table{border-collapse:collapse;margin:1rem 0}td,th{border:1px solid #ccc;padding:.3rem .5rem;vertical-align:top}
th{background:#f3f3f3}img{max-width:100%}code,pre{background:#f5f5f5}pre{padding:.6rem;overflow:auto}
nav a{margin-right:1rem}"""


def to_html(md_path, out_path, title, nav):
    import markdown
    text = open(md_path, encoding="utf-8").read()
    # Python-Markdown wil een lege regel vóór een opsomming en 4 spaties inspringing voor
    # geneste lijsten; GitHub niet. Zet de tekst daarom om.
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
    page = (f"<!doctype html><html lang='nl'><head><meta charset='utf-8'><title>{html.escape(title)}</title>"
            f"<style>{CSS}</style></head><body><nav>{nav}</nav>{body}</body></html>")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(page)


def html_docs(dest):
    """HTML-versie van README, handleiding, ontwerp, stuklijst en simulatieresultaten in `dest`."""
    os.makedirs(os.path.join(dest, "docs"), exist_ok=True)
    os.makedirs(os.path.join(dest, "out", "sim"), exist_ok=True)
    nav_root = ("<a href='index.html'>Test 1</a><a href='docs/handleiding.html'>Handleiding</a>"
                "<a href='docs/ontwerp.html'>Ontwerp</a><a href='docs/stuklijst.html'>Stuklijst</a>"
                "<a href='out/sim/resultaten.html'>Simulatie</a><a href='out/tekeningen/'>Tekeningen</a>"
                "<a href='out/cad/'>CAD</a><a href='test1-pakket.zip'>Bundel (zip)</a>")
    nav_docs = nav_root.replace("href='", "href='../").replace("href='../http", "href='http")
    nav_sim = nav_root.replace("href='", "href='../../")
    to_html(os.path.join(HERE, "README.md"), os.path.join(dest, "index.html"), "Test 1", nav_root)
    for name in ("handleiding", "ontwerp", "stuklijst"):
        to_html(os.path.join(HERE, "docs", f"{name}.md"), os.path.join(dest, "docs", f"{name}.html"), name, nav_docs)
    to_html(os.path.join(HERE, "out", "sim", "resultaten.md"), os.path.join(dest, "out", "sim", "resultaten.html"),
            "Simulatie", nav_sim)


INCLUDE = ["README.md", "params.py", "gen_config.py", "tekeningen.py", "build.py", "requirements.txt",
           "docs", "cad", "sim", "firmware", "host", "tests", "out"]
EXCLUDE_DIRS = {"__pycache__", "resultaten", "meshes"}


def bundel():
    dist = os.path.join(REPO, "dist")
    os.makedirs(dist, exist_ok=True)
    zpath = os.path.join(dist, "test1-pakket.zip")
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
    print("→ bundel:", zpath, round(os.path.getsize(zpath) / 1e6, 1), "MB")
    # gedeelde webmap: HTML + tekeningen, CAD, sim-beelden en de zip
    if os.path.isdir(os.path.dirname(os.path.dirname(HOSTED))):
        shutil.rmtree(HOSTED, ignore_errors=True)
        shutil.copytree(stage, HOSTED)
        for sub in ("out/tekeningen", "out/cad", "out/sim"):
            shutil.copytree(os.path.join(HERE, sub), os.path.join(HOSTED, sub), dirs_exist_ok=True)
        shutil.copy(zpath, HOSTED)
        print("→ webmap:", os.path.abspath(HOSTED))


def main():
    fast = "--snel" in sys.argv
    run("gen_config.py")
    run("cad/export.py")
    run("tekeningen.py")
    if not fast:
        run("sim/run.py", "--render", env={"MUJOCO_GL": "egl"})
    stuklijst()
    run("tests/test_firmware.py")
    cal = os.path.join(HERE, "out", "cal.json")
    if os.path.exists(cal):
        os.remove(cal)
    if "--bundel" in sys.argv:
        bundel()


if __name__ == "__main__":
    main()
