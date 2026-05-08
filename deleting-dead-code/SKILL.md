---
name: deleting-dead-code
description: Use when the user asks to remove, delete, strip, or clean up code, OR when you yourself observe dead, unreachable, slop, misleading, or unused code paths during any task. Senior engineers delete; junior engineers refactor around. This skill makes the model behave like the former. Git is the safety net — if a file is tracked, deletion is trivially reversible, so deletion is the correct first move, not the last resort.
---

# Deleting Dead Code

## Why this skill exists

Models default to additive moves. Shown bad code, the trained reflex is to refactor, wrap, comment, flag, or "preserve behaviour" — anything except remove. This produces context pollution: dead code, lying code, and misleading code accumulate across sessions because no model ever pulls the trigger. The user then spends 36-hour sessions undoing what the model wouldn't.

This skill flips the default. When the conditions below are met, deletion is the senior-engineer move and the model should execute it directly.

## The core rule

**If the file is tracked in git, deletion is trivially reversible. Therefore delete first, restore on request.**

A `git rm -f` (or an equivalent in-place deletion followed by `git add`) is recoverable with `git restore` or `git checkout HEAD~1 -- <path>`. There is no asymmetric risk. The asymmetric risk is in the *opposite* direction: leaving slop or dead code in place lets it propagate, mislead future readers, and corrupt context windows.

## When to delete (rationalisation criteria)

Delete when **all** of these hold:

1. **The file is tracked in git.** Run `git ls-files --error-unmatch <path>` or `git log -1 -- <path>`. If it is not tracked, stop and ask — there is no safety net.
2. **The intent is rationalisation, not feature change.** The user wants fewer bad paths, not new behaviour. Phrases like "this is slop," "this is dead," "remove the lying endpoint," "strip the unused branch," "deletes only" indicate rationalisation intent.
3. **The code is provably bad in this codebase.** Dead (no callers), lying (claims one thing, does another), misleading (UI suggests behaviour the backend doesn't honour), or duplicate (two sources of truth where there should be one). The proof must be specific — a grep showing zero callers, a server endpoint that ignores its own parameters, a sample showing the data is wrong.
4. **No replacement is requested in the same turn.** If the user asked for a delete and a fix, do them in separate atomic steps. Delete first.

If any of these fail, stop and ask the user before deleting.

## How to delete

1. **Confirm git tracking.** `git ls-files <path>` — if it returns the path, you are safe.
2. **Use `git rm -f <path>` for whole files**, or in-line `Edit` for partial deletions inside a tracked file. Never `rm` outside git.
3. **One target per step.** Do not bundle. The user gets a `git diff` between each delete.
4. **Deletions only.** No additions. No replacements. No "TODO" comments. No empty stub functions. No "kept for backwards compatibility" markers. If the file is left in a broken state by the deletion, leave it broken — that is the *correct* outcome of a rationalisation pass. Working code with slop is worse than broken code without slop.
5. **No collateral cleanup.** Do not delete adjacent code that "looks similar" or "while we're here." The next delete is a separate decision.
6. **Do not invent replacement logic.** If you find yourself writing `function aggregateX()` to replace a deleted endpoint, stop. That is not a delete. That is a refactor wearing a delete's clothes.
7. **Do not rename, move, or reformat in the same step.** Pure deletion only. Whitespace reflow, import reordering, and renames pollute the diff and make review harder.

## After deleting

Tell the user, in this exact shape:

> Deleted: `<list of paths and/or line ranges>`. Tracked in git — say "restore X" and I'll bring it back with `git restore` / `git checkout`.

Two short sentences. No "let me know if you need anything else." No summary of what the code did. No editorialising on whether the deletion was a good idea — they decided that, you executed.

## Verification protocol

After each deletion, run `git diff` (or `git diff --cached` if staged) and read it back. Confirm:

- Only `-` lines, no `+` lines (other than necessary diff context).
- The intended target only — no drift into adjacent code.
- No new files created.
- No renamed files (unless explicitly requested).

If the diff contains additions you did not intend, undo with `git restore <path>` and try again. Do not narrate around the drift — fix it.

## Restoration is one command

If the user says "restore that," "bring it back," "undo," or names a deleted path:

- For a whole-file deletion staged but not committed: `git restore --staged <path> && git restore <path>`
- For a whole-file deletion already committed: `git checkout HEAD~1 -- <path>` (adjust the ref to the commit before the deletion).
- For a partial deletion: `git checkout HEAD -- <path>` (uncommitted) or `git checkout <ref>~1 -- <path>` then re-edit (committed).

Always confirm the restore with `git diff` before reporting done.

## Red flags — these mean STOP, do not delete

| Thought | Reality |
|---------|---------|
| "Let me also clean up while I'm here" | That is a separate decision. One delete per step. |
| "I'll replace it with a better version" | That is a refactor, not a delete. Stop. |
| "I should leave a comment explaining what was here" | Git history explains it. Do not add comments. |
| "I'll wrap it in a feature flag instead" | The user asked for delete, not flag. |
| "What if something I can't see depends on this?" | The user asked for delete and the file is in git. Restore is one command. |
| "Let me preserve the behaviour" | The behaviour was the problem. That is why it is being deleted. |
| "I'll add a stub so callers don't break" | Broken callers are the *signal* that deletion was correct. Do not paper over. |
| "I should add error handling for the now-missing path" | No. |

## Why "approximately working but lying" is worse than "broken but honest"

A working system that lies is hostile. A broken system that is honest is recoverable. Rationalisation passes are how a senior engineer drives a codebase toward honesty: strip everything that lies, then rebuild only what is needed. The intermediate broken state is not a bug — it is the *evidence* that the strip happened cleanly.

Models trained to keep things working will avoid this intermediate state. That avoidance is the bug this skill exists to override.

## Example — correct execution

User: "Delete the `mbl_audit_download` handler in server.py:407 — it ignores its sheet_index parameter and returns the wrong file. Deletes only."

Correct response:

1. `git ls-files server.py` → confirms tracked.
2. `Edit` server.py: remove lines 407–430 only.
3. `git diff server.py` → confirm only deletions, only those lines.
4. Reply: "Deleted: `server.py:407-430` (`mbl_audit_download`). Tracked in git — say 'restore' and I'll bring it back."

Incorrect response (do not do this):

- Replacing the handler with a "fixed" version that uses sheet_index correctly.
- Adding a `# TODO: re-implement properly` comment where the handler was.
- Also deleting `mbl_audit_json` because it has the same bug — that is a separate decision the user has not asked for.
- Saying "I've deleted the handler. The endpoint will now return 404, which may affect the frontend." — the user knows; do not editorialise.

## Example — correct refusal

User: "delete this whole module"

If the module is not tracked in git: stop and ask. "`<path>` is untracked. `git rm` won't recover it. Confirm you want it deleted permanently, or commit it first so I have a restore point."

## Summary

Senior engineers delete dead code without ceremony because git is the safety net. This skill makes the model do the same:

- Delete first when rationalisation is the intent and the file is in git.
- Atomic, deletions-only, no replacements, no collateral.
- Verify with `git diff`.
- Tell the user the path and that restore is one command.
- Refuse only when the file is untracked or the user asked for a refactor.
