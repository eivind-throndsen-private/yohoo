# Pre-Commit Hook for Yohoo

## Overview

The `.git/hooks/pre-commit` hook automatically updates the commit information displayed in the footer of `yohoo.html` before each commit.

## What It Does

Before every commit, the hook:
1. Extracts the date and message from the last commit
2. Updates the `<!-- BUILD_COMMIT_INFO -->` section in `yohoo.html`
3. Stages the updated file for the current commit

## Example

The footer will show something like:
```
Last commit: 2026-01-08 16:27 - "Add GitHub commit info display in footer"
```

## Important Notes

- **No network calls**: The commit info is static HTML, no GitHub API calls
- **No credentials**: Everything is local git operations
- **Second-to-last commit**: The displayed info is from the previous commit (the current commit hasn't happened yet when the hook runs)
- **This is expected**: You acknowledged this tradeoff is acceptable

## Hook Installation

The hook is already installed at `.git/hooks/pre-commit` and is executable.

If you need to reinstall it:
```bash
chmod +x .git/hooks/pre-commit
```

## Hook Location

**Important**: Git hooks are NOT committed to the repository (they're in `.git/hooks/`). If you clone this repo elsewhere, you'll need to copy the pre-commit hook manually.

To share the hook with others, keep a copy in the repo:
```bash
cp .git/hooks/pre-commit hooks/pre-commit
git add hooks/pre-commit
```

Then others can install it:
```bash
cp hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

## Troubleshooting

If the commit info doesn't update:
1. Check hook is executable: `ls -l .git/hooks/pre-commit`
2. Verify hook exists: `cat .git/hooks/pre-commit`
3. Test hook manually: `.git/hooks/pre-commit`

## Disabling the Hook

To temporarily disable:
```bash
chmod -x .git/hooks/pre-commit
```

To re-enable:
```bash
chmod +x .git/hooks/pre-commit
```
