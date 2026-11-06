#!/usr/bin/env bash
# Build the Safari app wrapper for the Yohoo Helper extension.
# Requires full Xcode (not just Command Line Tools) on macOS.
set -euo pipefail
cd "$(dirname "$0")/.."

if ! xcrun --find safari-web-extension-converter >/dev/null 2>&1; then
    echo "safari-web-extension-converter not found. Install Xcode and run:" >&2
    echo "  sudo xcode-select -s /Applications/Xcode.app/Contents/Developer" >&2
    exit 1
fi

python3 -I scripts/build_safari_extension.py dist/safari/Resources
xcrun safari-web-extension-converter dist/safari/Resources \
    --project-location dist/safari --app-name "Yohoo Helper" \
    --bundle-identifier io.m10s.yohoo.helper --macos-only --no-open --force
echo "Open dist/safari/Yohoo\ Helper/Yohoo\ Helper.xcodeproj, pick your team under Signing, and Run."
