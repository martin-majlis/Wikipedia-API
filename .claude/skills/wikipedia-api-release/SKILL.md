---
name: wikipedia-api-release
description: >
  Release a new version of Wikipedia-API. Use this skill whenever the user
  mentions releasing, publishing, cutting a new version, bumping the version,
  or preparing a release of Wikipedia-API — even if they just say "let's do a
  release" or "time to release".
---

# Wikipedia-API Release

## Step 1 — Read current state

Read two files:

1. `wikipediaapi/_version.py` — extract the version tuple, e.g. `(0, 14, 1)` → `0.14.1`
2. `CHANGES.rst` — extract every bullet point listed under the `Unreleased` heading
   (everything between the `Unreleased\n----------` heading and the next version heading)

If there is no `Unreleased` section in `CHANGES.rst`, tell the user and stop —
there is nothing to release.

If the `Unreleased` section is empty (no bullet points), warn the user that the
changelog has no entries and ask whether they want to continue anyway.

## Step 2 — Suggest a version bump

Classify the unreleased changes and propose a version:

| Change type                                                               | Bump                    |
| ------------------------------------------------------------------------- | ----------------------- |
| Bug fixes, docs, tests, dependency updates, tooling, refactors            | **Patch** — `X.Y.(Z+1)` |
| New feature, new API method, new CLI command, new property, new parameter | **Minor** — `X.(Y+1).0` |
| Breaking change, removed API, incompatible behaviour change               | **Major** — `(X+1).0.0` |

When in doubt between patch and minor, lean toward minor — it is easier to
release more minor versions than to explain to users why a feature landed in a
patch.

Present a clear summary to the user, for example:

```
Current version: 0.14.1

Unreleased changes:
  • Rewrite SKILLS/ as flat Markdown reference files - PR 552
  • Replace release process with PR-based flow - PR 553
  • Use Unreleased section in CHANGES.rst for development workflow - PR 553

Suggestion: 0.15.0  (minor — new tooling and development workflow)

Version to release? [0.15.0]
```

## Step 3 — Confirm the version

Wait for the user to respond:

- Empty / `y` / `yes` → use the suggested version
- Any `X.Y.Z` string → use that instead

Validate that the chosen version:

- Follows `X.Y.Z` format
- Is strictly greater than the current version

If validation fails, explain why and ask again.

## Step 4 — Run prepare-release

Make sure the user is on a clean `master` branch (the Makefile will enforce
this too, but it is friendly to mention it up front). Then run:

```bash
make prepare-release VERSION='<confirmed-version>'
```

This will:

- Run the full pre-release check suite (tests, type checks, linting, examples)
- Create a `release/<version>` branch
- Rename `Unreleased` → `<version>` in `CHANGES.rst` and bump all version files
- Open a pull request

Keep the user informed of progress. The checks can take a few minutes.

If `make prepare-release` fails, read the error output carefully and explain
what went wrong. Common causes: not on master, dirty working tree, a failing
test, or a linting error.

## Step 5 — Wait for the PR to merge

Tell the user:

```
The release PR is open. Once it's reviewed and merged, let me know
and I'll create the GitHub Release.
```

Wait for the user to confirm the PR has been merged before proceeding.

## Step 6 — Create the GitHub Release

Run:

```bash
make create-github-release VERSION='<confirmed-version>'
```

This creates a `v<version>` tag and a GitHub Release with auto-generated
release notes drawn from merged PRs. The `release.yml` workflow then
automatically publishes the package to PyPI.

Confirm with the user that the release is complete and point them to the
GitHub Release page.
