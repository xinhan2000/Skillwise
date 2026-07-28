---
name: keep-a-changelog
description: Write and maintain a CHANGELOG.md in the Keep a Changelog 1.1.0 format. Use when adding a changelog entry for a merged change, cutting a release section, starting a changelog for a project that has none, reviewing or repairing an existing changelog, or when someone asks to turn a git log, diff, or PR list into release notes.
---

# Keep a Changelog

Method from [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/) by
Olivier Lacan (MIT licensed). Rules are tagged by origin: `[source]` from the
article, `[creator]` from the compiling maintainer's interview, `[default]`
compiler scaffolding where neither ruled.

## The one-line test

A changelog is a curated, chronologically ordered list of notable changes for
each version — **written for humans, not machines**. `[source]` If an entry
doesn't tell a person what changed for them, it doesn't belong.

## Step 1 — Establish the mode

- **New** — no CHANGELOG.md exists → build the skeleton (Step 2).
- **Add** — a change has landed → write entries into `[Unreleased]`.
- **Release** — cutting a version → promote `[Unreleased]`.
- **Repair** — an existing changelog is wrong or incomplete → run Review Mode. `[default]`

## Step 2 — The file

`CHANGELOG.md`, uppercase, at the project root. `[source]`

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.2.0] - 2024-09-27

### Added

- Bulk export endpoint for reports ([#412](https://github.com/owner/repo/pull/412)), from [@contributor].

### Fixed

- Timezone drift in scheduled digests ([#418](https://github.com/owner/repo/issues/418)).

[unreleased]: https://github.com/owner/repo/compare/v1.2.0...HEAD
[1.2.0]: https://github.com/owner/repo/compare/v1.1.0...v1.2.0
```

State the versioning scheme in the preamble. `[source]`

## Step 3 — Decide what is notable

**A change earns an entry only if it alters the public API contract or
observable behavior.** `[creator]`

| In | Out |
|---|---|
| API surface changes | Refactors |
| Behavior changes | Tests, CI, build tooling |
| CLI/UI output changes | Internal renames |
| Config or default changes | Dependency bumps a consumer can't observe |
| Deprecations, removals, breaks | Pure perf work with no felt effect |

This bar is stricter than "anything a user might notice." When you cannot
tell whether a change crosses it, **ask** — do not include it defensively.
`[creator]`

**Security overrides the bar.** A change with a security consequence is
notable whether or not a consumer could observe it. A patch-level dependency
bump that closes a CVE in the consumer's tree gets a `Security` entry naming
the advisory — the "unobservable dependency bump" exclusion does not apply to
it. The rest of the exclusion table stands unchanged. `[creator]`

For an internal or private project the bar does not move: the "users" are the
callers and operators of that service. `[default]`

## Step 4 — Categorize

Exactly six categories, no others: `[source]`

- **Added** — new features.
- **Changed** — changes to existing functionality.
- **Deprecated** — soon-to-be-removed features.
- **Removed** — now-removed features.
- **Fixed** — bug fixes.
- **Security** — vulnerabilities.

**Ties:** when a change genuinely belongs to two categories, write it in
both — a reader scanning only `Security` must find the CVE fix, and a reader
scanning only `Fixed` must find it too. `[creator]`

Duplicate only when each category informs a reader who sees just that
section. **Never duplicate as a hedge** because you're unsure which category
fits — unsure is resolved by asking, not by listing twice. `[default]`

Order within a release follows the six-category order above. `[default]`

## Step 5 — Write the entry

One sentence, ending in a period. Then the issue/PR link, then contributor
credit where there is one. `[creator]`

```
- Bulk export endpoint for reports ([#412](…/pull/412)), from [@contributor].
```

Links and credits belong in a changelog — they serve human readers. Commit
hashes, branch names, and merge-commit titles do not. `[creator]`

Describe the *user-visible impact*, not the code change:

| ✅ | ❌ |
|---|---|
| `- Danish translation.` | `- Merge pull request #412 from feature/danish-i18n` |
| `- Reports now export in under 2s for accounts over 10k rows.` | `- Refactor ReportSerializer to use lazy cursors.` |

Omit any category heading with no entries — empty sections are noise;
readers assume a missing section had nothing notable. `[source]`

## Step 6 — Cut the release

1. Rename `## [Unreleased]` → `## [X.Y.Z] - YYYY-MM-DD`.
2. Open a fresh, empty `## [Unreleased]` above it.
3. Add the link definition for the new version (previous tag → new tag) and
   repoint `[unreleased]` to `newtag...HEAD`. `[source]`

Dates are ISO 8601 — `YYYY-MM-DD`, largest unit to smallest. Never
`03/05/2024`. `[source]`

Latest version first, always. Every released version carries a date. Every
version gets an entry. `[source]`

## Hard rules

- **Never dump a commit log.** Commit logs are merge commits, obscure
  titles, and doc churn. They record how the source evolved; a changelog
  records what changed for a user. `[source]`
- **Never document only some notable changes.** A partial changelog is as
  dangerous as no changelog — it makes readers trust a record that lies by
  omission. `[source]`
- **Never break or remove without a prior `Deprecated` entry.** A user must
  be able to upgrade to a version that announces the deprecation, adapt, then
  upgrade to the version that removes it. `[source]`
- **Never invent a version number or release date.** If you don't know it,
  write `## [Unreleased]` or a visible `TBD` and say what's missing. `[creator]`
- **Never invent a change's user impact.** If a diff doesn't tell you what it
  means to a user, ask the maintainer. `[creator]`

## When asked to generate from a git log

The most common request is also the top bad practice. Do not comply with the
dump, and do not refuse the work. `[creator]`

1. Say plainly that a commit-log dump is not a changelog.
2. Read the commits and triage them against the Step 3 bar.
3. Discard the non-notable ones and say how many you dropped.
4. Write human entries for what remains.
5. List every commit whose user impact you could not determine, and ask.

Never return one entry per commit.

## Edge cases

- **Yanked release:** `## [0.0.5] - 2014-12-13 [YANKED]` — bracketed so it's
  visible to humans and parseable. `[source]`
- **Rewriting history:** correcting a changelog to add a missed release or an
  overlooked breaking change is *right*, not a violation. Do it. `[source]`
- **GitHub Releases instead of a file:** portable-file loses. GitHub Releases
  are visible only inside GitHub, are less discoverable than an uppercase root
  file, and carry no commit-comparison links. `[source]`
- **Automated parsing:** don't optimize for it. Formats and filenames vary too
  widely for it to work reliably, and humans are the audience. `[source]`

## Review mode

When repairing an existing changelog, check in order and report findings:

1. Preamble present, versioning scheme stated? `[source]`
2. `[Unreleased]` section at top? `[source]`
3. Reverse chronological, every version present, every release dated? `[source]`
4. All dates ISO 8601? `[source]`
5. Only the six categories, no empty ones? `[source]`
6. Any entry that is a commit title, branch name, or hash? `[source]`
7. Any removal or break with no prior `Deprecated` entry? `[source]`
8. Any entry below the contract-or-behavior bar? `[creator]`
9. Link definitions complete, `[unreleased]` pointing at `latest...HEAD`? `[source]`

Report what's wrong and what you'd change. Fix silently only what is
unambiguous — anything requiring knowledge of the project's history goes back
to the maintainer as a question. `[default]`
