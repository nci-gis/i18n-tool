# JSON → Excel (j2e)

Convert a set of localized JSON message files into one or more Excel workbooks for translators.

---

## Overview

Command:

```bash
i18n_tools j2e
```

The tool scans your JSON input directory structure (derived from `HOME_DIR` + `INPUT_DIR` + `JSON_DIR`) and groups files by namespace. Each namespace becomes a worksheet inside an Excel workbook named after the project (directory) it came from.

Locale style is controlled by `app.locale_style` in config (`per-namespace` or `per-locale`).

---

## Input Layout Requirements

Two supported directory styles. Replace `messages` with your actual JSON root (default is under `<HOME_DIR>/<INPUT_DIR>/<JSON_DIR>`):

### 1. per-namespace (default)

```plaintext
messages/
  common/
    en.json
    fr.json
  dashboard/
    en.json
    fr.json
```

### 2. per-locale

```plaintext
messages/
  en/
    common.json
    dashboard.json
  fr/
    common.json
    dashboard.json
```

Set in YAML config:

```yaml
app:
  locale_style: per-namespace  # or per-locale
```

---

## How Grouping Works

1. Each immediate subdirectory of the JSON root is treated as a project/workspace bucket (if `json2excel.inputs` not explicitly set).
2. Within that, each namespace (folder name in per-namespace, or JSON filename stem in per-locale) builds a unified row set.
3. Keys are flattened into two columns: `Root` and `Key`. Nested keys like `home.title.header` are split into `home` (Root) and `title.header` (Key).
4. One column per language appears (language codes taken from filenames or folder names depending on style). The first language column is expected to be `en` (used as the structural reference). Other languages align by full key.

---

## Output

Excel files are written to:

```plaintext
<HOME_DIR>/<OUTPUT_DIR>/<EXCEL_DIR>/<project>.xlsx
```

Each worksheet corresponds to a namespace. Example worksheet snippet:

| Root | Key       | en      | fr        |
| ---- | --------- | ------- | --------- |
| home | title     | Home    | Accueil   |
| home | subtitle  | Welcome | Bienvenue |
| nav  | menu.file | File    | Fichier   |
| nav  | menu.edit | Edit    | Éditer    |

If a translation cell is empty or key missing, the cell will be blank.

---

## Configuration Overrides

| Key                 | Purpose                                                                                                  |
| ------------------- | -------------------------------------------------------------------------------------------------------- |
| `app.locale_style`  | Determines how JSON files are interpreted (`per-namespace` / `per-locale`).                              |
| `json2excel.inputs` | Optional explicit list of input directory specs (objects with `name`, `path`, include/exclude patterns). |

Example `json2excel.inputs` entry:

```yaml
json2excel:
  inputs:
    - name: app
      path: app/i18n/messages
      pattern: "*.json"
```

Environment variables influencing paths:

- `HOME_DIR`, `INPUT_DIR`, `OUTPUT_DIR`, `JSON_DIR`, `EXCEL_DIR`

---

## Advanced: Custom Input Selection

If `json2excel.inputs` is omitted, the tool enumerates each subdirectory inside the JSON root and treats each as a project grouping. Provide `inputs` to explicitly control which directories and patterns are processed.

Include / Exclude examples (mutually exclusive):

```yaml
json2excel:
  inputs:
    - name: app1
      path: app1/i18n/messages
      include: ["common", "dashboard"]
    - name: app2
      path: app2/i18n/messages
      exclude: ["draft"]
```

---

## Typical Workflow

1. Update / add translations in JSON repositories (often developers do this for new keys in source language).
2. Run `i18n_tools j2e` to generate or refresh Excel workbooks.
3. Distribute Excel file(s) to translators.
4. After translation, run the reverse command (see `e2j.md`) to sync updated localized strings back into JSON.

---

## Example Session

```bash
i18n_tools j2e
ls output/excel
# => myproject.xlsx
```

Open the workbook and edit non-English columns only; avoid altering key structure columns.

---

## Troubleshooting

| Issue                                | Cause                                                | Resolution                                                                 |
| ------------------------------------ | ---------------------------------------------------- | -------------------------------------------------------------------------- |
| No Excel file produced               | Wrong path                                           | Check `HOME_DIR`, `INPUT_DIR`, `JSON_DIR`; verify files exist.             |
| Missing worksheet                    | Namespace folder or JSON file absent in some locales | Ensure each locale has the file (or accept missing columns).               |
| Rows collapsed / merged unexpectedly | Duplicate flattened keys                             | Ensure unique keys; search for accidental duplicates.                      |
| Non-UTF8 decode errors               | Invalid encoding in source JSON                      | Convert files to UTF-8 or adjust reader options (currently fixed to utf8). |
| Wrong grouping                       | Mis-set `app.locale_style`                           | Set correct style and re-run.                                              |

If problems persist, run with higher log verbosity (set `log.level: 10` in config) and inspect debug output.

---

## See Also

- Reverse operation: `e2j.md` (Excel → JSON)
- Main `README` for configuration and environment variable details

---

Happy converting! 🎉
