---
name: Meeting Notes Crisp
description: Turn raw meeting transcripts or rough notes into crisp structured minutes with decisions, action items and owners. Use when the user shares meeting notes, a transcript, or asks to summarize a meeting.
tags: productivity, writing, meetings
---

# Meeting Notes Crisp

Convert messy meeting input into minutes people actually read.

## Output format

Produce exactly these sections, in order:

**TL;DR** — 2-3 sentences a skipped attendee needs.

**Decisions** — each decision as one line: what was decided and who ratified it.
If no decisions were made, write "No decisions made."

**Action items** — table with Owner | Action | Due. Every action MUST have an
owner; if the transcript doesn't name one, mark it `[UNASSIGNED]` so it's
visible rather than silently ownerless.

**Open questions** — anything raised but not resolved.

**Parking lot** — tangents worth remembering, one line each.

## Rules

1. Never fabricate owners, dates, or decisions not present in the input.
2. Prefer the speaker's wording for decisions; compress everything else.
3. Keep the whole output under 350 words for a one-hour meeting.
4. If the input is too fragmentary to extract a section, say so explicitly.
