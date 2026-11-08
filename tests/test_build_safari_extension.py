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


GITHUB_HOST = "eivind-throndsen-private.github.io"


def test_github_pages_host_is_trusted_everywhere():
    chrome = json.loads((ROOT / "extension" / "manifest.json").read_text())
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "Resources"
        build(out)
        safari = json.loads((out / "manifest.json").read_text())
    for m in (chrome, safari):
        assert f"https://{GITHUB_HOST}/yohoo/*" in m["content_scripts"][0]["matches"]
    for name in ("content-script.js", "background.js"):
        assert GITHUB_HOST in (ROOT / "extension" / name).read_text()
    assert f"https://{GITHUB_HOST}" in (ROOT / "proxy_server.py").read_text()
