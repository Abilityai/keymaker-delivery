---
name: clients
description: The client portfolio - every client with its health score, state, implementations and next step; stalls first. Use for "how are the clients", "who is at risk", "what's stalled", "weekly delivery check".
argument-hint: "[--stalled]"
allowed-tools: [Read, Bash, Glob, Grep]
user-invocable: true
metadata:
  version: "0.1"
  created: 2026-10-01
  author: keymaker
---

# Clients

1. Check the shared folder for new handoffs from Keymaker Sales (`*-handoff.md` not yet recorded
   as a client). If there is one, say so first and offer to create the client with
   `/client-status`.
2. Run `python3 scripts/portfolio.py list` (`--stalled` if asked). Print the table.
3. Read it back in three lines: who is red or amber and why (the health parts from
   `portfolio.py health`), what is stalled and for how long, and the one thing the delivery
   manager should do today.
4. Record the numbers this desk owns if `record_metrics` is available (`active_clients`,
   `health_avg`, `stalled_implementations`); otherwise print the line the script prints.

Never contact a client. Never change a state here; that is `/client-status`, with a reason.
