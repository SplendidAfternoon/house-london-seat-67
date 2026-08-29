"""Push docs/ to SplendidAfternoon.github.io (user GitHub Pages repo)."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
PAGES_REPO = "https://github.com/SplendidAfternoon/SplendidAfternoon.github.io.git"


def run(cmd: list[str], cwd: Path) -> None:
    print("   ", " ".join(cmd))
    subprocess.run(cmd, cwd=cwd, check=True)


def main() -> None:
    if not DOCS.is_dir():
        raise SystemExit(f"missing {DOCS}; run publish_pages.py first")

    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / "pages"
        run(["git", "clone", PAGES_REPO, str(target)], cwd=Path(tmp))
        for item in target.iterdir():
            if item.name == ".git":
                continue
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()
        for item in DOCS.iterdir():
            dest = target / item.name
            if item.is_dir():
                shutil.copytree(item, dest)
            else:
                shutil.copy2(item, dest)
        run(["git", "add", "-A"], cwd=target)
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=target,
            capture_output=True,
            text=True,
            check=True,
        )
        if not status.stdout.strip():
            print("    no changes to publish")
            return
        run(["git", "commit", "-m", "Sync docs from house-london-seat-67"], cwd=target)
        run(["git", "push", "origin", "main"], cwd=target)
        print("    published to https://splendidafternoon.github.io/")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as exc:
        sys.exit(exc.returncode)
