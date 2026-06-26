# Yohoo Local Title Helper

The local title helper is an optional localhost server used by `yohoo.html` when a dropped link does not include a useful title. Yohoo creates the link immediately, then silently asks the helper for a better title. If the helper is unavailable, slow, blocked, or unable to fetch a title, the page keeps the original fallback title.

## Files

- `proxy_server.py`: Flask server that fetches a page and extracts `<title>`, `og:title`, or `twitter:title`.
- `requirements-title-helper.txt`: minimal runtime dependencies for the helper only.
- `scripts/start_title_helper.sh`: foreground launcher for development and manual use.
- `scripts/install_title_helper.sh`: macOS LaunchAgent installer for running the helper in the background.
- `scripts/uninstall_title_helper.sh`: removes the LaunchAgent.
- `logs/`: runtime logs created by the helper.

## API

Base URL:

```text
http://127.0.0.1:3001
```

Health check:

```zsh
curl http://127.0.0.1:3001/health
```

Fetch a title:

```zsh
curl --get http://127.0.0.1:3001/fetch-title \
  --data-urlencode 'url=https://example.com'
```

Successful response:

```json
{
  "title": "Example Domain",
  "url": "https://example.com",
  "error": null
}
```

Error response:

```json
{
  "title": null,
  "url": "https://example.com",
  "error": "No title found in page"
}
```

## Manual Run

```zsh
scripts/start_title_helper.sh
```

The script creates `.venv` if needed and installs only the helper runtime dependencies from `requirements-title-helper.txt`.

Stop the foreground server with `Ctrl+C`.

## Background Install On macOS

```zsh
scripts/install_title_helper.sh
```

This installs a LaunchAgent named `io.github.yohoo.title-helper`, starts it immediately, and writes logs to:

```text
logs/title-helper.out.log
logs/title-helper.err.log
logs/proxy_server.log
```

Remove it:

```zsh
scripts/uninstall_title_helper.sh
```

Restart it after code changes:

```zsh
scripts/install_title_helper.sh
```

## Browser Integration

Yohoo tries these endpoints:

```text
http://127.0.0.1:3001/fetch-title
http://localhost:3001/fetch-title
```

Allowed browser origins are configured in `proxy_server.py`. The current allowlist includes:

- `null`, for local `file://` use.
- `http://localhost`.
- `http://127.0.0.1`.
- `https://eivind-throndsen-private.github.io`.

The Chrome extension documented in `docs/chrome-extension-title-helper.md` can also use this helper as a fallback after checking open Chrome tabs and extension-side fetches.

## Security Model

The helper is intentionally local and narrow:

- It binds to `127.0.0.1`, not the LAN.
- It only supports `http://`, `https://`, and `file://` URLs.
- Public HTTP targets are resolved and private, loopback, link-local, multicast, reserved, and unspecified IPs are rejected.
- Redirects are followed manually and revalidated on each hop.
- Requests have a timeout, redirect cap, URL length cap, and response byte cap.
- CORS is limited to the configured Yohoo origins.

`file://` support reads local HTML files by path. Keep the helper on a trusted personal machine, and do not broaden the CORS origin allowlist unless the new page is also trusted.

## Troubleshooting

Check whether the server is running:

```zsh
curl http://127.0.0.1:3001/health
```

Check whether port `3001` is occupied:

```zsh
lsof -nP -iTCP:3001 -sTCP:LISTEN
```

Read logs:

```zsh
tail -n 100 logs/proxy_server.log
tail -n 100 logs/title-helper.err.log
```

Common outcomes:

- `Origin not allowed`: add the trusted Yohoo origin to `ALLOWED_ORIGINS` in `proxy_server.py`.
- `Private or local network targets are not allowed`: the target resolved to a private/local address and was blocked by SSRF protection.
- `No title found in page`: the page did not expose a usable HTML title in the bytes fetched.
- Login page titles for private tools: keep the page open in Chrome and use the Chrome extension, because the local helper does not have browser cookies.
