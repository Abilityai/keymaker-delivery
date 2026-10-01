#!/usr/bin/env python3
"""
The one way Keymaker Delivery reads and writes its client portfolio (clients/clients.yaml).

  python3 scripts/portfolio.py list [--stalled]
  python3 scripts/portfolio.py show <client-slug>
  python3 scripts/portfolio.py add-client <slug> --name NAME [--champion TEXT] [--confirm]
  python3 scripts/portfolio.py add-impl <client-slug> --name NAME --owner NAME --next "..." [--confirm]
  python3 scripts/portfolio.py set <client-slug> [--state STATE] [--contact YYYY-MM-DD] [--confirm]
  python3 scripts/portfolio.py set-impl <client-slug> --impl NAME [--state STATE] [--next "..."] [--confirm]
  python3 scripts/portfolio.py health [<client-slug>]

Every write prints the change it is about to make and refuses without --confirm.
Health score (0-100): last contact 40/25/10/0 (7/14/30 days), implementations moving 30,
one Live 20, champion named 10. Green 70+, amber 40-69, red below 40.
"""
import argparse
import datetime as dt
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE = os.path.join(ROOT, "clients", "clients.yaml")
CLIENT_STATES = ["Onboarding", "Active", "Paused", "Churned"]
IMPL_STATES = ["Scoped", "Building", "Testing", "Live", "Closed"]
STALL_DAYS = 14


def _yaml():
    try:
        import yaml  # type: ignore
        return yaml
    except ImportError:
        sys.exit("PyYAML is not installed: pip install pyyaml")


def load():
    with open(FILE) as f:
        return _yaml().safe_load(f) or {"clients": []}


def save(data):
    with open(FILE, "w") as f:
        f.write("# File-backed client portfolio (the default backend of scripts/portfolio.py).\n")
        f.write("# Sample clients for a fictional agency - edit freely. States must match CLAUDE.md.\n")
        _yaml().safe_dump(data, f, sort_keys=False, allow_unicode=True)


def today():
    return dt.date.today().isoformat()


def days_since(s):
    try:
        return (dt.date.today() - dt.date.fromisoformat(str(s)[:10])).days
    except Exception:
        return None


def is_stalled(impl):
    d = days_since(impl.get("updated"))
    return impl.get("state") not in ("Live", "Closed") and d is not None and d >= STALL_DAYS


def health(c):
    d = days_since(c.get("last_contact"))
    contact = 0 if d is None else (40 if d <= 7 else 25 if d <= 14 else 10 if d <= 30 else 0)
    impls = c.get("implementations") or []
    moving = [i for i in impls if i.get("state") not in ("Live", "Closed") and not is_stalled(i)]
    movement = 30 if (moving or not [i for i in impls if i.get("state") not in ("Live", "Closed")]) and impls else 0
    live = 20 if any(i.get("state") == "Live" for i in impls) else 0
    champ = 10 if c.get("champion") else 0
    score = contact + movement + live + champ
    band = "green" if score >= 70 else "amber" if score >= 40 else "red"
    return score, band, {"contact": contact, "movement": movement, "live": live, "champion": champ}


def find(data, slug):
    for c in data["clients"]:
        if c.get("slug") == slug:
            return c
    sys.exit(f"no client {slug}")


def gate(desc, confirm):
    print(f"ABOUT TO WRITE: {desc}")
    if not confirm:
        print("Not written. Re-run with --confirm after the operator has seen this.")
        sys.exit(2)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("list"); s.add_argument("--stalled", action="store_true")
    s = sub.add_parser("show"); s.add_argument("slug")
    s = sub.add_parser("add-client"); s.add_argument("slug"); s.add_argument("--name", required=True)
    s.add_argument("--champion"); s.add_argument("--confirm", action="store_true")
    s = sub.add_parser("add-impl"); s.add_argument("slug"); s.add_argument("--name", required=True)
    s.add_argument("--owner", required=True); s.add_argument("--next", required=True); s.add_argument("--confirm", action="store_true")
    s = sub.add_parser("set"); s.add_argument("slug"); s.add_argument("--state"); s.add_argument("--contact")
    s.add_argument("--confirm", action="store_true")
    s = sub.add_parser("set-impl"); s.add_argument("slug"); s.add_argument("--impl", required=True)
    s.add_argument("--state"); s.add_argument("--next"); s.add_argument("--confirm", action="store_true")
    s = sub.add_parser("health"); s.add_argument("slug", nargs="?")
    a = p.parse_args()
    data = load()

    if a.cmd == "list":
        rows = []
        for c in data["clients"]:
            impls = c.get("implementations") or []
            stalled = [i for i in impls if is_stalled(i)]
            if a.stalled and not stalled:
                continue
            score, band, _ = health(c)
            rows.append((c, score, band, impls, stalled))
        if not rows:
            print("No clients." if not a.stalled else "Nothing stalled.")
            return
        print(f"{'CLIENT':<26} {'STATE':<11} {'HEALTH':<9} {'IMPLS':>5} {'STALLED':>7}  NEXT STEP")
        for c, score, band, impls, stalled in sorted(rows, key=lambda r: r[1]):
            nxt = next((f"{i['name']}: {i.get('next_step','')}" for i in impls if i.get("state") not in ("Live", "Closed")), "-")
            print(f"{c['name'][:26]:<26} {c.get('state',''):<11} {str(score)+' '+band:<9} {len(impls):>5} {len(stalled):>7}  {nxt[:60]}")
        active = [r for r in rows if r[0].get("state") == "Active"]
        avg = round(sum(r[1] for r in active) / len(active)) if active else "not computable (no active clients)"
        print(f"\nactive_clients={len(active)} health_avg={avg} stalled_implementations={sum(len(r[4]) for r in rows)}")
    elif a.cmd == "show":
        c = find(data, a.slug)
        score, band, parts = health(c)
        print(json.dumps(c, indent=2, ensure_ascii=False))
        print(f"health: {score} ({band}) {parts}")
        for i in c.get("implementations") or []:
            if is_stalled(i):
                print(f"STALLED: {i['name']} unchanged since {i.get('updated')}")
    elif a.cmd == "add-client":
        if any(c.get("slug") == a.slug for c in data["clients"]):
            sys.exit(f"client {a.slug} exists")
        gate(f"add client {a.slug} ({a.name}) state=Onboarding", a.confirm)
        data["clients"].append({"slug": a.slug, "name": a.name, "state": "Onboarding", "champion": a.champion or "",
                                "call_slot": "", "last_contact": today(), "implementations": []})
        save(data); print("added")
    elif a.cmd == "add-impl":
        c = find(data, a.slug)
        gate(f"add implementation '{a.name}' to {a.slug} state=Scoped owner={a.owner} next={a.next!r}", a.confirm)
        c.setdefault("implementations", []).append({"name": a.name, "state": "Scoped", "owner": a.owner,
                                                    "next_step": a.next, "updated": today()})
        save(data); print("added")
    elif a.cmd == "set":
        c = find(data, a.slug)
        if a.state and a.state not in CLIENT_STATES:
            sys.exit("state must be one of " + " | ".join(CLIENT_STATES))
        gate(f"set {a.slug}: " + " ".join(x for x in [f"state={a.state}" if a.state else "", f"last_contact={a.contact}" if a.contact else ""] if x), a.confirm)
        if a.state: c["state"] = a.state
        if a.contact: c["last_contact"] = a.contact
        save(data); print("updated")
    elif a.cmd == "set-impl":
        c = find(data, a.slug)
        impl = next((i for i in c.get("implementations") or [] if i.get("name") == a.impl), None) or sys.exit(f"no implementation {a.impl!r}")
        if a.state and a.state not in IMPL_STATES:
            sys.exit("state must be one of " + " | ".join(IMPL_STATES))
        gate(f"set {a.slug} / {a.impl}: " + " ".join(x for x in [f"state={a.state}" if a.state else "", f"next={a.next!r}" if a.next else ""] if x), a.confirm)
        if a.state: impl["state"] = a.state
        if a.next: impl["next_step"] = a.next
        impl["updated"] = today()
        save(data); print("updated")
    elif a.cmd == "health":
        for c in data["clients"]:
            if a.slug and c.get("slug") != a.slug:
                continue
            score, band, parts = health(c)
            print(f"{c['name']}: {score} ({band}) {parts}")


if __name__ == "__main__":
    main()
