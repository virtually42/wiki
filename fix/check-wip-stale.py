#!/usr/bin/env python3
"""Surface stale wip.md files. Default threshold: 7 days.

Note: this is a long-lived lint script, not a one-shot fix. Move to tools/
once you're happy with it.

Usage:
  python3 check-wip-stale.py            # report to stdout
  python3 check-wip-stale.py --days 14  # custom threshold
"""
import argparse
import re
from datetime import date
from pathlib import Path

ROOT = Path("/p/wiki")


def parse_updated(p: Path) -> date | None:
    text = p.read_text()
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    fm = text[3:end]
    m = re.search(r"^updated:\s*(\d{4}-\d{2}-\d{2})", fm, re.M)
    if not m:
        return None
    y, mo, d = map(int, m.group(1).split("-"))
    return date(y, mo, d)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=7)
    args = ap.parse_args()

    today = date.today()
    candidates = [ROOT / "wip.md"] + list(ROOT.glob("projects/*/wip.md"))
    stale = []
    for p in candidates:
        if not p.exists():
            continue
        upd = parse_updated(p)
        if upd is None:
            print(f"WARN  {p.relative_to(ROOT)}: missing or unparseable 'updated' field")
            continue
        age = (today - upd).days
        if age > args.days:
            stale.append((p.relative_to(ROOT), upd, age))

    if not stale:
        print(f"OK    no wip files older than {args.days} days")
        return 0
    print(f"STALE wip files (threshold {args.days}d):")
    for path, upd, age in stale:
        print(f"  {path}  updated={upd}  age={age}d")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
