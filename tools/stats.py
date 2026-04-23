#!/usr/bin/env python3
"""Pretty-print teleport telemetry funnels from the counter endpoint.

Usage:
    python3 tools/stats.py
"""
import json
import sys
import urllib.request

COUNTER_URL = "https://teleport.mnlt.deno.net"


def fetch_stats() -> dict:
    with urllib.request.urlopen(f"{COUNTER_URL}/stats", timeout=10) as r:
        return json.loads(r.read())


def pct(a: int, b: int) -> str:
    if b == 0:
        return "—"
    return f"{100 * a / b:.0f}%"


def rule(title: str) -> None:
    print(title)
    print("─" * max(len(title), 12))


def print_install_funnel(stats: dict) -> None:
    started = stats.get("install-started", 0)
    completed = stats.get("install-completed", 0)
    first = stats.get("first-run", 0)
    migr = stats.get("migration", 0)

    rule("INSTALL FUNNEL")
    print(f"  install-started       {started:>6}")
    print(f"  install-completed     {completed:>6}   {pct(completed, started):>5} of started")
    print(f"  first-run             {first:>6}   {pct(first, completed):>5} of completed")
    print(f"  migration             {migr:>6}   {pct(migr, first):>5} of first-run")
    print()


def print_per_service_funnel(
    stats: dict, started_prefix: str, completed_prefix: str, title: str
) -> None:
    started_by: dict[str, int] = {}
    completed_by: dict[str, int] = {}
    for key, val in stats.items():
        if key.startswith(started_prefix):
            started_by[key[len(started_prefix):]] = val
        elif key.startswith(completed_prefix):
            completed_by[key[len(completed_prefix):]] = val

    if not (started_by or completed_by):
        return

    rule(title)
    services = sorted(
        set(started_by) | set(completed_by),
        key=lambda s: -started_by.get(s, 0),
    )
    print(f"  {'service':<20} {'started':>8} {'done':>6} {'conv':>6}")
    for svc in services:
        s = started_by.get(svc, 0)
        c = completed_by.get(svc, 0)
        print(f"  {svc:<20} {s:>8} {c:>6} {pct(c, s):>6}")
    print()


def print_discovery_funnel(stats: dict) -> None:
    detected: dict[str, int] = {}
    used: dict[str, int] = {}
    for key, val in stats.items():
        if key.startswith("mcp-detected/"):
            detected[key.split("/", 1)[1]] = val
        elif key.startswith("skill-used/"):
            used[key.split("/", 1)[1]] = val

    if not (detected or used):
        return

    rule("DISCOVERY → USE (per MCP)")
    ids = sorted(
        set(detected) | set(used),
        key=lambda s: -(detected.get(s, 0) + used.get(s, 0)),
    )
    print(f"  {'id':<25} {'detected':>9} {'used':>6} {'conv':>6}")
    for id_ in ids:
        d = detected.get(id_, 0)
        u = used.get(id_, 0)
        print(f"  {id_:<25} {d:>9} {u:>6} {pct(u, d):>6}")
    print()


def print_top_skills(stats: dict, n: int = 10) -> None:
    used = [
        (k[len("skill-used/"):], v)
        for k, v in stats.items() if k.startswith("skill-used/")
    ]
    if not used:
        return

    used.sort(key=lambda x: -x[1])
    rule(f"TOP {min(n, len(used))} SKILLS (by usage)")
    for i, (id_, v) in enumerate(used[:n], 1):
        print(f"  {i:>2}. {id_:<30} {v:>4}")
    print()


def main() -> int:
    try:
        stats = fetch_stats()
    except Exception as e:
        print(f"error fetching {COUNTER_URL}/stats: {e}", file=sys.stderr)
        return 1

    if not stats:
        print("(no data yet)")
        return 0

    print()
    print_install_funnel(stats)
    print_per_service_funnel(
        stats, "add-key-started/", "add-key-completed/",
        "ADD-KEY FUNNEL (per service)",
    )
    print_discovery_funnel(stats)
    print_top_skills(stats)
    return 0


if __name__ == "__main__":
    sys.exit(main())
