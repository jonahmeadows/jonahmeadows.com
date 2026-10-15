#!/usr/bin/env python3
"""Fetch the nola.com author RSS feed and regenerate data/latest.json.

Used by .github/workflows/update-articles.yml (scheduled) and can be run
locally:  python3 scripts/fetch_rss.py
"""

import html
import json
import re
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

FEED_URL = ("https://www.nola.com/search/?a=d1e3009c-f2ce-11ef-a083-13bafcd54a62"
            "&s=start_time&sd=desc&f=rss&l=50")
OUT = Path(__file__).resolve().parent.parent / "data" / "latest.json"
MAX_ITEMS = 50

# Full browser-like headers: nola.com rejects requests with only a bare UA.
HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/126.0.0.0 Safari/537.36"),
    "Accept": "application/rss+xml, application/xml;q=0.9, */*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def tag(block: str, name: str) -> str:
    m = re.search(rf"<{name}>(.*?)</{name}>", block, re.S)
    return html.unescape(m.group(1)).strip() if m else ""


def fetch(url: str, tries: int = 3) -> str:
    last = None
    for attempt in range(1, tries + 1):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            last = e
            print(f"attempt {attempt}: HTTP {e.code}", flush=True)
        except Exception as e:  # URLError, timeout, etc.
            last = e
            print(f"attempt {attempt}: {type(e).__name__}: {e}", flush=True)
        if attempt < tries:
            time.sleep(5)
    raise SystemExit(f"failed to fetch feed after {tries} attempts: {last}")


def main() -> int:
    xml = fetch(FEED_URL)

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

    if not items:
        raise SystemExit("feed returned no items; refusing to overwrite latest.json")

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
