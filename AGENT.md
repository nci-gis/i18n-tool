# Agent Guide

This repository contains a Python CLI tool for converting i18n JSON files to Excel and back.

## Quick orientation

- Entry point: [src/i18n/__main__.py](src/i18n/__main__.py)
- CLI wiring and tool registry: [src/i18n/adapters/cli/app.py](src/i18n/adapters/cli/app.py)
- JSON -> Excel: [src/i18n/apps/json2excel.py](src/i18n/apps/json2excel.py)
- Excel -> JSON: [src/i18n/apps/excel2json.py](src/i18n/apps/excel2json.py)
- Config resolution and paths: [src/i18n/shared.py](src/i18n/shared.py)
- Locale layout logic: [src/i18n/core/json_wrapper.py](src/i18n/core/json_wrapper.py)
- Excel I/O: [src/i18n/core/excel_wrapper.py](src/i18n/core/excel_wrapper.py)

## How to run

- Use the module entry point during development: `python -m i18n j2e` or `python -m i18n e2j`.
- The installed script is `i18n_tools` (from [pyproject.toml](pyproject.toml)).

## Configuration model

- Config precedence: `.env` < [src/i18n/resources/default.yaml](src/i18n/resources/default.yaml) < custom config via `CONFIG_FILE`.
- Locale layout is controlled by `app.locale_style` (per-namespace or per-locale).
- Input discovery uses `json2excel.inputs` and `i18n.inputs` in YAML or defaults to directory scanning.

## Tests

- If tests are added, place them under [tests/](tests) and run with `pytest`.

## Style and safety notes

- Keep CLI behavior backward compatible (`j2e` and `e2j`).
- Preserve filesystem layout assumptions unless explicitly changing the contract.
- Be careful with encoding and ensure JSON writes remain `utf8`.
