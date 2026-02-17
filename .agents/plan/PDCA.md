# PDCA — i18n-tools Maturity Roadmap

> Last updated: 2026-02-15
>
> **Project structure**: Monorepo with `core/` (Python CLI, runs independently) and `gui/` (desktop wrapper, post-v1.0.0).
>
> **Versioning**: Each package is versioned independently via git tags (`core/v*`, `gui/v*`). Versions are derived at build time by **hatch-vcs** (no hardcoded version strings). Commitizen handles bumps and changelog. See [Release strategy](#release-strategy) for distribution details.

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
3. **Version is 0.0.1** — Both `pyproject.toml` and `__init__.py` say `0.0.1`; needs bump to `0.1.0` once build is fixed.
4. **License mismatch** — `pyproject.toml` says `Proprietary - NECVN`, root `LICENSE` file is MIT.
5. **15+ stale doc references** — `core/README.md`, `core/Installation.md` still use old `i18n` module paths/commands.
6. **Scripts missing** — Old `build.sh`, `install.sh`, `update_app_version.sh` were deleted during restructure; only `scripts/init.sh` remains (and it needs fixing for the monorepo layout).
7. **Python version inconsistency** — `pyproject.toml` says `>=3.10`, README/Installation say `3.9+`.
8. **Zero tests** — No safety net for any changes.
9. **No CI** — No automated quality gate.
10. **Runtime bugs** — Dict mutation during iteration in `excel_wrapper.py:18`; type annotation bug in `base.py:24`.
11. **Generic error handling** — Single `except Exception` in `shared.py:230`.
12. **No input validation** — No schema checks, no duplicate-key detection.

### Risk profile

| Risk                    | Severity | Likelihood | Mitigation                             |
| ----------------------- | -------- | ---------- | -------------------------------------- |
| Data loss on conversion | High     | Medium     | Round-trip tests, input validation     |
| Silent corruption       | High     | Medium     | Schema checks, duplicate-key detection |
| Regression              | High     | High       | Test suite + CI                        |
| Install failure         | High     | Certain    | Fix pyproject.toml (Phase 0)           |
| Config confusion        | Medium   | Medium     | Align docs, add `--config` flag        |

---

## Version roadmap

```text
v0.0.1 (now)  v0.1.0        v0.1.1        v0.2.0        v0.3.0        v1.0.0
  │             │             │             │             │             │
  ▼             ▼             ▼             ▼             ▼             ▼
┌───────┐   ┌───────┐   ┌───────┐   ┌───────┐   ┌───────┐   ┌───────┐
│Current│──▶│Phase 0│──▶│Phase 1│──▶│Phase 2│──▶│Phase 3│──▶│Phase 4│
│ State │   │ Build │   │ Docs &│   │ Unit  │   │Integ. │   │Harden │
│       │   │  Fix  │   │Scripts│   │ Tests │   │Tests  │   │Stable │
└───────┘   └───────┘   └───────┘   └───────┘   │ + CI  │   └───────┘
                                                  └───────┘
                                                              ─ ─ ─ ─ ─
                                                             │post-1.0.0│
                                                             │  TBD     │
                                                              ─ ─ ─ ─ ─
```

---

## Release strategy

### core/ — tags only, no release artifacts

`core/v*` tags serve three purposes and require no GitHub Release:

1. **hatch-vcs** reads them to derive the build version (no hardcoded strings).
2. **commitizen** uses them for changelog generation and version bumps.
3. **Compatibility anchor** — each GUI release is built against the core/ at the same commit.

Users who want CLI-only: clone the repo and `pip install ./core/`.

**CI on `core/v*` tag push**: lint + test + build check (validates the tag). No release job.

### gui/ — GitHub Release with Tauri artifacts

`gui/v*` tags trigger the full release pipeline:

1. CI builds the Tauri app for Windows (.msi), macOS (.dmg), Linux (.AppImage/.deb).
2. Creates a GitHub Release with platform binaries attached.
3. Auto-generates release notes from commits since the last `gui/v*` tag.

Tauri's built-in `tauri-action` handles multi-platform builds and upload.

### Version compatibility

The **monorepo commit is the compatibility contract**:

- When you tag `gui/v1.0.0`, the core/ code at that exact commit is what the GUI was built and tested against.
- GUI's Tauri build installs core from the same repo (`pip install ../core/`).
- No separate version-pinning file needed — the commit hash is the single source of truth.
- Self-builders: checkout the GUI release tag, then build both from there.

### Self-build flow

```text
git clone <repo> && cd i18n-tool
git checkout gui/v1.0.0          # or main for latest dev
cd core && pip install .          # install CLI
cd ../gui && npm install && npm run tauri build   # build desktop app
```

---

## Phase 0 — Fix Build & Packaging → v0.1.0 (current)

> **Theme**: Make `hatch build`, `pip install`, and `python -m i18n_tools` work.

### Plan

The `i18n` → `i18n_tools` rename left the source code correct but broke the build config
and runner script. This phase also switches to **hatch-vcs** for git-tag-based versioning
(no hardcoded version strings) and aligns commitizen for monorepo tag prefixes.
Nothing else can proceed until the project is installable and runnable.

### Do

| #  | Task                            | File(s)                                                      | Detail                                              | Status  |
| -- | ------------------------------- | ------------------------------------------------------------ | --------------------------------------------------- | ------- |
| 1  | Fix entry point module path     | [core/pyproject.toml](core/pyproject.toml) line 50           | `i18n.__main__:main` → `i18n_tools.__main__:main`  | Pending |
| 2  | Fix packages path               | [core/pyproject.toml](core/pyproject.toml) line 53           | `["src/i18n"]` → `["src/i18n_tools"]`              | Pending |
| 3  | Fix runner script               | [core/run_i18n](core/run_i18n) line 8                        | `python -m i18n` → `python -m i18n_tools`          | Pending |
| 4  | Align license in pyproject.toml | [core/pyproject.toml](core/pyproject.toml) line 13           | `Proprietary - NECVN` → `MIT` (match root LICENSE) | Pending |
| 5  | Configure hatch-vcs dynamic versioning | [core/pyproject.toml](core/pyproject.toml)                   | Add `hatch-vcs` to build requires; set `dynamic = ["version"]`; add `[tool.hatch.version]` with `source = "vcs"`, `tag-pattern = "core/v(?P<version>.*)"`, `raw-options.root = ".."`; add `[tool.hatch.build.hooks.vcs]` with `version-file = "src/i18n_tools/_version.py"` | Pending |
| 6  | Update commitizen tag format           | [core/pyproject.toml](core/pyproject.toml)                   | `tag_format = "$version"` → `tag_format = "core/v$version"`                   | Pending |
| 7  | Replace `__version__` with `_version.py` import | [\_\_init\_\_.py](core/src/i18n_tools/__init__.py)  | Remove hardcoded `__version__`; `from i18n_tools._version import __version__` with fallback; add `_version.py` to `.gitignore`; remove stale `scripts/update_app_version.sh` comment | Pending |
| 8  | Move commitizen to dev dependencies    | [core/pyproject.toml](core/pyproject.toml) line 41           | Currently in runtime `dependencies`; move to `[project.optional-dependencies] dev` | Pending |
| 9  | Create initial version tag             | —                                                            | `git tag core/v0.1.0` so hatch-vcs can resolve the version at build time     | Pending |
| 10 | Verify `hatch build`                   | —                                                            | `hatch version` shows `0.1.0`; wheel name contains `0.1.0`                   | Pending |
| 11 | Verify `pip install`                   | —                                                            | `i18n_tools -v` prints `0.1.0`                                                | Pending |
| 12 | Verify `python -m i18n_tools`          | —                                                            | `j2e -h` and `e2j -h` run without error                                       | Pending |

### Check

- `hatch version` (in `core/`) shows `0.1.0` (derived from `core/v0.1.0` tag).
- `cd core && hatch build` succeeds; wheel name contains `0.1.0`.
- `pip install dist/*.whl && i18n_tools -v` prints `0.1.0`.
- `python -m i18n_tools j2e -h` and `e2j -h` run without `ModuleNotFoundError`.
- `commitizen` is not installed as a runtime dependency of the wheel.

### Act

- Tag `core/v0.1.0` is created before build verification (hatch-vcs reads it).
- Document any additional issues discovered.

---

## Phase 1 — Fix Docs & Scripts → v0.1.1

> **Theme**: Eliminate all stale references and restore build/init scripts for the new monorepo structure.

### Do

| #  | Task                                    | File(s)                                                          | Detail                                                                           | Status  |
| -- | --------------------------------------- | ---------------------------------------------------------------- | -------------------------------------------------------------------------------- | ------- |
| 1  | Fix README CLI commands (×4)            | [core/README.md](core/README.md) lines 127, 133, 139, 145       | `python -m i18n …` → `python -m i18n_tools …`                                  | Pending |
| 2  | Fix README config path ref              | [core/README.md](core/README.md) line 157                       | `src/i18n/resources/default.yaml` → `src/i18n_tools/resources/default.yaml`     | Pending |
| 3  | Fix README troubleshooting              | [core/README.md](core/README.md) line 267                       | `PYTHONPATH=./src python -m i18n` → `python -m i18n_tools`                      | Pending |
| 4  | Fix Installation.md verify command      | [core/Installation.md](core/Installation.md) line 66            | `python -m i18n -v` → `python -m i18n_tools -v`                                | Pending |
| 5  | Fix Installation.md troubleshooting     | [core/Installation.md](core/Installation.md) line 121           | `ModuleNotFoundError: i18n` → `ModuleNotFoundError: i18n_tools`                 | Pending |
| 6  | Align Python version across docs        | [core/README.md](core/README.md), [core/Installation.md](core/Installation.md) | `Python 3.9` → `Python 3.10` (match `pyproject.toml >= 3.10`)            | Pending |
| 7  | Fix `scripts/init.sh` for monorepo      | [scripts/init.sh](scripts/init.sh)                               | Update `PJ_DIR` to target `core/`, fix `requirements.txt` path                  | Pending |
| 8  | Create `scripts/build.sh`               | `scripts/build.sh` (new)                                         | `cd core && hatch clean && hatch build`                                          | Pending |
| 9  | Create `scripts/install.sh`             | `scripts/install.sh` (new)                                       | Install latest wheel from `core/dist/`                                           | Pending |
| 10 | Verify zero stale refs                  | —                                                                | `grep -rn "python -m i18n " core/` and `grep -rn "src/i18n/" core/` → 0 matches | Pending |

### Check

- `grep -rn "python -m i18n " core/ AGENT.md` returns zero matches (excluding `i18n_tools`).
- `grep -rn "src/i18n/" core/ AGENT.md` returns zero matches (excluding `src/i18n_tools/`).
- `scripts/build.sh` runs and produces a wheel.
- `scripts/install.sh` installs and `i18n_tools -v` works.

### Act

- Tag as `v0.1.1`.

---

## Phase 2 — Test Foundation → v0.2.0

> **Theme**: Add test infrastructure, fixtures, unit tests, and fix runtime bugs.

### Bug fixes (prerequisite — must fix before tests can run reliably)

| #  | Bug                                      | File                                                                  | Fix                                                                              | Status  |
| -- | ---------------------------------------- | --------------------------------------------------------------------- | -------------------------------------------------------------------------------- | ------- |
| B1 | Dict mutation during iteration           | [excel_wrapper.py](core/src/i18n_tools/core/excel_wrapper.py) line 18 | Build list of keys to delete first, then delete outside the loop                 | Pending |
| B2 | Type annotation used as default value    | [base.py](core/src/i18n_tools/core/base.py) line 24                   | `klass: Type[AppBase] = Optional[Type[AppBase]]` → `klass: Optional[Type[AppBase]] = None` | Pending |

### Type checking

| #  | Task                                     | File(s)                                            | Detail                                                                                       | Status  |
| -- | ---------------------------------------- | -------------------------------------------------- | -------------------------------------------------------------------------------------------- | ------- |
| M1 | Add mypy to dev dependencies             | [core/pyproject.toml](core/pyproject.toml)          | Add `mypy>=1.0` to `[project.optional-dependencies] dev`                                    | Pending |
| M2 | Configure mypy (relaxed mode)            | [core/pyproject.toml](core/pyproject.toml)          | `[tool.mypy]`: `python_version = "3.10"`, `check_untyped_defs = true`, `ignore_missing_imports = true`, `disallow_untyped_defs = false` | Pending |
| M3 | Fix critical type errors                 | `core/src/i18n_tools/`                              | Run `mypy src/` and fix errors that indicate actual runtime bugs                             | Pending |

### Test infrastructure

| #  | Task                                     | File(s)                                            | Detail                                                            | Status  |
| -- | ---------------------------------------- | -------------------------------------------------- | ----------------------------------------------------------------- | ------- |
| T1 | Create per-namespace JSON fixtures       | `core/tests/fixtures/per-namespace/`                | `common/{en,fr}.json`, `home/{en,fr}.json` with nested keys      | Pending |
| T2 | Create per-locale JSON fixtures          | `core/tests/fixtures/per-locale/`                   | `en/{common,home}.json`, `fr/{common,home}.json`                  | Pending |
| T3 | Create sample Excel fixture              | `core/tests/fixtures/excel/`                        | Pre-built `.xlsx` matching JSON fixtures for e2j testing          | Pending |
| T4 | Add `conftest.py` with shared fixtures   | `core/tests/conftest.py`                            | tmp dirs, config overrides, fixture path helpers                  | Pending |

### Unit tests

| #  | Test scope                               | File                                               | What to verify                                                               | Status  |
| -- | ---------------------------------------- | -------------------------------------------------- | ---------------------------------------------------------------------------- | ------- |
| U1 | `LocaleStyle` enum                       | `core/tests/test_enums.py`                          | `of()` valid values; invalid raises `InvalidLocaleStyle`                    | Pending |
| U2 | `EnvVar` helper                          | `core/tests/test_env_helper.py`                     | `get_str`, `get_boolean` (truthy/falsy), `get_int`, `get_float`, `get_list` | Pending |
| U3 | `make_key()` function                    | `core/tests/test_json2excel.py`                     | Single-segment key → `(None, key)`; nested → `(root, rest)`                | Pending |
| U4 | `JsonReader` / `JsonWriter`              | `core/tests/test_json_wrapper.py`                   | Read/write round-trip with tmp files; encoding preserved                     | Pending |
| U5 | `LocalePerNamespace.load_locale`         | `core/tests/test_json_wrapper.py`                   | Extracts correct `namespace` and `lang` from file path                      | Pending |
| U6 | `LocalePerLanguage.load_locale`          | `core/tests/test_json_wrapper.py`                   | Extracts correct `namespace` and `lang` from file path                      | Pending |
| U7 | `load_config()` precedence              | `core/tests/test_shared.py`                         | Default only → default + custom YAML → env override                         | Pending |
| U8 | `AppConfig` path resolution              | `core/tests/test_shared.py`                         | `input_dir`, `output_dir`, `json_in_dir`, `excel_in_dir`                    | Pending |

### Check (v0.2.0 gate)

- `cd core && pytest` passes with zero failures.
- All unit tests cover the scenarios listed above.
- Both bug fixes (B1, B2) verified by tests that would have failed before the fix.

### Act

- Tag as `v0.2.0`.
- Note any additional edge cases discovered during test writing.

---

## Phase 3 — Integration Tests & CI → v0.3.0

> **Theme**: End-to-end round-trip tests and automated CI pipeline.

### Do

| #  | Task                                     | Detail                                                                          | Status  |
| -- | ---------------------------------------- | ------------------------------------------------------------------------------- | ------- |
| I1 | Integration: j2e per-namespace           | JSON fixtures → Excel → verify worksheet names, column headers, cell values     | Pending |
| I2 | Integration: j2e per-locale              | Same for per-locale layout                                                      | Pending |
| I3 | Integration: e2j per-namespace           | Excel fixture → JSON → verify file paths and content                            | Pending |
| I4 | Integration: e2j per-locale              | Same for per-locale layout                                                      | Pending |
| I5 | Round-trip: j2e → e2j                    | JSON → Excel → JSON; diff output vs input, expect match                         | Pending |
| I6 | Round-trip: e2j → j2e                    | Excel → JSON → Excel; compare worksheet data                                    | Pending |
| I7 | Edge-case tests                          | Empty cells, missing locales, single-segment keys, unicode chars, duplicate keys | Pending |
| I8 | CI workflow: `ci.yml`                    | `.github/workflows/ci.yml`: triggers on PR + push to `main`; matrix: Python 3.10 + 3.11; steps: ruff check, mypy, pytest, coverage | Pending |
| I9 | CI workflow: `core-tag.yml`              | `.github/workflows/core-tag.yml`: triggers on `core/v*` tag push; runs full lint + test + `hatch build`; validates tag, no release artifacts | Pending |
| I10 | Coverage reporting in CI                | `coverage run` + `coverage report`; fail if < 60%                               | Pending |

### Check (v0.3.0 gate)

- `pytest` passes on clean install (Python 3.10 and 3.11).
- GitHub Actions CI is green.
- Coverage ≥ 60% for `core/src/i18n_tools/core/` and `core/src/i18n_tools/apps/`.
- Both locale styles verified via round-trip with no data loss.

### Act

- Tag as `v0.3.0`.
- Document any round-trip edge cases that need future attention.

---

## Phase 4 — Harden & Stabilize → v1.0.0

> **Theme**: Production-quality error handling, CLI flags, validation, and stable release.

### Do

| #   | Task                                             | File(s)                                                            | Detail                                                                     | Status  |
| --- | ------------------------------------------------ | ------------------------------------------------------------------ | -------------------------------------------------------------------------- | ------- |
| H1  | Replace generic `except Exception`               | [shared.py](core/src/i18n_tools/shared.py) line 230               | Specific: `FileNotFoundError`, `yaml.YAMLError`, `KeyError`, etc.         | Pending |
| H2  | Add `--config <path>` CLI flag                   | [app.py](core/src/i18n_tools/adapters/cli/app.py), `shared.py`    | Wire through argparse → `AppConfig`                                        | Pending |
| H3  | Add `--dry-run` CLI flag                         | [app.py](core/src/i18n_tools/adapters/cli/app.py), both apps      | Preview file operations without writing                                    | Pending |
| H4  | Add `--verbose` / `-V` CLI flag                  | [app.py](core/src/i18n_tools/adapters/cli/app.py), `shared.py`    | Set log level to DEBUG                                                     | Pending |
| H5  | JSON schema validation before conversion         | `core/json_wrapper.py` or new module                               | Validate structure matches locale style before processing                  | Pending |
| H6  | Duplicate-key detection in flattened output       | [json2excel.py](core/src/i18n_tools/apps/json2excel.py), [excel2json.py](core/src/i18n_tools/apps/excel2json.py) | Warn or error on duplicate keys after flattening | Pending |
| H7  | Guard `en` key existence in `DataFrameWrapper`   | [json2excel.py](core/src/i18n_tools/apps/json2excel.py) line 58   | Check `en` in `self.content` before access; clear error if missing         | Pending |
| H8  | Pre-commit hooks                                 | `.pre-commit-config.yaml` (new)                                    | `ruff check` + `ruff format`                                              | Pending |
| H9  | Coverage gate ≥ 80%                              | `.github/workflows/ci.yml`                                         | Fail CI if coverage drops below 80%                                        | Pending |
| H10 | Tests for all new features                       | `core/tests/`                                                      | Unit + integration for each new CLI flag and validation rule               | Pending |
| H11 | Tag v1.0.0 + CHANGELOG                          | —                                                                  | `cz bump --changelog` to generate changelog and create tag                 | Pending |
| H12 | Tighten mypy to strict mode                     | [core/pyproject.toml](core/pyproject.toml)                         | `disallow_untyped_defs = true`; add type stubs for third-party deps where available | Pending |
| H13 | Add mypy to CI gate                             | `.github/workflows/ci.yml`                                         | `mypy src/` must pass with zero errors                                     | Pending |

### Check (v1.0.0 gate)

- `ruff check`, `ruff format --check`, and `mypy src/` pass with zero findings.
- `--dry-run` outputs planned operations without writing files.
- `--config` accepts a custom YAML and overrides defaults.
- `--verbose` enables debug logging.
- Round-trip hash matches for all fixture datasets.
- Coverage ≥ 80%.
- All new CLI flags documented in `--help` and README.
- `v1.0.0` tag created with full changelog.

### Act

- Publish v1.0.0 release.
- Update README badges (CI status, version).
- Freeze Phase 4 scope; new features go to post-v1.0.0 backlog.

---

## Post-v1.0.0 — TBD

> Items below are planned but **not scoped or scheduled** until v1.0.0 ships.
> Priorities and phasing will be decided after stable release.

### Backlog

| Category          | Item                                                                       |
| ----------------- | -------------------------------------------------------------------------- |
| **GUI**           | Desktop wrapper (Tauri v2 + React + Vite + TS) in `gui/`                  |
| **Release**       | `gui-release.yml`: triggered by `gui/v*` tag, `tauri-action` builds + uploads to GitHub Release |
| **Release**       | Self-build documentation in root README (checkout tag → build core → build GUI) |
| **CLI**           | `--output-format json` for machine-readable output                        |
| **API**           | Public Python API with clean return types                                  |
| **CLI**           | `--include` / `--exclude` flags for namespace and language filtering       |
| **Reporting**     | Summary stats, missing translations, change diffs                          |
| **Distribution**  | Publish to PyPI (or internal registry)                                     |
| **Distribution**  | Dockerfile for containerised usage                                         |
| **Performance**   | Profiling and optimisation for large datasets                              |

### GUI architecture (reference)

```text
gui/                          core/
├── src/ (React frontend)     └── src/i18n_tools/ (Python CLI)
│   file picker, table views,
│   workflow UI
│        ↓ Tauri Commands (IPC)
├── src-tauri/ (Rust glue)
│        ↓ Subprocess
│   Invokes: python -m i18n_tools ...
```

Stack: Tauri v2 + React + Vite + TypeScript. Python CLI (`core/`) reused 100% via subprocess.

### GUI prerequisites from earlier phases

- **Phase 2-3**: Tests + CI (stable foundation).
- **Phase 4**: CLI flags (`--config`, `--dry-run`, `--verbose`) for GUI to invoke.
- **Post-v1.0.0**: Structured JSON output mode (`--output-format json`) + public API.
