#!/usr/bin/env python3
"""Build the Safari extension resources from the Chrome extension sources.

background.js and content-script.js are shared verbatim. Only the manifest
differs: Safari cannot grant extensions access to file:// URLs, so those
entries are removed.

Usage: build_safari_extension.py [output_dir]   (default: dist/safari/Resources)
"""
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "extension"
SHARED = ("background.js", "content-script.js")


def safari_manifest(manifest):
    m = json.loads(json.dumps(manifest))
    m["host_permissions"] = [p for p in m.get("host_permissions", []) if not p.startswith("file:")]
    for cs in m.get("content_scripts", []):
        cs["matches"] = [x for x in cs["matches"] if not x.startswith("file:")]
    return m


def main(out):
    out.mkdir(parents=True, exist_ok=True)
    for name in SHARED:
        shutil.copyfile(SRC / name, out / name)
    manifest = json.loads((SRC / "manifest.json").read_text())
    (out / "manifest.json").write_text(json.dumps(safari_manifest(manifest), indent=4) + "\n")
    print(f"Safari resources written to {out}")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "dist" / "safari" / "Resources")
