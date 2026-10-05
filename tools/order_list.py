#!/usr/bin/env python3
"""Build a clickable order list (HTML) from docs/order-list.json.

Usage: tools/order_list.py [output dir]
Default: ../../hosted/pneumatic-arm (shared web folder of the workspace).
Product photos are downloaded once and kept in <output dir>/img/.
"""
import html, json, os, re, sys, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "..", "..", "hosted", "pneumatic-arm")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36"


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "nl-NL,nl;q=0.9"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def foto(item_id):
    """Path of the first product photo (relative to OUT), or None."""
    rel = f"img/{item_id}.jpg"
    path = os.path.join(OUT, rel)
    if os.path.exists(path):
        return rel
    try:
        page = get(f"https://nl.aliexpress.com/item/{item_id}.html").decode("utf-8", "ignore")
        m = re.search(r'"imagePathList":\["(https?:[^"]+)"', page)
        if not m:
            return None
        open(path, "wb").write(get(m.group(1) + "_220x220.jpg"))
        return rel
    except Exception as e:
        print("no photo for", item_id, e, file=sys.stderr)
        return None


def euro(x):
    return f"€{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


data = json.load(open(os.path.join(ROOT, "docs", "order-list.json")))
os.makedirs(os.path.join(OUT, "img"), exist_ok=True)
e = html.escape
parts = [f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(data['title'])}</title>
<style>
body{{font-family:system-ui,sans-serif;max-width:1000px;margin:2rem auto;padding:0 1rem;color:#222}}
table{{border-collapse:collapse;width:100%;margin-bottom:.5rem}}
td,th{{border-bottom:1px solid #ddd;padding:.4rem;vertical-align:top;text-align:left}}
img{{width:90px;height:90px;object-fit:cover;border-radius:4px}}
.n{{text-align:right;white-space:nowrap}} .noot{{color:#666;font-size:.9em}}
.s{{color:#a60}} h2{{margin-top:2rem}}
</style></head><body><h1>{e(data['title'])}</h1>"""]
totaal_alles = 0
for b in data["orders"]:
    parts.append(f"<h2>{e(b['name'])}</h2><p>Status: {e(b['status'])}</p>")
    if b.get("note"):
        parts.append(f"<p class='noot'>{e(b['note'])}</p>")
    parts.append("<table><tr><th></th><th>Part</th><th>Choose variant</th><th class='n'>Qty</th><th class='n'>Price</th><th class='n'>Subtotal</th></tr>")
    totaal = 0
    for r in b["items"]:
        sub = r["qty"] * r["price"]
        totaal += sub
        img = foto(r["id"]) if r.get("id") else None
        link = r.get("url") or (f"https://nl.aliexpress.com/item/{r['id']}.html" if r.get("id") else None)
        naam = f"<a href='{link}' target='_blank'>{e(r['what'])}</a>" if link else e(r["what"])
        noot = f"<div class='noot'>{e(r['note'])}</div>" if r.get("note") else ""
        schat = " <span class='s'>(estimate)</span>" if r.get("estimate") else ""
        pic = f"<a href='{link}' target='_blank'><img src='{img}' alt=''></a>" if img else ""
        parts.append(f"<tr><td>{pic}</td><td>{naam}{noot}</td><td>{e(r['variant'])}</td>"
                     f"<td class='n'>{r['qty']}</td><td class='n'>{euro(r['price'])}{schat}</td><td class='n'>{euro(sub)}</td></tr>")
    parts.append(f"<tr><th colspan='5'>Total</th><th class='n'>{euro(totaal)}</th></tr></table>")
    if b.get('status') not in ('postponed', 'alternative'):
        totaal_alles += totaal
parts.append(f"<h2>Total (excluding alternatives): {euro(totaal_alles)}</h2>")
parts.append("<p class='noot'>Prices are the lowest from the search results unless stated otherwise; the real price per variant shows in the cart.</p></body></html>")
open(os.path.join(OUT, "order-list.html"), "w").write("\n".join(parts))
print(os.path.join(OUT, "order-list.html"), euro(totaal_alles))
