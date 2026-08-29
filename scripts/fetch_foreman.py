"""Download Foreman Foundations CSV to data/raw/foundations.csv."""

from __future__ import annotations

import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = RAW / "foundations.csv"
CSV_URL = "https://foreman.house-london.uk/download/csv/"


def fetch_all(refresh: bool = False) -> Path:
    RAW.mkdir(parents=True, exist_ok=True)
    if OUT.exists() and not refresh:
        size_mb = OUT.stat().st_size / (1024 * 1024)
        print(f"    using cached {OUT.name} ({size_mb:.1f} MB)")
        return OUT

    print("    downloading Foreman CSV (~115 MB) …")
    session = requests.Session()
    session.headers["User-Agent"] = "house-london-seat-67/1.0 (hackathon)"
    with session.get(CSV_URL, stream=True, timeout=300) as resp:
        resp.raise_for_status()
        tmp = OUT.with_suffix(".csv.part")
        downloaded = 0
        with tmp.open("wb") as fh:
            for chunk in resp.iter_content(chunk_size=1024 * 256):
                if not chunk:
                    continue
                fh.write(chunk)
                downloaded += len(chunk)
                if downloaded % (10 * 1024 * 1024) < 1024 * 256:
                    print(f"    {downloaded / (1024 * 1024):.0f} MB")
        tmp.replace(OUT)

    print(f"    wrote {OUT.stat().st_size / (1024 * 1024):.1f} MB -> {OUT}")
    return OUT


if __name__ == "__main__":
    fetch_all(refresh="--refresh" in sys.argv)
