# Yohoo Helper for Safari

Safari port of the [Chrome extension](chrome-extension-title-helper.md). It improves titles for links dropped onto Yohoo. The JavaScript is shared with the Chrome version; only the manifest differs.

## What differs from Chrome

- **No local file links.** Safari does not let extensions touch `file://` URLs, so those entries are stripped from the Safari manifest. Clicking a `file://` link in Yohoo falls back to copying the URL.
- **Per-site permissions.** Safari asks you to allow the extension on each website. The open-tab title match (the most useful path for Google Docs and Vend Wiki) only sees tabs on sites you have allowed, so allow `docs.google.com`, your wiki host and the Yohoo host, or choose "Always Allow on Every Website".
- **Needs a signed app.** Safari only loads extensions that ship inside a macOS app, so there is no "load unpacked" equivalent without Xcode.

## Build

Requires full Xcode (Command Line Tools are not enough). One-time setup after installing Xcode:

```zsh
sudo xcode-select -s /Applications/Xcode.app/Contents/Developer
sudo xcodebuild -license accept
sudo xcodebuild -runFirstLaunch
```

You also need an Apple ID added in Xcode > Settings > Accounts (a free personal team works), so an Apple Development signing certificate exists.

```zsh
scripts/build_safari_app.sh
```

First run: writes the Safari resources to `dist/safari/Resources`, runs `safari-web-extension-converter`, forces the app bundle ID to `io.m10s.yohoo.helper` (the converter picks a name that breaks Apple's prefix rule) and fills in your team ID from your signing certificate. Then open `dist/safari/Yohoo Helper/Yohoo Helper.xcodeproj` and press Run, or build from the command line:

```zsh
cd "dist/safari/Yohoo Helper"
xcodebuild -project "Yohoo Helper.xcodeproj" -scheme "Yohoo Helper" -derivedDataPath build -allowProvisioningUpdates build
open "build/Build/Products/Debug/Yohoo Helper.app"
```

Later runs only refresh the resources and keep the project and signing. Pass `--force` to regenerate the project. A build signed with a personal team only runs on the Mac that built it.

To get only the resources (no Xcode needed):

```zsh
python3 scripts/build_safari_extension.py
```

## Enable

1. Safari > Settings > Extensions, tick `Yohoo Helper`.
2. Click `Edit Websites` and allow the Yohoo host plus any sites you drag links from.
3. If the app is unsigned or a dev build: Safari > Settings > Developer (or the Develop menu) > `Allow Unsigned Extensions`. This resets every time Safari quits.
4. Reload Yohoo.

## Keep in sync

Change code in `extension/`, then rebuild. Host allowlists live in `extension/manifest.json`, `content-script.js` and `background.js`, exactly as for Chrome, so the Safari build picks up changes automatically.

## Troubleshooting

- Titles fall back to the raw URL: check that the extension has access to the Yohoo host and the source site.
- Local helper at `127.0.0.1:3001` still works as a fallback, but Safari may ask for permission to reach it.
- Logs: Develop > Web Extension Background Content > Yohoo Helper.

## Status

Verified: the resources bundle (`tests/test_build_safari_extension.py`), project generation, and a signed Debug build with Xcode 27.2 on macOS. Not yet verified: title fetching inside Safari.
