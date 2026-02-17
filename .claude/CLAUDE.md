# CLAUDE.md — Project Instructions for Claude Code

> **Shared knowledge base**: [AGENTS.md](../AGENTS.md) defines pair
> programming workflows, decision frameworks, and the `.agents/`
> directory structure. Load it first for full context before starting
> any task.

## Project overview

Monorepo for **i18n-tools**: a toolkit that converts i18n JSON files to Excel and back.

| Directory | Purpose | Tech |
| --------- | ------- | ---- |
| `core/` | Python CLI (runs independently) | Python 3.10+, hatchling, polars |
| `gui/` | Desktop GUI wrapper (planned, post-v1.0.0) | Tauri v2 + React + Vite + TS |

## Key files

- `AGENT.md` — quick orientation, project layout, and file map
- `docs/plan/PDCA.md` — maturity roadmap, current cycle tasks, and version gates
- `core/pyproject.toml` — build config, dependencies, tool settings
- `core/src/i18n_tools/` — main source package

## Working in `core/`

### Run

```sh
cd core
python -m i18n_tools j2e   # JSON -> Excel
python -m i18n_tools e2j   # Excel -> JSON
```

### Build

```sh
cd core && hatch build
```

### Test

```sh
cd core && pytest
```

### Lint

```sh
cd core && ruff check src/ && ruff format --check src/
```

## Rules

- **Package name is `i18n_tools`** (not `i18n`). The rename from `i18n` to `i18n_tools` is complete in source but some configs/docs still have stale references — see PDCA.md Cycle 0.
- **`core/` must remain independently runnable** without the GUI. Do not introduce cross-dependencies.
- **Keep CLI commands backward compatible**: `j2e` and `e2j` are the stable subcommands.
- **JSON encoding must stay `utf-8`**. Never change the encoding contract.
- **Do not commit `.env` files** or any secrets. Use `.env.sample` as the template.
- **Follow existing patterns**: singleton config (`@simple_singleton`), registry pattern (`@register_as_tool`), strategy pattern for locale styles.
- **Python style**: ruff with line-length 120. See `core/pyproject.toml` `[tool.ruff]` for full config.
- **Commits**: use conventional commits (commitizen is configured). Format: `type(scope): description`.

## Current state

The project is at **Cycle 0 (v0.1.0)** — fixing build/packaging after the `i18n` -> `i18n_tools` rename. Key blockers:

1. `core/pyproject.toml` entry point and packages still reference `i18n`
2. `core/run_i18n` script uses old module name
3. Version drift between `__init__.py` and `pyproject.toml`
4. Stale doc references in `core/README.md` and `core/Installation.md`

Consult `docs/plan/PDCA.md` for the full task list and next cycles.

## Architecture notes

- **Config precedence**: `.env` < `default.yaml` < custom YAML via `CONFIG_FILE`
- **Locale styles**: `per-namespace` (`namespace/locale.json`) and `per-locale` (`locale/namespace.json`)
- **CLI dispatch**: `adapters/cli/app.py` uses a registry pattern — apps register via `@register_as_tool`
- **Data flow**: JSON files -> polars DataFrame -> Excel (j2e) and reverse (e2j)
