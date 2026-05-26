#!/usr/bin/env python3
import hashlib, re, sys, urllib.request
from pathlib import Path

URL = "https://www.sfelectricaltraining.org/"
SNAPSHOT_FILE = Path("snapshot.txt")
HASH_FILE = Path("snapshot.hash")
OPEN_SIGNALS = ["now accepting", "applications will be accepted", "2027 electrical apprenticeship", "apply now", "application period"]
CLOSED_SIGNALS = ["are now closed", "reached our limit"]

def fetch():
    req = urllib.request.Request(URL, headers={"User-Agent": "sfjatc-watcher/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="replace")

def extract_banner(html):
    t = re.sub(r"<script.*?</script>", " ", html, flags=re.DOTALL|re.IGNORECASE)
    t = re.sub(r"<style.*?</style>", " ", t, flags=re.DOTALL|re.IGNORECASE)
    t = re.sub(r"<[^>]+>", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    m = re.search(r"(Electrical Apprenticeship Applications.{0,2000})", t, re.IGNORECASE)
    return m.group(1) if m else t[:2000]

def main():
    try:
        html = fetch()
    except Exception as e:
        print(f"::error::Fetch failed: {e}")
        sys.exit(2)
    banner = extract_banner(html)
    h = hashlib.sha256(banner.encode()).hexdigest()
    prior = HASH_FILE.read_text().strip() if HASH_FILE.exists() else ""
    SNAPSHOT_FILE.write_text(banner)
    HASH_FILE.write_text(h)
    lower = banner.lower()
    open_hits = [s for s in OPEN_SIGNALS if s in lower]
    closed_hits = [s for s in CLOSED_SIGNALS if s in lower]
    print(f"Hash: {h[:12]} / prior: {prior[:12] or '(none)'}")
    print(f"Open signals: {open_hits or 'none'}")
    print(f"Closed signals: {closed_hits or 'none'}")
    print("---")
    print(banner[:800])
    print("---")
    if h != prior and prior:
        print("::notice::PAGE CHANGED")
        if open_hits and not closed_hits:
            print("::warning::Window appears OPEN")
        sys.exit(1)
    print("No change.")
    sys.exit(0)

if __name__ == "__main__":
    main()
