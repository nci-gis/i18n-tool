# Installation

This guide explains how to install the i18n Tools package locally from a built wheel located in the `dist/` directory.

If you have not installed Python yet, see the "[Installing Python](README.md#installing-python)" section in `README.md` first.

---

## 1. Prerequisites

- Python 3.9+ (verify with `python --version`)
- `pip` and `venv` available (`python -m ensurepip --upgrade` if needed)
- Project workspace cloned (or package wheel obtained)

Optional (recommended): use a virtual environment to isolate dependencies.

Create & activate a venv (PowerShell on Windows):

```powershell
python -m venv .venv
. .venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 2. Get the Package

The wheel file should already be present under `dist/` (e.g. `dist/i18n_tools-<version>-py3-none-any.whl`).

---

## 3. Install Using Provided Scripts

Convenience scripts wrap the wheel installation.

Windows (cmd):

```cmd
scripts\install.bat
```

Windows (PowerShell):

```powershell
& scripts/install.bat
```

Linux/macOS:

```bash
chmod +x scripts/install.sh  # first time only
./scripts/install.sh
```

Behavior (by default):

1. Locates the newest wheel in `dist/`.
2. Runs `pip install --upgrade <wheel>`.
3. Prints installed version using `python -m i18n -v`.

---

## 4. Upgrade / Reinstall

After building a newer wheel:

```bash
pip install --upgrade dist/i18n_tools-<new-version>-py3-none-any.whl
```

Force reinstall overwriting cached artifacts:

```bash
pip install --force-reinstall dist/i18n_tools-<version>-py3-none-any.whl
```

---

## 6. Uninstall

```bash
pip uninstall i18n-tools
```

If you installed in editable mode, the source directory remains; only the package entry metadata is removed.

---

## 7. Verification

Check the CLI responds:

```bash
i18n_tools -v
i18n_tools -h
```

Run a quick round-trip (adjust paths to your data):

```bash
i18n_tools j2e
i18n_tools e2j
```

If you see logging output with start/end markers the install is functioning.

---

## 8. Troubleshooting

| Symptom                                 | Possible Cause                                      | Fix                                                               |
| --------------------------------------- | --------------------------------------------------- | ----------------------------------------------------------------- |
| `python: command not found`             | Python not installed / PATH not updated             | Install Python or start a new shell; see README.                  |
| `ModuleNotFoundError: i18n`             | Virtual environment not activated or install failed | Activate venv, reinstall wheel.                                   |
| `pip` installs but old version persists | Multiple Python versions                            | Use `python -m pip install ...` matching the interpreter you run. |
| Permission denied (Linux)               | System site-packages writes blocked                 | Use a venv or add `--user` (not recommended for shared envs).     |

Still stuck? Capture command + full output and share the issue.

---

## 9. Next Steps

- Check [j2e](docs/j2e.md) for JSON to EXCEL conversion.
- Check [e2j](docs/e2j.md) for EXCEL to JSON conversion.
- Review [README](README.md) for configuration, environment variables, and usage examples.

---
