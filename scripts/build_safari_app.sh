#!/usr/bin/env bash
# Build the Safari app wrapper for the Yohoo Helper extension.
# Requires full Xcode (not just Command Line Tools) on macOS.
#
# The Xcode project references dist/safari/Resources in place, so it only needs
# generating once. Re-running refreshes the resources and keeps your project and
# signing settings. Pass --force to regenerate the project from scratch.
set -euo pipefail
cd "$(dirname "$0")/.."

PROJ="dist/safari/Yohoo Helper/Yohoo Helper.xcodeproj"

if ! xcrun --find safari-web-extension-converter >/dev/null 2>&1; then
    echo "safari-web-extension-converter not found. Install Xcode and run:" >&2
    echo "  sudo xcode-select -s /Applications/Xcode.app/Contents/Developer" >&2
    exit 1
fi

python3 -I scripts/build_safari_extension.py dist/safari/Resources

if [ -d "$PROJ" ] && [ "${1:-}" != "--force" ]; then
    echo "Project exists, resources refreshed. Rebuild in Xcode (Cmd+R). Use --force to regenerate."
    exit 0
fi

xcrun safari-web-extension-converter dist/safari/Resources \
    --project-location dist/safari --app-name "Yohoo Helper" \
    --bundle-identifier io.m10s.yohoo.helper --macos-only --no-open --force

# Team ID comes from your Apple Development signing certificate (OU field).
TEAM_ID="$(security find-certificate -c 'Apple Development' -p 2>/dev/null \
    | openssl x509 -noout -subject -nameopt multiline 2>/dev/null \
    | awk '/organizationalUnitName/ {print $3; exit}')"

# The converter names the app io.m10s.yohoo.Yohoo-Helper, which breaks the
# "extension ID must be prefixed by the app ID" rule, and leaves the team empty.
python3 -I - "$PROJ" "$TEAM_ID" <<'EOF'
import re, sys
from pathlib import Path

proj, team = Path(sys.argv[1]), sys.argv[2]
for name in ("project.pbxproj", "project.xcproj"):
    f = proj / name
    if not f.exists():
        continue
    text = f.read_text().replace("io.m10s.yohoo.Yohoo-Helper", "io.m10s.yohoo.helper")
    if team and "DEVELOPMENT_TEAM" not in text:
        text = re.sub(
            r'^(\s*)("PRODUCT_BUNDLE_IDENTIFIER": [^\n]*\n)',
            lambda m: f'{m.group(1)}"DEVELOPMENT_TEAM": "{team}",\n{m.group(1)}{m.group(2)}',
            text, flags=re.M)
        text = re.sub(
            r'^(\s*)(PRODUCT_BUNDLE_IDENTIFIER = [^\n]*\n)',
            lambda m: f'{m.group(1)}DEVELOPMENT_TEAM = {team};\n{m.group(1)}{m.group(2)}',
            text, flags=re.M)
    f.write_text(text)
print(f"Team: {team or 'not found, set it in Xcode'}")
EOF
echo "Open the project, check Signing, and Run:"
echo "  open \"$PROJ\""
