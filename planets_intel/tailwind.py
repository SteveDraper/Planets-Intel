"""Compile Tailwind at build time and return the CSS text."""

import hashlib
import platform
import stat
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INPUT_CSS = ROOT / "styles" / "input.css"
BINARY = ROOT / ".tools" / "tailwindcss"
TAILWIND_VERSION = "4.3.3"

TAILWIND_ASSETS = {
    ("darwin", "arm64"): (
        "tailwindcss-macos-arm64",
        "cdf646702987a743464dff4d9c60fd4480d1c1e73dd819a9a67f1078815dce9d",
    ),
    ("darwin", "x86_64"): (
        "tailwindcss-macos-x64",
        "7922e0953f2110c05976e3bf58f14e643d90427575e766b7d433f5f80cbee7e1",
    ),
    ("linux", "aarch64"): (
        "tailwindcss-linux-arm64",
        "55fd0b241214eff3de1e8ee4f22796662f2d2e7a49bcfca7477cfd0bac398195",
    ),
    ("linux", "x86_64"): (
        "tailwindcss-linux-x64",
        "dc61b3ac6b8c9ca874c0cc4c57b2409791a64c5540404ca5f5367360babc313a",
    ),
}


def compile_css() -> str:
    cli = _ensure_cli()
    with tempfile.NamedTemporaryFile(suffix=".css", delete=False) as handle:
        compiled = Path(handle.name)
    result = subprocess.run(
        [str(cli), "-i", str(INPUT_CSS), "-o", str(compiled), "--minify"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        compiled.unlink(missing_ok=True)
        raise SystemExit(result.stderr or "Tailwind compile failed")
    css = compiled.read_text(encoding="utf-8")
    compiled.unlink(missing_ok=True)
    if ".min-h-screen" not in css or ".underline-offset-4" not in css:
        raise SystemExit("Tailwind compile did not include the report utilities.")
    return css


def _asset() -> tuple[str, str]:
    system = platform.system().lower()
    machine = platform.machine().lower()
    if machine == "arm64" and system == "linux":
        machine = "aarch64"
    key = (system, machine)
    if key not in TAILWIND_ASSETS:
        raise SystemExit(f"No Tailwind standalone CLI build for {system}/{machine}.")
    return TAILWIND_ASSETS[key]


def _ensure_cli() -> Path:
    import urllib.request

    name, expected = _asset()
    if BINARY.is_file() and hashlib.sha256(BINARY.read_bytes()).hexdigest() == expected:
        return BINARY
    BINARY.parent.mkdir(parents=True, exist_ok=True)
    url = (
        "https://github.com/tailwindlabs/tailwindcss/releases/download/"
        f"v{TAILWIND_VERSION}/{name}"
    )
    temporary = BINARY.with_suffix(".download")
    urllib.request.urlretrieve(url, temporary)
    digest = hashlib.sha256(temporary.read_bytes()).hexdigest()
    if digest != expected:
        temporary.unlink(missing_ok=True)
        raise SystemExit(f"Tailwind CLI checksum mismatch for {name}.")
    temporary.replace(BINARY)
    BINARY.chmod(BINARY.stat().st_mode | stat.S_IEXEC)
    if platform.system().lower() == "darwin":
        subprocess.run(
            ["xattr", "-d", "com.apple.quarantine", str(BINARY)],
            check=False,
            capture_output=True,
        )
    return BINARY
