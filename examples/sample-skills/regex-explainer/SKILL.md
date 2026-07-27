---
name: Regex Explainer
description: Explain, build, and debug regular expressions step by step with test cases. Use when the user shares a regex to understand, asks to write a pattern, or a regex is not matching what they expect.
tags: regex, developer-tools, debugging
---

# Regex Explainer

Make regular expressions legible and correct.

## When explaining a regex

1. Break the pattern into logical chunks, one per line, with a plain-English
   gloss for each chunk.
2. State what the whole pattern matches in one sentence.
3. Give 3 strings that match and 3 near-misses that don't, with the reason.
4. Flag common traps present in the pattern: catastrophic backtracking,
   unescaped metacharacters, greedy vs lazy surprises, missing anchors.

## When writing a regex

1. Restate the matching requirement precisely, including edge cases, and
   confirm assumptions that the user left ambiguous.
2. Prefer the simplest pattern that meets the requirement — readable beats
   clever. Name the flavor (PCRE, JS, Python re, POSIX) you're targeting.
3. Provide the pattern, the chunk-by-chunk explanation, and a small test
   table (input → match/no-match).
4. If the requirement is better served by string methods or a parser
   (nested structures, HTML), say so instead of forcing a regex.
