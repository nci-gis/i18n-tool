# i18n Tools

A Python toolkit for converting i18n JSON files to Excel and back, supporting multiple languages and nested keys.

---

## Features

- Convert i18n JSON files to Excel for easy editing and translation.
- Convert Excel files back to i18n JSON format for integration.
- Supports multiple languages and nested keys.
- Flexible directory and config options.
- Command-line interface with help and version commands.

---

## Installing Python

Python 3.9 or newer is required. If you already have `python --version` showing 3.9+ you can skip this section.

### Windows

Option A (Recommended GUI):

1. Go to the [official Python downloads page for Windows](https://www.python.org/downloads/windows/)
2. Download the latest Python 3.x (64-bit) installer.
3. Run the installer and CHECK the box: "Add Python to PATH".
4. Choose "Customize installation" if you want `pip` and `venv` (they are enabled by default) then finish.
5. Open a new PowerShell window and verify:

```powershell
python --version
pip --version
```

Option B (Command line with winget on Windows 10/11):

```powershell
winget install --id Python.Python.3 -e
```

If `python` still opens the Microsoft Store, try:

```powershell
py -3 --version
```

Then use `py -3 -m venv .venv` when creating the virtual environment.

Upgrade pip (optional but recommended):

```powershell
python -m pip install --upgrade pip
```

### Ubuntu (Debian-based)

Most recent Ubuntu releases include Python 3.x preinstalled. Check first:

```bash
python3 --version
```

If the version is < 3.9 or Python is missing:

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip
```

Create a versioned alternative (optional):

```bash
sudo update-alternatives --install /usr/bin/python python /usr/bin/python3 1
```

Verify:

```bash
python --version || python3 --version
pip3 --version
which python3
```

Then create a venv with:

```bash
python3 -m venv .venv
```

After installation proceed with Quickstart below.

---

## Quickstart

1. **Install Python (>= 3.9)**
2. **Setup environment:**

    ```sh
    cd <project dir>
    python -m venv .venv
    # Activate:
    # Windows (PowerShell): .venv\Scripts\Activate.ps1
    # Windows (cmd): .venv\Scripts\activate.bat
    # Unix-like: source .venv/bin/activate
    ```

3. **Install dependencies:**

    ```sh
    pip install -r requirements.txt
    ```

4. **Configure:**
    - Copy `.env.sample` to `.env` and edit as needed.
    - Place input files in the `input` directory.
    - Output files are generated in `output` by default.

---

## Usage

- **Convert JSON to Excel:**

    ```sh
    python -m i18n j2e
    ```

- **Convert Excel to JSON:**

    ```sh
    python -m i18n e2j
    ```

- **Show help:**

    ```sh
    python -m i18n -h
    ```

- **Show version:**

    ```sh
    python -m i18n -v
    ```

---

## Configuration

### Configuration Precedence

The tool merges settings from three sources (lowest to highest precedence):

1. Environment variables loaded from `.env` (optional)
2. Built‑in defaults in `src/i18n/resources/default.yaml`
3. Custom config file specified by `CONFIG_FILE` (if provided)

Later sources override earlier ones. Environment variables only seed the `env` section (input/output paths). Application behavior (like `locale_style`) is ultimately taken from the YAML config with highest precedence.

### Environment Variables (`.env`)

Copy `.env.sample` to `.env` and adjust as needed. All variables are optional; sensible defaults are used when omitted.

| Variable         | Default             | Purpose                                                                                                                          |
| ---------------- | ------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| `APP_NAME`       | `i18n-tools`        | Name used in logging.                                                                                                            |
| `LOG_COLOR_MODE` | (unset = false)     | Enable colored logging if one of: `true, yes, 1` (case-insensitive).                                                             |
| `HOME_DIR`       | `<HOME>/i18n-tools` | Working root. Relative paths are resolved against this. If set to `.`, current directory is used. Created if missing.            |
| `CONFIG_FILE`    | (unset)             | Path (absolute or relative to `HOME_DIR`) to a custom YAML config that overrides defaults.                                       |
| `INPUT_DIR`      | `input`             | Directory (absolute or relative to `HOME_DIR`) containing source files (both JSON and Excel). Must exist.                        |
| `OUTPUT_DIR`     | `output`            | Directory (absolute or relative to `HOME_DIR`) where generated files are written. Created if missing.                            |
| `JSON_DIR`       | `json`              | Directory (absolute or relative to `INPUT_DIR` / `OUTPUT_DIR`) containing JSON resources. Must exist for JSON->Excel operations. |
| `EXCEL_DIR`      | `excel`             | Directory (absolute or relative to `INPUT_DIR` / `OUTPUT_DIR`) containing Excel sources. Must exist for Excel->JSON operations.  |

Example `.env`:

```env
HOME_DIR=.
INPUT_DIR=data
OUTPUT_DIR=output
JSON_DIR=json
EXCEL_DIR=excel
LOG_COLOR_MODE=true
```

Notes:

- Boolean parsing treats `true`, `yes`, `1` (any case) as True.
- If a path is not absolute it is joined to the appropriate base (`HOME_DIR`, then `INPUT_DIR`).
- Missing required input directories (e.g. `json` or `excel`) will raise an error.

### YAML Config (`default.yaml` / custom `CONFIG_FILE`)

YAML controls higher-level behavior:

```yaml
app:
    name: i18n-tools
    locale_style: per-namespace  # or per-locale
log:
    level: 20  # INFO
json2excel:
    inputs: []    # optional explicit JSON file patterns
i18n:
    inputs: []    # optional explicit Excel file patterns
    indent: 2     # JSON indentation when exporting
```

Key fields:

- `app.locale_style`: Layout of your i18n filesystem.
  - `per-locale`: `<locale>/<namespace>.json`
  - `per-namespace`: `<namespace>/<locale>.json`
- `json2excel.inputs`: Override autodiscovery when importing from JSON.
- `i18n.inputs`: Override autodiscovery when importing from Excel.
- `i18n.indent`: Indentation level in generated JSON.

Directory layout examples:

Per-Locale:

```plaintext
messages/
    en/
        common.json
        home.json
    ja/
        common.json
        home.json
```

Per-Namespace:

```plaintext
messages/
    common/
        en.json
        ja.json
    home/
        en.json
        ja.json
```

To use a custom config, set `CONFIG_FILE`, e.g.:

```env
CONFIG_FILE=conf/my-config.yaml
```

This file is resolved relative to `HOME_DIR` unless absolute.

---

## Troubleshooting

- Ensure Python >= 3.9.
- Activate the virtual environment before running commands.
- Install missing dependencies:

    ```sh
    pip install -r requirements.txt
    ```

- For permission errors, run as administrator or check file paths.
- Try `PYTHONPATH=./src python -m i18n [option]`, if get module not found error

---

## Documentation

For more details, refer to the documentation as follows:

- [Installation](Installation.md)
- [Convert JSON to Excel](docs/j2e.md)
- [Convert Excel to JSON](docs/e2j.md)

Additional examples may be added over time. Feel free to open issues or PRs to improve docs.
