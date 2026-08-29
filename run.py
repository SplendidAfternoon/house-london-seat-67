"""Seat 67 — Extend-in-Place: fetch → build → serve.

    python run.py

Stop with Ctrl+C.
"""

import socket
import subprocess
import sys
import webbrowser
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SITE = ROOT / "site"
PACKAGES = ["pandas", "requests"]
STEPS = [
    ("Downloading Foreman CSV (skips if cached)", "fetch_foreman.py"),
    ("Exporting verified takeaways", "export_takeaways.py"),
    ("Classifying and aggregating by borough", "build_site.py"),
    ("Bundling offline single-file demo", "build_standalone.py"),
]


def run_step(script: str) -> None:
    result = subprocess.run([sys.executable, str(ROOT / "scripts" / script)], cwd=ROOT)
    if result.returncode != 0:
        sys.exit(
            f"\nStep failed: {script}\n"
            "If it was a download problem, run again — finished downloads are kept."
        )


def ensure_packages() -> None:
    try:
        import pandas  # noqa: F401
        import requests  # noqa: F401
    except ImportError:
        print("    installing pandas, requests …")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--quiet", *PACKAGES], check=True
        )


def free_port(start: int = 8099) -> int:
    for port in range(start, start + 50):
        with socket.socket() as probe:
            if probe.connect_ex(("127.0.0.1", port)) != 0:
                return port
    sys.exit("No free port found between 8099 and 8148.")


def main() -> None:
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except AttributeError:
        pass

    total = len(STEPS) + 2
    print(f"==> 1/{total}  Checking Python packages")
    ensure_packages()

    for i, (label, script) in enumerate(STEPS, start=2):
        print(f"==> {i}/{total}  {label}")
        run_step(script)

    port = free_port()
    if port != 8099:
        print(f"    Port 8099 was busy, using {port} instead.")

    url = f"http://localhost:{port}"
    print(f"\n==> {total}/{total}  Serving the site\n")
    print(f"    {url}")
    print("    Offline demo: dist/replacement-gap.html")
    print("    Leave this window open. Press Ctrl+C to stop.\n")

    try:
        webbrowser.open(url)
    except Exception:
        pass

    handler = partial(SimpleHTTPRequestHandler, directory=str(SITE))
    with ThreadingHTTPServer(("127.0.0.1", port), handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")


if __name__ == "__main__":
    main()
