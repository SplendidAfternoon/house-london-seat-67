"""Copy dist/ demo files into docs/ for GitHub Pages."""

from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
DIST = ROOT / "dist"
ARTIFACTS = ("presentation.html", "tear-down-applications.html")

INDEX_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Seat 67 — Tear-Down Applications</title>
  <style>
    body { margin: 0; min-height: 100vh; display: grid; place-items: center;
      background: #0f1210; color: #f4efe4; font-family: "Segoe UI", system-ui, sans-serif; }
    main { max-width: 28rem; padding: 2rem; }
    h1 { font-family: Georgia, serif; font-size: 1.75rem; font-weight: 600; margin: 0 0 0.5rem; }
    p { color: #b7b0a1; line-height: 1.5; margin: 0 0 1.5rem; }
    a { display: block; color: #8ecae6; text-decoration: none; padding: 0.75rem 0;
      border-bottom: 1px solid #2a2f2b; }
    a:hover { color: #f4efe4; }
  </style>
</head>
<body>
  <main>
    <h1>Tear-Down Applications</h1>
    <p>Seat 67 · House London #1</p>
    <a href="presentation.html">Presentation (arrow keys)</a>
    <a href="tear-down-applications.html">Interactive map</a>
  </main>
</body>
</html>
"""


def main() -> None:
    DOCS.mkdir(parents=True, exist_ok=True)
    for name in ARTIFACTS:
        src = DIST / name
        if not src.exists():
            raise SystemExit(f"missing {src}; run build_standalone.py first")
        dst = DOCS / name
        shutil.copy2(src, dst)
        print(f"    copied {name} ({dst.stat().st_size // 1024} KB)")
    (DOCS / "index.html").write_text(INDEX_HTML, encoding="utf-8")
    (DOCS / ".nojekyll").touch()
    print(f"    wrote {DOCS / 'index.html'}")


if __name__ == "__main__":
    main()
