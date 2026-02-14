# PDCA — i18n-tools Maturity Roadmap

> Last updated: 2026-02-14

## Maturity snapshot

### Overall: 5/10 — "Functional core, broken packaging, no safety net"

| Dimension               | Score | Notes                                                            |
| ----------------------- | ----- | ---------------------------------------------------------------- |
| Architecture            | 8/10  | Clean modular design, clear separation of concerns               |
| Code Quality            | 6/10  | Decent but inconsistent type hints (~70%), some tight coupling   |
| Error Handling          | 4/10  | Generic catch-all in main, limited recovery strategies           |
| Testing                 | 1/10  | Zero tests despite pytest configured in pyproject.toml           |
| Documentation           | 7/10  | Good user docs, but 15+ stale refs after rename                  |
| CI/CD                   | 0/10  | No pipeline defined at all                                       |
| Input Validation        | 3/10  | Minimal; no schema validation, no duplicate-key checks           |
| Logging & Observability | 5/10  | Centralized logger with color support; gaps in conversion detail |
| Build & Release         | 4/10  | Hatch + uv scripts exist but entry point and packages are broken |
| Configuration           | 7/10  | Flexible three-tier config (env / default yaml / custom yaml)    |

### Strengths

- Registry pattern for CLI tools, singleton config, strategy pattern for locale styles.
- Comprehensive user docs (README, Installation, j2e, e2j, AGENT).
- Modern build tooling (hatchling, uv, commitizen).

### Critical gaps (blocking stable release)

1. **Build is broken** — `pyproject.toml` entry point and packages still reference `i18n` after rename to `i18n_tools`.
2. **run_i18n is broken** — Script invokes `python -m i18n` instead of `python -m i18n_tools`.
3. **Version drift** — `__init__.py` says `0.0.4`, `pyproject.toml` says `0.1.0`, actual is `0.0.1`.
4. **15+ stale doc references** — AGENT.md, README.md, Installation.md still use old paths/commands.
5. **Zero tests** — No safety net for any changes.
6. **No CI** — No automated quality gate.
7. **Generic error handling** — Single `except Exception` in `shared.py`.
8. **No input validation** — No schema checks, no duplicate-key detection.

### Risk profile

| Risk                    | Severity | Likelihood | Mitigation                             |
| ----------------------- | -------- | ---------- | -------------------------------------- |
| Data loss on conversion | High     | Medium     | Round-trip tests, input validation     |
| Silent corruption       | High     | Medium     | Schema checks, duplicate-key detection |
| Regression              | High     | High       | Test suite + CI                        |
| Install failure         | High     | Certain    | Fix pyproject.toml (Cycle 0 / v0.1.0)  |
| Config confusion        | Medium   | Medium     | Align docs, add `--config` flag        |

---

## Version roadmap

```text
v0.0.1 (now)    v0.1.0          v0.2.0          v0.3.0          v1.0.0
  │               │               │               │               │
  ▼               ▼               ▼               ▼               ▼
┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐
│ Current │──▶│ Cycle 0 │──▶│ Cycle 1 │──▶│ Cycle 2 │──▶│ Cycle 3 │
│  State  │   │ Fix &   │   │ Test &  │   │ Harden  │   │ Stable  │
│         │   │ Ship    │   │ Gate    │   │         │   │ Release │
└─────────┘   └─────────┘   └─────────┘   └─────────┘   └─────────┘
                                                          ─ ─ ─ ─ ─
                                                         │ Cycle 4  │
                                                         │ GUI      │
                                                          ─ ─ ─ ─ ─
                                                          (post 1.0)
```

---

## Cycle 0 — Fix & Ship → v0.1.0 (current)

> **Theme**: Make the project build, install, and run correctly after the rename.

### Plan

The `i18n` → `i18n_tools` rename left the code correct but the build config, runner script,
and documentation broken. Nothing else can proceed until the project is installable and runnable.

Key references:

- Entry point config: [pyproject.toml](pyproject.toml) line 50
- Packages config: [pyproject.toml](pyproject.toml) line 53
- Runner script: [run_i18n](run_i18n)
- Version sync: [scripts/update_app_version.sh](scripts/update_app_version.sh)

### Do

| #  | Task                                                           | Status  |
| -- | -------------------------------------------------------------- | ------- |
| 1  | Fix pyproject.toml entry point module path                     | Pending |
| 2  | Fix pyproject.toml packages to ["src/i18n_tools"]              | Pending |
| 3  | Fix run_i18n to use python -m i18n_tools                       | Pending |
| 4  | Run update_app_version.sh to sync version to 0.1.0             | Pending |
| 5  | Fix AGENT.md (8 path refs + 2 CLI commands)                    | Pending |
| 6  | Fix README.md (1 path ref + 4 CLI commands)                    | Pending |
| 7  | Fix Installation.md (1 CLI command + 1 error message ref)      | Pending |
| 8  | Fix scripts/update_app_version.sh path to src/i18n_tools/      | Pending |
| 9  | Verify hatch build produces a valid wheel                      | Pending |
| 10 | Verify python -m i18n_tools j2e -h and e2j -h run              | Pending |
| 11 | Make initial git commit                                        | Pending |

### Check

- `hatch build` succeeds and produces `dist/i18n_tools-0.1.0-py3-none-any.whl`.
- `pip install dist/*.whl && i18n_tools -v` prints `0.1.0`.
- `python -m i18n_tools j2e` and `e2j` run without `ModuleNotFoundError`.
- `grep -r "src/i18n/" docs/ AGENT.md README.md Installation.md` returns zero matches.
- All files committed on `main`.

### Act

- Document any remaining rename issues discovered during verification.
- Update CHANGELOG.md with v0.1.0 release notes.

---

## Cycle 1 — Test & Gate → v0.2.0

> **Theme**: Add a test suite and CI so changes can be made safely.

### Work items

| #  | Task                                                          | Status  |
| -- | ------------------------------------------------------------- | ------- |
| 1  | Create fixture data for `per-namespace` layout                | Pending |
| 2  | Create fixture data for `per-locale` layout                   | Pending |
| 3  | Unit tests: key flattening (`json_wrapper.py`)                | Pending |
| 4  | Unit tests: key reconstruction (`excel_wrapper.py`)           | Pending |
| 5  | Unit tests: config loading and precedence (`shared.py`)       | Pending |
| 6  | Integration test: j2e round-trip (per-namespace)              | Pending |
| 7  | Integration test: j2e round-trip (per-locale)                 | Pending |
| 8  | Integration test: e2j round-trip (per-namespace)              | Pending |
| 9  | Integration test: e2j round-trip (per-locale)                 | Pending |
| 10 | Edge-case tests: empty cells, missing locales, duplicate keys | Pending |
| 11 | Add GitHub Actions CI (`pytest` on Python 3.10 + 3.11)        | Pending |
| 12 | Add coverage reporting to CI                                  | Pending |

### Gate (v0.2.0)

- `pytest` passes on a clean environment.
- CI green on Python 3.10 and 3.11.
- Coverage > 60% for `core/` and `apps/`.
- Both locale styles verified via round-trip with no data loss.

---

## Cycle 2 — Harden → v0.3.0

> **Theme**: Make the tool robust — better errors, validation, and developer tooling.

### Backlog

| #  | Task                                                                     | Status  |
| -- | ------------------------------------------------------------------------ | ------- |
| 1  | Replace generic `except Exception` in `shared.py` with specific handlers | Pending |
| 2  | Add JSON schema validation before conversion                             | Pending |
| 3  | Add duplicate-key detection in flattened output                          | Pending |
| 4  | Implement round-trip integrity verification (hash comparison)            | Pending |
| 5  | Add `--config <path>` CLI flag                                           | Pending |
| 6  | Add `--dry-run` CLI flag (preview file operations)                       | Pending |
| 7  | Add `--verbose` CLI flag                                                 | Pending |
| 8  | Pre-commit hooks: `ruff check` + `ruff format`                          | Pending |
| 9  | Type hints audit and completion (target 100%)                            | Pending |
| 10 | Progress indicators (tqdm) for large conversions                         | Pending |
| 11 | Tests for all new features                                               | Pending |

### Gate (v0.3.0)

- `ruff check` and `ruff format --check` pass with zero findings.
- `--dry-run` outputs planned operations without modifying files.
- Round-trip hash matches for all fixture datasets.
- Coverage > 80% for `core/` and `apps/`.
- All new CLI flags documented in README and `--help`.

---

## Cycle 3 — Stable Release → v1.0.0

> **Theme**: Ship a production-ready v1.0.0 with structured output and a public API.

### Scope

| #  | Task                                                                       | Status  |
| -- | -------------------------------------------------------------------------- | ------- |
| 1  | Add `--output-format json` for machine-readable CLI output                 | Pending |
| 2  | Expose conversion functions as a public Python API with clean return types | Pending |
| 3  | Add `--include` / `--exclude` flags for namespace and language filtering   | Pending |
| 4  | Report generation: summary stats, missing translations, change diffs       | Pending |
| 5  | Complete API reference documentation                                       | Pending |
| 6  | Automated release workflow (GitHub Actions + `release.sh`)                 | Pending |
| 7  | Publish to PyPI (or internal registry)                                     | Pending |
| 8  | Performance profiling and optimisation for large datasets                  | Pending |
| 9  | Dockerfile for containerised usage (optional)                              | Pending |
| 10 | Tests for all new features                                                 | Pending |

### Gate (v1.0.0)

- CLI can produce JSON output consumable by external tools.
- Public API functions are importable and documented.
- v1.0.0 tag created with full changelog.
- Published to package registry.

---

## Cycle 4 — Desktop GUI (post-v1.0.0)

> **Theme**: Wrap the CLI in a lightweight desktop app for non-technical users.
> **Note**: This cycle is scoped beyond v1.0.0. Version TBD after stable release.

### Stack

Tauri v2 + React + Vite + TypeScript. Python CLI reused 100% via subprocess.

### Architecture

```text
React Frontend (file picker, table views, workflow UI)
    ↓ Tauri Commands (IPC)
Rust Layer (thin glue, generated with Claude Code)
    ↓ Subprocess
Python CLI (existing i18n_tools package)
```

### Deliverables

| #  | Task                                                      | Status  |
| -- | --------------------------------------------------------- | ------- |
| 1  | Scaffold Tauri + React + Vite project (`gui/`)            | Pending |
| 2  | Rust commands for j2e/e2j subprocess invocation            | Pending |
| 3  | File/directory picker UI for input/output paths            | Pending |
| 4  | Config editor panel (locale style, paths, options)         | Pending |
| 5  | Translation table view (editable, per-namespace tabs)      | Pending |
| 6  | Workflow buttons: Convert, Preview (dry-run), Import       | Pending |
| 7  | Error display and progress indicators                      | Pending |
| 8  | Desktop packaging (`.msi` / `.deb` / `.dmg`)              | Pending |

### Prerequisites from earlier cycles

- **Cycle 1**: Tests + CI (stable foundation).
- **Cycle 2**: CLI flags (`--config`, `--dry-run`) for GUI to invoke.
- **Cycle 3**: Structured JSON output mode (`--output-format json`) + public API.

### Gate

- App launches and connects to Python CLI backend.
- Full round-trip workflow (j2e then e2j) works through the GUI.
- App bundle < 15MB (excluding Python runtime).
- Works on Windows and Linux (macOS as stretch goal).
