# Yohoo Dropped-Link Title Fetching Design

Date: 2026-04-28

## Problem

Dragging a URL onto `yohoo.html` can provide a URL and sometimes a title through the browser drag payload. When the payload does not contain a useful title, the page cannot reliably fetch and parse the target page itself. Browser `fetch()` and `XMLHttpRequest` are constrained by same-origin/CORS rules, and most arbitrary web pages do not opt in to being fetched by a local `file://` start page.

The design goal is therefore not to bypass browser security from the page. It is to add optional title providers that are silent when unavailable:

1. Keep the current drag/drop behavior as the baseline.
2. Use drag payload title data when present.
3. Try an optional installed helper with a short timeout.
4. Fall back to the URL/domain without alerts or visible errors.

Important UX rule: title enrichment must never block link creation. Dropping a link should always create something immediately.

## Evaluation Criteria

- Usability: links should appear immediately, with titles improved automatically where possible.
- Transparency: technical helpers should be explainable and inspectable, especially if they can fetch arbitrary URLs.
- Easy installation: non-technical users should not need Python, terminal commands, or extension developer mode.
- Minimum noise: no alerts, badges, popups, browser prompts, or log spam during ordinary drag/drop.
- Graceful failure: users without the helper should see the exact current behavior.

## Experiment Summary

Three isolated worktrees were created from `HEAD` so the main checkout behavior remains unchanged.

- Local proxy helper: `/tmp/yohoo-title-proxy`, branch `title-proxy-experiment`.
- Browser extension bridge: `/tmp/yohoo-title-extension`, branch `title-extension-experiment`.
- Export/enrich/import script: `/tmp/yohoo-title-import`, branch `title-import-experiment`.

Validation performed:

- Proxy experiment: `python3 -m py_compile proxy_server.py`.
- Extension experiment: `python3 -m json.tool extension/manifest.json`, `node --check extension/background.js`, `node --check extension/content-script.js`.
- Import experiment: `python3 -m py_compile scripts/enrich_yohoo_titles.py`, plus a local `file://` HTML fixture that updated one exported link title correctly.

## Approach 1: Optional Local Title Helper

### Concept

Run a small localhost service, probably evolved from the existing `proxy_server.py`, bound only to `127.0.0.1`. After an external drop, Yohoo creates the link immediately using the current title fallback, then silently calls:

```text
GET http://127.0.0.1:3001/fetch-title?url=<encoded_url>
```

If the helper responds quickly with `{ "title": "..." }`, Yohoo updates that link title in `localStorage` and re-renders. If the helper is missing, slow, or returns an error, Yohoo does nothing visible.

### Installation Model

For personal/technical setup:

- `make -C archive install` or a root-level equivalent installs dependencies.
- A macOS `.command` or LaunchAgent starts the helper.
- Optional packaging can turn it into a background app later.

For other users:

- No installation required.
- The page silently times out and behaves as it does today.
- No settings panel is required unless we want an explicit "Title helper: available/unavailable" diagnostics row.

### Implementation Notes

- Add a title provider function to `yohoo.html` that tries `127.0.0.1` first, then `localhost`, with a short timeout around 1-2 seconds.
- Only fetch `http://`, `https://`, and optionally `file://`.
- Keep `createLink()` synchronous from a user perspective, but return the created link object/id so async enrichment can update the correct link.
- Do not alert when the helper is missing. At most write a debug log if debug mode already exists.
- Harden the server before shipping:
  - Bind only to `127.0.0.1`.
  - Reject private-network HTTP targets unless explicitly needed, to avoid local SSRF surprises.
  - Use request timeout, response size cap, redirect cap, and allowed schemes.
  - Avoid full URL logging by default, or make it opt-in debug logging.

### Pros

- Best fit for the user's stated tolerance: technical complexity can be local and invisible to others.
- Works with `file://` Yohoo without extension file-access toggles.
- Can support local files as well as web URLs.
- No browser extension permission warnings.
- Easy to feature-detect from the page.

### Cons

- Requires a running local process for enriched titles.
- Requires installation/packaging work to become truly one-click.
- Localhost services need security discipline even when bound to loopback.
- Corporate/security tooling may dislike unknown local servers.

### Experiment Result

The proxy worktree patches `yohoo.html` to create links immediately and call `enrichLinkTitleSilently()` afterward. Missing helper behavior is silent by construction because failed `fetch()` calls only resolve to no title. The existing `proxy_server.py` compiles, so the experiment validates integration shape but not full browser drag/drop behavior.

### Recommendation

This is the preferred primary path. It maximizes title quality and minimizes noise for everyone else.

## Approach 2: Browser Extension Bridge

### Concept

Install a small Manifest V3 extension. A content script runs on the Yohoo page and listens for a custom browser event:

```text
yohoo:title-request
```

The content script forwards the request to the extension background service worker. The service worker fetches the target page using extension host permissions, extracts a title, and sends a response back through:

```text
yohoo:title-response
```

If the extension is not installed or not allowed on the Yohoo page, no one hears the event. Yohoo times out silently and keeps the fallback title.

### Installation Model

For personal/technical setup:

- Load an unpacked extension in developer mode.
- Grant access to `file://` URLs if Yohoo is opened directly from disk.
- Grant host access for target pages.

For distribution:

- Package through browser extension stores or provide browser-specific instructions.
- Consider optional host permissions to reduce install warnings, but that may introduce permission prompts during use.

### Implementation Notes

- The Yohoo page should not call `chrome.runtime` directly. A page-level custom event bridge keeps the page browser-agnostic and silent when the extension is absent.
- The extension needs a content script match for the Yohoo origin:
  - `file:///*` for direct local use, with manual file access enabled.
  - `http://localhost/*` if Yohoo is served locally.
  - A specific deployed origin if Yohoo moves to a hosted URL.
- The service worker should cap HTML bytes and timeout requests.
- A broad `http://*/*` and `https://*/*` host permission gives best utility but creates visible install warnings. Optional host permissions reduce install-time noise but can add runtime noise.

### Pros

- Real-time title updates without a local server.
- Clean failure mode: if absent, the page receives no response.
- Extension background context is the right browser-sanctioned place for privileged fetches.
- Could eventually add browser action diagnostics without changing the Yohoo UI.

### Cons

- Extension install and permission warnings are user-visible.
- `file://` access requires an extra manual toggle in Chrome.
- Packaging and maintenance become browser-specific.
- Some target sites will still block or degrade automated fetches.
- Broad host permissions may be hard to justify for non-technical users.

### Experiment Result

The extension worktree contains `extension/manifest.json`, `background.js`, `content-script.js`, and a Yohoo event bridge prototype. JSON and JS syntax checks pass. The experiment validates the low-noise integration pattern but needs browser manual testing for actual extension permission behavior.

### Recommendation

Good secondary option if a real extension is acceptable. It is less attractive than the local helper for "minimum noise" because browser permission UI is inherently visible.

## Approach 3: Export, Batch Enrich, Import

### Concept

Use the existing Yohoo export/import system. The user exports the current data JSON, runs a local script that fetches titles in batch, then imports the enriched JSON back into Yohoo.

This does not fix titles at drag time. It is a repair/maintenance path for links already added with poor titles.

### Installation Model

For personal/technical setup:

- A dependency-free Python script can run with system Python.
- A macOS `.command` wrapper can open a file picker when no input path is provided.

For other users:

- No effect unless they deliberately use it.
- No background process, extension, or browser permission.

### Implementation Notes

- Keep the script dependency-free if possible.
- Read Yohoo export JSON and only update links whose title is empty, equal to the URL, equal to normalized URL, or equal to hostname.
- Provide `--all` for deliberate full refresh.
- Output a new `*-titles.json` file rather than mutating the source export.
- Preserve Yohoo's import safety behavior: importing already creates a backup.

### Pros

- Most transparent and inspectable path.
- No browser security workaround at runtime.
- No local server, no extension permissions, no background process.
- Can batch-fix many existing links at once.
- Easy to test with local `file://` fixtures.

### Cons

- Not automatic at drag/drop time.
- Requires export/import steps and therefore has more workflow friction.
- Import replaces current Yohoo state, so stale exports can overwrite newer edits if the user is careless.
- Less useful for non-technical users unless wrapped very carefully.

### Experiment Result

The import worktree adds `scripts/enrich_yohoo_titles.py` and `Enrich Yohoo Titles.command`. The script compiles and successfully updates a local fixture export from a `file://` HTML page title.

### Recommendation

Useful fallback and maintenance tool. It should not be the primary UX for dropped links.

## Proposed Final Architecture

Implement a title provider chain in `yohoo.html`:

1. Extract title from drag payload HTML/text when available.
2. Create or update the link immediately.
3. Try optional providers asynchronously:
   - Primary candidate: local title helper.
   - Optional later candidate: extension bridge.
4. If a provider returns a better title, update the link silently.
5. If every provider fails, keep the current fallback title.

The provider chain should be deliberately quiet:

- Timeout each provider quickly.
- Never show alerts for missing helpers.
- Never block link creation.
- Only expose helper state in an explicit diagnostics/settings area, not in normal use.

## Decision

Recommended next implementation:

1. Ship the local helper integration first, feature-detected and silent.
2. Add a one-click macOS launcher/installer for the helper.
3. Keep export/enrich/import as a documented maintenance tool.
4. Defer extension packaging unless there is a specific need to avoid a local server.

This balances the requirements best: strong usability for the technical owner, invisible no-op behavior for everyone else, and no new browser permission noise for ordinary users.

