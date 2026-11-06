# Yohoo Helper for Safari

Safari port of the [Chrome extension](chrome-extension-title-helper.md). It improves titles for links dropped onto Yohoo. The JavaScript is shared with the Chrome version; only the manifest differs.

## What differs from Chrome

- **No local file links.** Safari does not let extensions touch `file://` URLs, so those entries are stripped from the Safari manifest. Clicking a `file://` link in Yohoo falls back to copying the URL.
- **Per-site permissions.** Safari asks you to allow the extension on each website. The open-tab title match (the most useful path for Google Docs and Vend Wiki) only sees tabs on sites you have allowed, so allow `docs.google.com`, your wiki host and the Yohoo host, or choose "Always Allow on Every Website".
- **Needs a signed app.** Safari only loads extensions that ship inside a macOS app, so there is no "load unpacked" equivalent without Xcode.

## Build

Requires full Xcode (Command Line Tools are not enough), then:

```zsh
scripts/build_safari_app.sh
```

This writes the Safari resources to `dist/safari/Resources` and runs `safari-web-extension-converter` to create `dist/safari/Yohoo Helper/Yohoo Helper.xcodeproj`. Open it, choose your team under Signing & Capabilities, and Run.

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

The Safari resources bundle and converter script are tested only for output shape (`tests/test_build_safari_extension.py`). The Xcode app wrapper has not been built or run in Safari yet, because the machine that authored it has no Xcode.
