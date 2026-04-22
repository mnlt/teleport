# Teleport

Ephemeral skill execution for Claude Code. Use curated skills from community repos without permanent installation.

## Install

```bash
mkdir -p ~/.claude/skills/teleport && \
  curl -sL https://raw.githubusercontent.com/mnlt/teleport/main/meta-skill/SKILL.md \
  -o ~/.claude/skills/teleport/SKILL.md
```

## Use

Just ask Claude Code for something one of the catalog skills covers. The meta-skill consults the catalog, fetches the matching skill on-demand, and runs it from `/tmp/` — nothing persists to your skills directory.

Examples:
- "Create a PDF from these notes"
- "Make me a slide deck about X"
- "Generate an animated GIF for Slack"
- "Design a poster for Y"

## How it works

1. You install one meta-skill (this repo) — nothing else.
2. When you ask for something, Claude invokes `teleport`.
3. The meta-skill fetches `catalog.json`, picks the best-matching skill, downloads its `SKILL.md` to `/tmp/teleport/<id>/`.
4. As the skill references auxiliary files (scripts, templates, other markdown), they're fetched **on-demand**, only when needed.
5. Execution happens from `/tmp/`. When the session ends, the temp dir is gone.
6. If you love a specific skill and use it often, install it permanently:
   ```bash
   cp -r /tmp/teleport/<id>/ ~/.claude/skills/<id>/
   ```

## Catalog

See [catalog.json](./catalog.json). v0.1.0 ships with 10 skills from [`anthropics/skills`](https://github.com/anthropics/skills).

**Licenses:** each skill's license is governed by its upstream `source_repo`. Verify before redistribution or production use.

## Adding skills

1. Edit `catalog.json` to add an entry with `id`, `name`, `description`, `tags`, `source_repo`, `path`, `ref`.
2. Verify the referenced skill resolves via `curl https://raw.githubusercontent.com/<source_repo>/<ref>/<path>/SKILL.md`.
3. Open a PR.

## Status

**v0.1.0 — MVP.** Validating empirically whether the "ephemeral meta-skill + lazy fetch" pattern is viable in practice. See `TEST_LOG.md` for observations.

## Design notes

- **Lazy over eager:** the meta-skill fetches the minimum file set needed. Cheaper and simpler than cloning full folders.
- **Temp-only by default:** `~/.claude/skills/` stays clean. Permanent install is a single `cp` away for skills that earn their keep.
- **No runtime dependencies beyond `curl` + Claude Code's built-in tools.**

## Known caveats

- Skills whose internal structure references files by natural language (e.g. "use the templates") without explicit filenames may need clarification prompts during execution.
- Skills requiring Python packages, browsers, or system tools still need those installed locally — the meta-skill doesn't provision runtime dependencies.
- Minimum 2 network round-trips (catalog + SKILL.md) before work starts. Expect ~1-2s overhead.
