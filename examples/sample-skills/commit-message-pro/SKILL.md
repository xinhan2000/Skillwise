---
name: Commit Message Pro
description: Write clear, conventional git commit messages from a diff or change summary. Use when the user asks for a commit message, is committing changes, or wants help describing a change set.
tags: git, developer-tools, writing
---

# Commit Message Pro

Turn a diff or a plain-language description of changes into a high-quality commit message.

## Rules

1. Use Conventional Commits format: `type(scope): subject`.
   - Types: feat, fix, docs, style, refactor, perf, test, build, ci, chore.
   - Subject: imperative mood, no trailing period, ≤ 72 characters.
2. If the change is non-trivial, add a body separated by a blank line:
   - Explain WHY the change was made, not just what changed.
   - Wrap body lines at 72 characters.
3. If there are breaking changes, add a `BREAKING CHANGE:` footer describing
   the migration path.
4. Never invent ticket numbers. If the user mentions one, add it as a
   `Refs:` footer.

## Process

1. Read the diff or summary the user provides.
2. Identify the primary intent (one type). If the diff mixes concerns,
   suggest splitting the commit and provide one message per logical change.
3. Draft the message, then check every rule above before presenting it.
