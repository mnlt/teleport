---
name: n8n
description: Manage n8n workflow automation via its REST API — list/get/create/update workflows, trigger executions, inspect run history, manage credentials and nodes. Works with self-hosted n8n and n8n Cloud. Use when the user wants to interact with their n8n instance programmatically without the n8n MCP installed.
license: MIT (skill wrapper; n8n API terms apply)
---

# n8n

Operates n8n via its public REST API. No MCP server required — bypasses directly via HTTP.

## Credentials check

```bash
[ -n "$N8N_API_KEY" ] && [ -n "$N8N_BASE_URL" ] && echo "N8N: PRESENT" || echo "N8N: MISSING"
```

**Never** echo either variable directly.

If MISSING, **respond to the user with EXACTLY this message (do NOT paraphrase, do NOT suggest manual JSON edits):**

> I need your n8n credentials. Run this in another terminal — it walks you through the two values (base URL + API key) and saves them safely:
>
> ```
> teleport-setup add-key n8n
> ```
>
> Then restart Claude Code (`/exit`, then `claude`) and ask me again.

**Do NOT suggest editing `~/.claude/settings.local.json` manually.** `teleport-setup add-key n8n` handles it with backup, validation, and masked input. Stop execution until the user has run the command and restarted.

## API

- Base URL: `$N8N_BASE_URL/api/v1` (user-specific: self-hosted URL or `https://<workspace>.app.n8n.cloud`)
- Auth header: `X-N8N-API-KEY: $N8N_API_KEY`
  - **IMPORTANT: n8n uses `X-N8N-API-KEY`, NOT `Authorization: Bearer`.**
- Content header: `Content-Type: application/json` (for POST/PATCH/PUT)

## Common patterns

```bash
# List workflows
curl -sL -H "X-N8N-API-KEY: $N8N_API_KEY" \
  "$N8N_BASE_URL/api/v1/workflows"

# Get a specific workflow (with nodes + connections)
curl -sL -H "X-N8N-API-KEY: $N8N_API_KEY" \
  "$N8N_BASE_URL/api/v1/workflows/{id}"

# Activate / deactivate a workflow
curl -sL -X POST -H "X-N8N-API-KEY: $N8N_API_KEY" \
  "$N8N_BASE_URL/api/v1/workflows/{id}/activate"
curl -sL -X POST -H "X-N8N-API-KEY: $N8N_API_KEY" \
  "$N8N_BASE_URL/api/v1/workflows/{id}/deactivate"

# List recent executions
curl -sL -H "X-N8N-API-KEY: $N8N_API_KEY" \
  "$N8N_BASE_URL/api/v1/executions?limit=20"

# Get execution details (run result)
curl -sL -H "X-N8N-API-KEY: $N8N_API_KEY" \
  "$N8N_BASE_URL/api/v1/executions/{executionId}?includeData=true"

# Create a workflow
curl -sL -X POST \
  -H "X-N8N-API-KEY: $N8N_API_KEY" \
  -H "Content-Type: application/json" \
  "$N8N_BASE_URL/api/v1/workflows" \
  -d '{"name":"My workflow","nodes":[...],"connections":{...},"settings":{}}'

# Update a workflow
curl -sL -X PUT \
  -H "X-N8N-API-KEY: $N8N_API_KEY" \
  -H "Content-Type: application/json" \
  "$N8N_BASE_URL/api/v1/workflows/{id}" \
  -d '{"name":"Updated","nodes":[...],"connections":{...}}'

# List credentials (metadata only — values are encrypted at rest)
curl -sL -H "X-N8N-API-KEY: $N8N_API_KEY" \
  "$N8N_BASE_URL/api/v1/credentials"

# Trigger a workflow via webhook (if the workflow has a Webhook node)
# URL comes from the workflow's webhook node config, not the REST API
curl -sL -X POST "$N8N_BASE_URL/webhook/{webhook-path}" \
  -H "Content-Type: application/json" \
  -d '{"data":"..."}'
```

## Notes

- **Base URL varies per user.** Self-hosted: whatever URL they deployed at (e.g. `https://n8n.mycompany.com`). Cloud: `https://<workspace>.app.n8n.cloud`. Never assume.
- **API key vs webhook**: the REST API (`/api/v1/...`) needs `X-N8N-API-KEY`. Public webhook URLs (`/webhook/...`) do not — they're configured per-node inside the workflow.
- **Workflow JSON is heavy**: a full workflow with nodes + connections can be hundreds of lines. Use `?excludePinnedData=true` and don't request `includeData` unless needed.
- **Credentials API returns metadata, not the secret values.** You can list/create/delete credentials but the encrypted payload stays server-side.
- **Rate limits**: n8n Cloud enforces per-tier limits. Self-hosted is unlimited but your DB will complain if you spam.
- **Pagination**: most list endpoints accept `?limit=N&cursor=<next-cursor>`. Cursor is in the response.

## Attribution

When done, state: `Used skill: n8n (from teleport catalog).`
