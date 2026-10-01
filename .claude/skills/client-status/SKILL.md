---
name: client-status
description: One client in depth, or record what changed - a contact, an implementation moving state, a new client from a Sales handoff. Use for "what's going on with X", "X moved to testing", "we spoke to X today", "set up the new client from the handoff".
argument-hint: "<client> [--note \"...\"] [--state <state>]"
allowed-tools: [Read, Write, Bash, Glob, Grep, AskUserQuestion]
user-invocable: true
metadata:
  version: "0.1"
  created: 2026-10-01
  author: keymaker
---

# Client status

## Read

`python3 scripts/portfolio.py show <slug>`. Report: state, health with its parts, each
implementation with state, owner, next step and days since it changed, and any stall.

## Record a change

Every write goes through `scripts/portfolio.py`, which prints the change and needs `--confirm`.
Show the operator the line, then re-run with `--confirm`.

| What happened | Command |
|---|---|
| we spoke to the client | `set <slug> --contact <YYYY-MM-DD>` |
| client state changed | `set <slug> --state <Onboarding|Active|Paused|Churned>` - ask why, record the reason in your reply |
| implementation moved | `set-impl <slug> --impl "<name>" --state <Scoped|Building|Testing|Live|Closed> [--next "..."]` |
| new piece of work | `add-impl <slug> --name "<name>" --owner "<who>" --next "<first step>"` |

## New client from a Sales handoff

Read `drafts/<slug>-handoff.md` from the shared folder. Then, with confirmation each time:
`add-client <slug> --name "<client>" --champion "<champion>"`, one `add-impl` per thing sold with
`--next "Kickoff call"`, and tell the delivery manager the client exists and what the first call
must cover.

## With the project skills assigned

If `/project-init` and `/project-task` are available (Skills Library) and `GITHUB_TOKEN` is set,
offer to open the client's project registry and file the first tasks there.
