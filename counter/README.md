# teleport counter

Anonymous event counter for teleport telemetry. Deployed on [Deno Deploy](https://deno.com/deploy) with Deno KV. Free tier: 1M requests/month, 13k writes/day — more than enough.

## What it stores

Counter entries keyed by `(event, subject)` in Deno KV. Nothing else. No IPs, no user IDs, no timestamps per event (only aggregate counts).

## API

- **`POST /count`** — body `{"event":"...","subject":"..."}` → increments that counter. Returns `ok`.
- **`GET /stats`** — returns every counter as flat map, e.g. `{"skill-used/github": 42, "install-completed": 128}`.
- **`GET /health`** — returns `ok` (smoke test).

## Events emitted by teleport

| Event | Subject (id) | Emitted from |
|-------|--------------|--------------|
| `install-started` | — | `setup/install.sh` (top) |
| `install-completed` | — | `setup/install.sh` (end) |
| `first-run` | — | `setup/teleport_setup.py` (once per install) |
| `migration` | — | `setup/teleport_setup.py` (after ≥1 MCP migrated) |
| `mcp-detected` | `<mcp-id>` | `setup/teleport_setup.py` (once per install per MCP) |
| `add-key-started` | `<service>` | `setup/teleport_setup.py` (start of add-key flow) |
| `add-key-completed` | `<service>` | `setup/teleport_setup.py` (credential saved) |
| `skill-used` | `<skill-id>` | `meta-skill/SKILL.md` (when Claude fetches a skill) |

All events honour `TELEPORT_NO_TELEMETRY=1` to opt out.

## Deploy

One-time setup:

```bash
# Install deployctl
deno install -Arf jsr:@deno/deployctl

# Login (opens browser)
deployctl login
```

Then from this directory:

```bash
deno task deploy
```

First deploy creates the project at `https://teleport-counter.<your-deno-username>.deno.dev`. Subsequent `deno task deploy` updates it.

## Local dev

```bash
deno task dev
```

Runs at `http://localhost:8000`. Uses a local KV file (`.kv.db` in this directory), not production.

Smoke test:

```bash
curl -X POST http://localhost:8000/count \
  -H "content-type: application/json" \
  -d '{"event":"install-completed"}'

curl http://localhost:8000/stats
```

## Ops notes

- No dashboard — query `/stats` directly or set up a CI job that pulls and renders.
- Data is append-only in practice. To reset a counter, SSH into Deno KV via the dashboard and delete the key.
- Rate limits: free tier handles well over 1000 req/min. No abuse protection in v0.1 — add one if public endpoint gets hammered.
