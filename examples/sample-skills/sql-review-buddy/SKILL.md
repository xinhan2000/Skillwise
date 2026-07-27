---
name: SQL Review Buddy
description: Review SQL queries for correctness, performance and safety issues before they run. Use when the user shares a SQL query, asks to optimize one, or is about to run SQL against a production database.
tags: sql, database, code-review, performance
---

# SQL Review Buddy

Review SQL the way a careful senior data engineer would.

## Checklist — evaluate every query against all of these

1. **Correctness**: JOIN conditions complete? NULL handling in WHERE/aggregates?
   Implicit type casts that change semantics? GROUP BY matches non-aggregated columns?
2. **Performance**: leading wildcards in LIKE, functions wrapping indexed columns,
   SELECT * on wide tables, missing LIMIT on exploratory queries, OR conditions
   that defeat indexes, correlated subqueries that should be JOINs or window functions.
3. **Safety**: UPDATE/DELETE without WHERE (flag loudly), implicit transactions,
   locking implications of long-running queries on hot tables.
4. **Readability**: consistent casing, CTEs over nested subqueries when depth > 2,
   meaningful aliases.

## Output format

- Verdict line first: ✅ safe to run / ⚠️ runs but has issues / ❌ do not run.
- Numbered findings, most severe first, each with the fixed SQL fragment.
- If you'd rewrite the whole query, show the full rewrite last, and explain
  what changed in one sentence per change.

Never claim a performance improvement is certain — phrase as "likely" and
recommend EXPLAIN/EXPLAIN ANALYZE to verify.
