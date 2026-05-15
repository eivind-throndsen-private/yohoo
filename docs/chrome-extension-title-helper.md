# Yohoo Chrome Extension Helper

Primary environment: Google Chrome on macOS.

## What It Does

The extension improves titles for links dropped onto Yohoo and can open trusted local `file://` links from Yohoo.

When Yohoo asks for a title, the extension tries:

1. An already-open Chrome tab with the same URL.
2. Extension-side `fetch()` with Chrome host permissions.
3. The local Yohoo helper at `127.0.0.1:3001`, if it is running.

The open-tab path is the most important one for private pages such as Google Docs or Vend Wiki. If the page is already open and Chrome knows its tab title, the extension can return that title without asking Python to use browser cookies.

If the extension is not installed, disabled, or cannot resolve a title, Yohoo silently keeps the existing fallback title. If local file opening is unavailable, Yohoo copies the file URL and asks you to paste it into the browser address bar.

## Install In Chrome

1. Open Chrome.
2. Go to `chrome://extensions`.
3. Enable `Developer mode` in the top-right corner.
4. Click `Load unpacked`.
5. Select this folder:

```text
/Users/eivind.throndsen@m10s.io/1-Projects/yohoo/extension
```

6. Confirm that `Yohoo Helper` is enabled.
7. Refresh Yohoo:

```text
https://eivind-throndsen-private.github.io/yohoo/yohoo.html
```

For local file links, open the extension details page and enable `Allow access to file URLs`. Chrome requires this manual toggle before extensions can interact with `file://` URLs.

## Use

1. Open the page you want to add in Chrome.
2. Drag the URL onto Yohoo.
3. The link appears immediately.
4. If the extension or local helper finds a better title, Yohoo updates the title silently.

For private Google Docs or Vend Wiki pages, keep the source page open in Chrome when you drag it. The extension can then match the dropped URL to the open tab and use Chrome's tab title.

For local files, click a `file://` Yohoo link. If Chrome has granted the extension file URL access, the helper opens the file in a new tab. If not, Yohoo copies the file URL as a fallback.

## Permissions

The extension requests:

- `tabs`: needed to read open tab URLs and titles so private/authenticated pages can be matched without scraping cookies.
- `http://*/*` and `https://*/*`: needed for extension-side title fetching when no matching open tab is found.
- `file:///*`: needed for opening local file links from Yohoo, and only works after Chrome's manual `Allow access to file URLs` toggle is enabled.

This is intentionally broad because Yohoo can accept links from any site. The extension does not send data to any third-party service. It only responds to title requests from Yohoo pages matched in `extension/manifest.json`.

## Local Helper Pairing

The extension works without the local helper, but they complement each other:

- Extension: better for private/authenticated browser pages, especially if the page is open in Chrome.
- Local helper: better for public server-side fetches, local automation, and future API-based providers.

Check local helper health:

```zsh
curl http://127.0.0.1:3001/health
```

Restart/reinstall the local helper:

```zsh
scripts/install_title_helper.sh
```

## Troubleshooting

- Refresh Yohoo after installing or updating the extension.
- In `chrome://extensions`, click `Details` for `Yohoo Helper` and verify it is enabled.
- If local files copy instead of opening, verify `Allow access to file URLs` is enabled and refresh Yohoo.
- To inspect extension logs, click the extension's `service worker` link on `chrome://extensions`.
- If Google Docs or Vend Wiki titles do not improve, make sure the source page is open in Chrome before dragging.
- If only public sites work, the private page may not have an open tab match and may block extension-side fetches.

## Update After Code Changes

Chrome does not automatically reload unpacked extension code.

1. Go to `chrome://extensions`.
2. Click the reload icon on `Yohoo Helper`.
3. Refresh Yohoo.
