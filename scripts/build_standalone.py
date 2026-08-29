"""Bundle site/ into dist/replacement-gap.html for offline demo."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
DIST = ROOT / "dist"
OUT = DIST / "replacement-gap.html"


def main() -> None:
    html = (SITE / "index.html").read_text(encoding="utf-8")
    css = (SITE / "style.css").read_text(encoding="utf-8")
    data = (SITE / "data.json").read_text(encoding="utf-8")

    html = html.replace(
        '<link rel="stylesheet" href="style.css" />',
        f"<style>\n{css}\n</style>",
    )
    html = html.replace(
        '<script src="app.js"></script>',
        f"<script>window.EMBEDDED_DATA = {data};</script>\n<script src=\"app.js\"></script>",
    )

    app_js = (SITE / "app.js").read_text(encoding="utf-8")
    html = html.replace('<script src="app.js"></script>', f"<script>\n{app_js}\n</script>")

    DIST.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    print(f"    wrote {OUT} ({OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
