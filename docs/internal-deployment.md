# Internal deployment runbook

## Live environment

Yohoo is published through the managed `static-prototype-publish` service and
protected by Google Cloud IAP.

| Setting | Value |
| --- | --- |
| Canonical URL | `https://eivind-throndsen.static.m10s.io/yohoo/` |
| Legacy URL | `https://static.m10s.io/eivind-throndsen/yohoo/` |
| Source file | `yohoo.html` |
| Environment | `production` |
| Namespace | `eivind-throndsen` (personal) |
| Prototype name | `yohoo` |
| Managed bucket | `gs://vend-prototypes` |
| Deployed object | `gs://vend-prototypes/eivind-throndsen/yohoo/index.html` |
| Onboarding service | `https://onboard.static.m10s.io` |

An unauthenticated request to the canonical URL is expected to return an HTTP
302 redirect to Google sign-in.

## Use the managed publisher

The publisher is installed as the `static-prototype-publish` plugin. At the
time of writing, its helper is located at:

```text
~/.claude/plugins/cache/vend-plugins/static-prototype-publish/1.5.0/scripts/publish_support.py
```

If that version is no longer installed, locate the current helper under the
same `static-prototype-publish` cache directory and read its `SKILL.md` before
publishing.

Do not use these legacy resources for the canonical site:

- `../static-prototype-site/publish.sh`
- GCP project `smp-pc-ai-unit-ai-productivity`
- Bucket `gs://yohoo-prototypes`
- Cloud Run service `yohoo-w5gm6kwvnq-lz.a.run.app`

Those resources form a separate, older static-site deployment. Uploading there
does not update `eivind-throndsen.static.m10s.io`.

## Publishing a content update

1. Confirm that `yohoo.html` contains the intended, tested version. Publish the
   file directly so unrelated worktree files cannot be included.

2. Check whether a test configuration is active:

   ```sh
   env | rg '^STATIC_PROTOTYPE_CONFIG='
   ```

   For this production site, the variable should be absent. If it is set, read
   the referenced configuration and do not silently fall back to production.

3. Ensure Google Cloud authentication is current:

   ```sh
   gcloud auth print-identity-token
   ```

   If this reports `Reauthentication required` or `ReauthUnattendedError`, run
   `gcloud auth login` interactively and complete the browser sign-in with the
   Vend account.

4. Resolve the personal namespace through the managed onboarding service. Do
   not print or log the identity token:

   ```sh
   static_identity_token="$(gcloud auth print-identity-token)"
   curl -sS -X POST \
     -H "Authorization: Bearer ${static_identity_token}" \
     -H 'Content-Type: application/json' \
     https://onboard.static.m10s.io/onboard
   ```

   Expected fields include:

   ```json
   {
     "slug": "eivind-throndsen",
     "bucket": "vend-prototypes",
     "url_prefix": "https://eivind-throndsen.static.m10s.io/"
   }
   ```

5. Run the managed publishing helper:

   ```sh
   python3 ~/.claude/plugins/cache/vend-plugins/static-prototype-publish/1.5.0/scripts/publish_support.py \
     --source yohoo.html \
     --environment production \
     --project 'managed central project' \
     --bucket vend-prototypes \
     --namespace eivind-throndsen \
     --namespace-type personal \
     --namespace-domain static.m10s.io \
     --legacy-url-prefix https://static.m10s.io \
     --name yohoo
   ```

   A successful run prints both the canonical and legacy URLs. A CSP warning is
   informational; a non-zero exit or final `publish:` error means deployment
   failed.

The helper validates the source and destination, stages when necessary, never
edits the source, and does not delete other bucket files.

## Verification

Verify the managed object metadata:

```sh
gsutil stat gs://vend-prototypes/eivind-throndsen/yohoo/index.html
```

Compare its SHA-256 hash with the source file. The values must match:

```sh
shasum -a 256 yohoo.html
gsutil cat gs://vend-prototypes/eivind-throndsen/yohoo/index.html | shasum -a 256
```

Inspect the deployed object for feature-specific markers when useful:

```sh
gsutil cat gs://vend-prototypes/eivind-throndsen/yohoo/index.html | \
  rg 'startAddLinkFlow|urlCaptureModal'
```

Finally, confirm that the canonical route reaches IAP:

```sh
curl -sSI --max-time 20 https://eivind-throndsen.static.m10s.io/yohoo/
```

An unauthenticated HTTP 302 confirms routing and IAP, but not authenticated
page content. The managed GCS object and checksum are the authoritative
command-line content verification. If a signed-in browser still shows an old
page after a successful hash comparison, hard-refresh with Cmd+Shift+R.

## Troubleshooting

- The browser shows code older than the managed GCS object: hard-refresh and
  inspect the canonical URL, not the old standalone Cloud Run URL.
- Publishing succeeds to `yohoo-prototypes` but the canonical page is
  unchanged: the wrong legacy publisher was used. Republish through the
  managed helper to `vend-prototypes`.
- Onboarding returns 401: renew `gcloud` authentication with the Vend account.
- Onboarding returns 403: verify the active account and managed Cloud Run
  access.
- The URL is inaccessible outside the company environment: test from inside
  the firewall and an authenticated IAP browser session.
