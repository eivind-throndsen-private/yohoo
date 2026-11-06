import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "build_safari_extension.py"


def build(out):
    subprocess.run([sys.executable, "-I", str(SCRIPT), str(out)], check=True)


def test_safari_manifest_drops_file_urls_and_keeps_version():
    chrome = json.loads((ROOT / "extension" / "manifest.json").read_text())
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "Resources"
        build(out)
        m = json.loads((out / "manifest.json").read_text())

    assert m["version"] == chrome["version"]
    assert "file:///*" not in m["host_permissions"]
    for cs in m["content_scripts"]:
        assert not any(x.startswith("file:") for x in cs["matches"])
    assert m["content_scripts"][0]["matches"]  # still has the web hosts


def test_shared_scripts_are_copied_verbatim():
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "Resources"
        build(out)
        for name in ("background.js", "content-script.js"):
            assert (out / name).read_bytes() == (ROOT / "extension" / name).read_bytes()
