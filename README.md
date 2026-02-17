# i18n-tools

A toolkit for converting i18n JSON files to Excel and back, supporting multiple languages and nested keys.

## Repository structure

```text
i18n-tool/
├── core/       Python CLI — runs independently
├── gui/        Desktop GUI wrapper (planned)
├── docs/       Project-wide planning docs
└── scripts/    Build and release helpers
```

| Module | Description | Status |
| ------ | ----------- | ------ |
| `core/` | Python CLI for JSON-to-Excel and Excel-to-JSON conversion. Can be installed and used standalone. | Active |
| `gui/` | Lightweight desktop wrapper (Tauri + React) that invokes the CLI via subprocess. | Planned (post-v1.0.0) |

## Getting started

### Prerequisites

- Python >= 3.9
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

### Setup

```sh
cd core
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Run

```sh
cd core

# JSON to Excel
python -m i18n_tools j2e

# Excel to JSON
python -m i18n_tools e2j

# Help
python -m i18n_tools -h
```

## Configuration

Copy `core/.env.sample` to `core/.env` and edit as needed. See [core/README.md](core/README.md) for the full configuration reference covering environment variables, YAML config, and locale style options.

## Documentation

- [Core CLI README](core/README.md) — usage, configuration, and troubleshooting
- [Installation guide](core/Installation.md)
- [JSON to Excel](core/docs/j2e.md)
- [Excel to JSON](core/docs/e2j.md)
- [Roadmap (PDCA)](docs/plan/PDCA.md)

## License

See [LICENSE](LICENSE) if present.

## Transparency

AI-assisted development (e.g., Claude Code, Copilot) was used for scaffolding and iteration.
