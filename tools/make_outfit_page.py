#!/usr/bin/env python3
"""Build "shop the look" pages for outfit pins.

Each outfit lives in outfits/<PIN_ID>/outfit.json:
{
  "pin_id": "pin-20261101-001",
  "title": "Black Crop Top & Gray Wide-Leg Trousers",
  "garments": [
    {"piece": "Top", "description": "Black cropped collared button-front shirt",
     "product": "SweatyRocks Crop Button Up Shirt, Black",
     "link": "https://link.amazon/B0aFGf5lu"}
  ]
}

Usage:
  python3 tools/make_outfit_page.py pin-20261101-001   # one page
  python3 tools/make_outfit_page.py --all              # every outfit
Writes outfits/<PIN_ID>/index.html, served at
https://anusha-skaties.github.io/pinterest-pins/outfits/<PIN_ID>/
"""
import html, json, re, struct, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LINK_RE = re.compile(r"^https://(link\.amazon|amzn\.to)/[A-Za-z0-9]+$")

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} | Shop the Look</title>
<meta name="description" content="Shop every piece of this character-inspired outfit.">
<meta property="og:title" content="{title}">
<meta property="og:image" content="{image}">
<meta name="robots" content="noindex">
<link rel="stylesheet" href="../../assets/outfit.css">
</head>
<body>
<main>
  <p class="eyebrow">guess the series this outfit is from</p>
  <h1>{title}</h1>
  <img class="pin" src="{image}" alt="Outfit breakdown: {alt}" width="{w}" height="{h}">
  <h2>Shop the look</h2>
  <ol class="pieces">
{items}
  </ol>
  <p class="disclosure">As an Amazon Associate I earn from qualifying purchases. Products are close matches, not the exact on-screen pieces.</p>
</main>
</body>
</html>
"""

ITEM = """    <li>
      <div class="piece">
        <span class="label">{piece}</span>
        <span class="desc">{description}</span>
        <span class="product">{product}</span>
      </div>
      <a class="shop" href="{link}" target="_blank" rel="sponsored nofollow noopener">Shop on Amazon</a>
    </li>"""


def png_size(path):
    with open(path, "rb") as f:
        head = f.read(24)
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        raise SystemExit(f"{path.name} is not a PNG")
    return struct.unpack(">II", head[16:24])


def build(pin_id):
    folder = ROOT / "outfits" / pin_id
    data = json.loads((folder / "outfit.json").read_text(encoding="utf-8"))
    if data.get("pin_id") != pin_id:
        raise SystemExit(f"{pin_id}: pin_id in outfit.json does not match folder")
    png = ROOT / "pins" / f"{pin_id}.png"
    if not png.exists():
        raise SystemExit(f"{pin_id}: pins/{pin_id}.png is missing")
    w, h = png_size(png)
    garments = data.get("garments") or []
    if not garments:
        raise SystemExit(f"{pin_id}: no garments")
    items = []
    for g in garments:
        if not LINK_RE.match(g.get("link", "")):
            raise SystemExit(f"{pin_id}: not an Amazon short link: {g.get('link')!r}")
        items.append(ITEM.format(**{k: html.escape(g.get(k, ""), quote=True)
                                    for k in ("piece", "description", "product", "link")}))
    title = html.escape(data["title"], quote=True)
    page = PAGE.format(
        title=title,
        alt=html.escape(", ".join(g["description"] for g in garments), quote=True),
        image=f"../../pins/{pin_id}.png", w=w, h=h,
        items="\n".join(items),
    )
    (folder / "index.html").write_text(page, encoding="utf-8")
    print(f"built outfits/{pin_id}/index.html ({len(garments)} pieces)")


if __name__ == "__main__":
    args = sys.argv[1:]
    if args == ["--all"]:
        args = sorted(p.parent.name for p in (ROOT / "outfits").glob("*/outfit.json"))
    if not args:
        raise SystemExit(__doc__)
    for pid in args:
        build(pid)
