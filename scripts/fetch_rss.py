#!/usr/bin/env python3
"""Fetch the nola.com author RSS feed and regenerate data/latest.json.

Used by .github/workflows/update-articles.yml (scheduled) and can be run
locally:  python3 scripts/fetch_rss.py
"""

import html
import json
import re
import sys
import urllib.request
from pathlib import Path

FEED_URL = ("https://www.nola.com/search/?a=d1e3009c-f2ce-11ef-a083-13bafcd54a62"
            "&s=start_time&sd=desc&f=rss&l=30")
OUT = Path(__file__).resolve().parent.parent / "data" / "latest.json"
MAX_ITEMS = 30


def tag(block: str, name: str) -> str:
    m = re.search(rf"<{name}>(.*?)</{name}>", block, re.S)
    return html.unescape(m.group(1)).strip() if m else ""


def main() -> int:
    req = urllib.request.Request(FEED_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        xml = resp.read().decode("utf-8", errors="replace")

    items = []
    for block in re.findall(r"<item>(.*?)</item>", xml, re.S)[:MAX_ITEMS]:
        img = re.search(r'<enclosure url="([^"]+)"', block)
        items.append({
            "title": tag(block, "title"),
            "link": tag(block, "link"),
            "pubDate": tag(block, "pubDate"),
            "creator": tag(block, "dc:creator"),
            "description": tag(block, "description"),
            "image": (img.group(1).replace("http://", "https://") if img else ""),
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    old = OUT.read_text() if OUT.exists() else ""
    new = json.dumps(items, indent=2) + "\n"
    if new != old:
        OUT.write_text(new)
        print(f"updated {OUT} ({len(items)} items)")
    else:
        print("no changes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
