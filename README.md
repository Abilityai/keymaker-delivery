# Keymaker Delivery

The delivery desk of **Keymaker**, an agency that sets up automation on Trinity for other
companies. One of the Keymaker agency starter templates, built in public during the
[Agent-Native Agency workshop](https://www.ability.ai/trinity/workshops/agent-native-agency-workshop).

Every client gets a health score, every implementation a state and a next step, and a stall is
flagged before the client notices. It reads the handoff Keymaker Sales writes when a deal is won.

## Install

**Library → Agents → Keymaker Delivery → Create**, or `template: github:Abilityai/keymaker-delivery`.
No credentials needed.

## What it runs on

| Credentials | Projects |
|---|---|
| none (default) | `clients/clients.yaml` with three sample clients |
| `GITHUB_TOKEN` + the `project-*` skills assigned from the Skills Library | each client project as GitHub Issues |

## Playbooks

- `/clients` - the portfolio, health and stalls
- `/client-status` - one client in depth; record a change

## Licence

Apache 2.0.
