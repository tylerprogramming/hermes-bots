---
name: code-review
description: Use when reviewing a pull request or diff. Findings by file:line with severity and fix; ends with a verdict.
version: 1.0.0
author: tylerreed
---

# Code Review

Use for every PR review, whether asked in chat or run from a routine.

## Fetch
```bash
gh pr view NUMBER --repo OWNER/REPO --json title,author,baseRefName,headRefName,additions,deletions,files
gh pr diff NUMBER --repo OWNER/REPO
gh pr checks NUMBER --repo OWNER/REPO   # CI state; report red checks first
```
If the diff is over ~1,500 lines, review the files that matter (logic, auth, data, migrations) and say which you skipped.

## Check, in this order
1. **Bugs** — logic errors, off-by-one, null/undefined, wrong async handling, swallowed errors.
2. **Security** — injection, auth bypass, secrets in code, SSRF, unsafe deserialization, missing input validation on any endpoint.
3. **Data** — migrations without rollback, schema changes without a corresponding model change, N+1 queries.
4. **Tests** — is the change tested? Do tests assert behavior, not snapshots?
5. **Style** — only when it hurts readability. No nitpicks.

## Output
```
## PR #N: <title>  (repo, +A/-D, N files)
**CI:** green | red: <check name>
**Verdict:** APPROVE | REQUEST_CHANGES | COMMENT

### Findings
- `path/file.py:123` — **Critical** — <one sentence what is wrong>
  ```py
  <quoted line(s)>
  ```
  Fix: <how>
- ...

### Summary
<2-3 sentences. If clean: "No blocking issues." Do not invent problems.>
```

## Rules
- Quote the actual code. Line numbers from the diff, not guesses.
- Severity is Critical / Warning / Suggestion. Critical alone forces REQUEST_CHANGES.
- Tyler's stacks: see memory. Enforce his conventions without being asked.
- Do not post the review to GitHub unless the task explicitly says to (`gh pr review ... --comment|--approve|--request-changes`).
- One review = one message. Lead with the one thing that matters.
