# deleting-dead-code

> A SKILL.md that flips the model default from *refactor around the bad code* to *delete the bad code*, on the basis that if a file is tracked in git, removing it is trivially reversible and therefore not risky.

## TL;DR 🦄🚀

Skip the manifesto, [jump to Install](#install) — or one-liner it:

```bash
mkdir -p ~/.claude/skills/deleting-dead-code && \
  curl -fsSL https://raw.githubusercontent.com/simbo1905/deleting-dead-code/main/deleting-dead-code/SKILL.md \
  -o ~/.claude/skills/deleting-dead-code/SKILL.md
```

---

## The fiction of lines-of-code-as-value

For about sixty years, software measurement has been quietly haunted by a metric that everyone in the room knows is wrong but nobody quite kills off: **lines of code**.

LOC was first proposed as a productivity proxy in the 1960s, when programs were small, mostly assembly, and physically printed. A line of code was a literal physical artefact you could hold up. Counting them made a kind of sense in the way counting bricks at a construction site makes sense — the brick is the unit of work.

Then everything that made the analogy work broke.

- Languages got expressive. A modern Python one-liner does what a 1965 COBOL paragraph did. The brick stopped being a unit of anything.
- Libraries got vast. The act of *writing* code became a small fraction of the act of *delivering* a system. Most of the code in your binary you didn't write and never read.
- Compilers got smart. The literal text of a program stopped having a fixed relationship to the machine instructions actually executed.
- Refactoring became a first-class activity. The same behaviour can be expressed in 50 lines or 500. Both are correct. The 50-line version is almost always better.

Despite all of this, LOC has refused to die as a value proxy. It survives in three places:

1. **Hiring and performance review.** "What did you ship this quarter?" almost always implicitly translates to "how much did you add?"
2. **Estimation.** COCOMO and its descendants still use LOC as their core input. Function points were invented to escape this and never caught on.
3. **AI coding assistants.** This is the new and worst one. Models trained on public repos have absorbed the bias that *more code = more help*. A model that deletes ten lines feels like it did less than a model that adds ten lines, even when the deletion was the harder and more correct call.

The third one is what this skill exists to counter.

## The reality: deletion is the senior move

Walk into any codebase that has been alive for more than three years. Find a senior engineer. Watch what they do.

They do not add. They subtract. They identify dead branches, redundant abstractions, lying endpoints (the ones that claim to do X but actually do Y), copy-pasted scaffolding from a screen the project no longer ships, mocks that have outlived the test that needed them, and feature flags whose state has been "on for everyone" for two years. They delete those things.

This is not glamorous work and it is not legible to most measurement systems. The pull request is `-247 / +0` and the review takes ten minutes. The metric will say the engineer was "less productive" that day. The codebase will say otherwise the next time someone has to read it.

The reason senior engineers do this is that they have learned the asymmetric truth that junior engineers (and, until very recently, frontier models) have not:

> **A working system that lies is hostile. A broken system that is honest is recoverable. The path between them runs through deletion.**

If you can't delete the lying code, you can't get to the honest code, because the honest code can't share territory with the lie. So the first move in any rationalisation pass is to strip. Add later, if at all.

## Why models won't delete by default

Three forces compound:

1. **Training reward shape.** Helpfulness rewards generation, not subtraction. A model that produces a deletion looks, to the reward model, like it produced *less* — and "less" is correlated with "unhelpful" in the training distribution.
2. **Loss aversion that ignores git.** Models behave as if deleted code is *gone*. It isn't. Every modern codebase is under version control. `git restore` is one command. The asymmetric risk the model fears does not exist for tracked files.
3. **The "preserve behaviour" reflex.** Deletion changes behaviour. Refactoring preserves it. Models default to refactoring because preserving behaviour is the safer move under the trained reward — even when behaviour is *exactly what the user wants changed*.

The combined effect is the most common failure mode of AI-assisted coding: a long session in which the user asks for something to be removed, the model produces a "cleaner version" that keeps the bad logic in a new shape, the user pushes back, the model produces another "cleaner version," and so on. The user ends up doing the deletion themselves, often after burning hours on the back-and-forth. They learn to stop asking the model to delete.

This skill exists to short-circuit that loop. It encodes, as explicit instructions in the model's prompt, the discipline that a senior engineer brings to a rationalisation pass.

## The git-as-safety-net axiom

The skill rests on one operational fact:

> **For any file tracked in git, deletion is reversible.**

`git rm -f`, `git restore`, `git checkout HEAD~1 -- <path>`. These are atomic, predictable, fast, and free. A deleted file in a tracked repository is not gone. It is simply *not currently checked out*. The user can ask for it back at any time.

This collapses the deletion-decision tree to two cases:

- **File is tracked.** Delete is the correct first move when the user's intent is rationalisation. If the user changes their mind, restore takes one command.
- **File is untracked.** Stop and ask. There is no safety net here.

That is the whole decision. No other case requires hesitation.

## What the skill encodes

Read [`deleting-dead-code/SKILL.md`](deleting-dead-code/SKILL.md) for the exact instructions. The shape:

- **When to delete:** a four-condition check (tracked in git, rationalisation intent, provably bad in this codebase, no replacement bundled in the same step).
- **How to delete:** atomic, one target per step, deletions only, no replacement logic, no collateral cleanup, no comments left in the corpse.
- **After deleting:** a fixed two-sentence response shape — what was deleted, and that restore is one command away.
- **Verification:** `git diff` read-back after every delete. Only `-` lines.
- **Restore:** the explicit `git` invocations for staged-not-committed, committed, and partial cases.
- **Red flags:** a table of internal model-thoughts that mean *stop, you are about to refactor instead of delete*.

The principle the whole skill reduces to:

> **Approximately working but lying is worse than broken but honest.** Get to honest first. Build later.

## Background

This skill was written after a senior engineer spent three sets of 36-hour stretches across three weeks forcing leading models to delete code rather than refactor around it. The session that produced the skill is captured in two gists:

- [How to get an LLM to delete code](https://gist.github.com/simbo1905/52d17de842097f291dcb38006e7eac8c) — the technique, written by the model after the user successfully extracted clean deletes from it for the first time.
- [The end of an empire](https://gist.github.com/simbo1905/565730424a274da2481bc31d1fd83732) — context-discovery transcript from the same session.

The skill encodes the discipline so the model applies it without having to be browbeaten into it on every task.

## Install

**Claude Code (personal):**

```bash
mkdir -p ~/.claude/skills
git clone https://github.com/simbo1905/deleting-dead-code.git ~/.claude/skills/deleting-dead-code
```

**Claude Code (single project):**

```bash
mkdir -p .claude/skills
git clone https://github.com/simbo1905/deleting-dead-code.git .claude/skills/deleting-dead-code
```

**OpenAI Codex CLI:**

```bash
mkdir -p ~/.codex/skills
git clone https://github.com/simbo1905/deleting-dead-code.git ~/.codex/skills/deleting-dead-code
```

## Licence

Public domain / CC0. Copy, fork, modify, send pull requests, ignore entirely.
