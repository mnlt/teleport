#!/usr/bin/env python3
"""UX demo: create a test state that exercises ALL teleport-setup flows.

Injects synthetic MCPs covering every plan status:

  ready to migrate   (creds in MCP env, env var NOT set in settings)
    - slack          (SLACK_BOT_TOKEN)
    - linear         (LINEAR_API_KEY)

  needs setup        (MCP installed but no creds locally)
    - notion         (empty env block — simulates OAuth/hosted install)
    - figma          (empty env block)

  already on teleport (env var already present in settings)
    - github         (if user already has GITHUB_TOKEN in env — likely true)

  unsupported        (not in teleport's knowledge base)
    - my-weather-bot

Cleans stale fake tokens from prior demo runs so scenarios reset fresh each time.
Pair with _uxdemo-cleanup.py to restore.
"""
import json, shutil
from pathlib import Path

H = Path.home()
CC = H / ".claude.json"
SL = H / ".claude" / "settings.local.json"
BAK_CC = H / ".claude.json.uxdemo"
BAK_SL = H / ".claude" / "settings.local.json.uxdemo"

if BAK_CC.exists() or BAK_SL.exists():
    print(f"⚠  existing uxdemo backup found — run _uxdemo-cleanup.py first")
    raise SystemExit(1)

# Back up BEFORE modifying
shutil.copy2(CC, BAK_CC)
if SL.exists():
    shutil.copy2(SL, BAK_SL)
print(f"✓ backed up → {BAK_CC.name} + {BAK_SL.name if SL.exists() else '(no settings.local)'}")

# Strip stale fake tokens from settings (so scenarios show MIGRATE, not DONE, on re-run)
FAKE_PREFIXES = {
    "SLACK_BOT_TOKEN":   "xoxb-fake-demo",
    "NOTION_API_KEY":    "secret_fake-notion",
    "LINEAR_API_KEY":    "lin_api_fake-linear",
    "FIGMA_ACCESS_TOKEN":"figd_fake-figma",
}
if SL.exists():
    with open(SL) as f:
        sl_data = json.load(f)
    env = sl_data.get("env", {})
    cleaned = []
    for var, prefix in FAKE_PREFIXES.items():
        if var in env and isinstance(env[var], str) and env[var].startswith(prefix):
            del env[var]
            cleaned.append(var)
    if cleaned:
        with open(SL, "w") as f:
            json.dump(sl_data, f, indent=2)
        print(f"  cleaned stale fake tokens: {', '.join(cleaned)}")

# Inject MCPs
with open(CC) as f:
    d = json.load(f)
proj = d.setdefault("projects", {}).setdefault(str(H), {})
mcps = proj.setdefault("mcpServers", {})

# READY — creds present in MCP env block, env var NOT set in settings
mcps["slack"] = {
    "type": "stdio",
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-slack"],
    "env": {"SLACK_BOT_TOKEN": "xoxb-fake-demo-1234567890"},
}
mcps["linear"] = {
    "type": "stdio",
    "command": "npx",
    "args": ["-y", "@linear/mcp"],
    "env": {"LINEAR_API_KEY": "lin_api_fake-linear-xyz789"},
}

# NEEDS SETUP — MCP installed but no creds locally (simulates OAuth/hosted install)
mcps["notion"] = {
    "type": "http",
    "url": "https://mcp.notion.com/mcp",
    "env": {},  # empty — hosted OAuth, token in Claude Code cache we can't read
}
mcps["figma"] = {
    "type": "stdio",
    "command": "npx",
    "args": ["-y", "figma-developer-mcp"],
    "env": {},  # empty — user forgot to pass --env
}

# UNSUPPORTED — not in teleport's knowledge base
mcps["my-weather-bot"] = {
    "type": "stdio",
    "command": "npx",
    "args": ["-y", "@someone/weather-mcp"],
    "env": {"WEATHER_API_KEY": "fake-weather"},
}

# (github may appear as "already on teleport" if user has GITHUB_TOKEN in env from earlier migrations — that's fine, it demos that state too)

with open(CC, "w") as f:
    json.dump(d, f, indent=2)

print()
print("✓ injected demo MCPs:")
print("   slack, linear         → ready to migrate   (y → migrate + disable)")
print("   notion, figma         → needs setup        (y → carousel for add-key)")
print("   my-weather-bot        → unsupported        (info only)")
print()
print("now try:")
print("  teleport-setup                    # interactive flow")
print("  teleport-setup --scan             # preview only")
print()
print("cleanup when done:")
print("  python3 ~/teleport/setup/_uxdemo-cleanup.py")
