# Excel → JSON (e2j)

Convert translated Excel workbooks back into localized JSON file sets.

---

## Overview

Command:

```bash
i18n_tools e2j
```

The tool reads Excel files within `<HOME_DIR>/<INPUT_DIR>/<EXCEL_DIR>` (or explicit `i18n.inputs` config). Each workbook’s worksheets become namespaces; each column after the key columns becomes a locale column.

Locale style (`per-namespace` vs `per-locale`) determines how JSON output directories are structured.

---

## Expected Excel Structure

Each worksheet must have the first columns in this order:

| Root | Key | en  | __other-locales__ ... |
| ---- | --- | --- | --------------------- |
| Root | Key | en  | other locales ...     |
| ---- | --- | --- | -------------------   |

Meaning:

- `Root`: Top-level key segment (can be blank if key is only one segment)
- `Key`: Remaining nested path relative to `Root` (can be blank if entire key is the `Root`)
- `en`: Source / reference language (used for stable key alignment)
- Other columns: Additional locales (e.g. `fr`, `ja`, `vi`)

Blank rows or rows where all locale values are empty are ignored for output.

Example worksheet snippet:

| Root | Key       | en      | fr        |
| ---- | --------- | ------- | --------- |
| home | title     | Home    | Accueil   |
| home | subtitle  | Welcome | Bienvenue |
| nav  | menu.file | File    | Fichier   |

The tool internally concatenates `Root` + `Key` (with `.`) when both present to form the full key path.

---

## Output Layout

Output JSON files are written under:

```plaintext
<HOME_DIR>/<OUTPUT_DIR>/<JSON_DIR>/<workbook>/<namespace>/...
```

Depending on `app.locale_style`:

### per-namespace (default)

```plaintext
output/json/<workbook>/common/en.json
output/json/<workbook>/common/fr.json
output/json/<workbook>/dashboard/en.json
output/json/<workbook>/dashboard/fr.json
```

### per-locale

```plaintext
output/json/<workbook>/en/common.json
output/json/<workbook>/en/dashboard.json
output/json/<workbook>/fr/common.json
output/json/<workbook>/fr/dashboard.json
```

---

## Configuration Keys

| Key                | Purpose                                                            |
| ------------------ | ------------------------------------------------------------------ |
| `app.locale_style` | Determines output directory style.                                 |
| `i18n.inputs`      | Optional list of Excel directory specs (like `json2excel.inputs`). |
| `i18n.indent`      | JSON indentation (default 2).                                      |

Example `i18n.inputs`:

```yaml
i18n:
  inputs:
    - name: product
      path: data/excel/product
      pattern: "*.xlsx"
```

Environment variables used for path resolution:

- `HOME_DIR`, `INPUT_DIR`, `OUTPUT_DIR`, `JSON_DIR`, `EXCEL_DIR`

---

## Validation & Conversion Flow

1. Resolve config and environment paths.
2. Collect workbooks from Excel input directory (or `i18n.inputs`).
3. For each worksheet: build a language map keyed by namespace (worksheet name).
4. Flatten per-language values based on reference keys from the `en` column.
5. Write locale JSON files using the selected locale style and indentation.

Empty cells are skipped—keys with no value in a locale are omitted (not written as empty strings).

---

## Typical Workflow

1. Receive edited Excel from translators.
2. Place/replace file in `<HOME_DIR>/<INPUT_DIR>/<EXCEL_DIR>/<project>`.
3. Run conversion: `i18n_tools e2j`.
4. Commit updated JSON output.
5. (Optional) Re-run `j2e` to confirm round-trip integrity.

---

## Example Session

```bash
i18n_tools e2j
tree output/json | head -n 20
```

Inspect a locale file:

```bash
cat output/json/myproject/common/en.json
```

---

## Quality Checks

After conversion you can quickly check for common issues:

```bash
grep -R 'TODO' output/json || echo 'No TODO markers'
python -m json.tool < output/json/myproject/common/en.json > NUL 2>&1 && echo OK (Windows)
```

Or run a minimal diff against previous version in VCS.

---

## Troubleshooting

| Issue                             | Cause                                     | Resolution                                             |
| --------------------------------- | ----------------------------------------- | ------------------------------------------------------ |
| No JSON files produced            | Wrong Excel path or empty worksheets      | Confirm `EXCEL_DIR` and workbook has data.             |
| Worksheet skipped                 | Contains < 1 data language column         | Ensure at least `en` + one target locale.              |
| Missing keys in some locale files | Cells blank in those locale columns       | Fill missing translations or accept fallback behavior. |
| Incorrect directory structure     | Wrong `app.locale_style`                  | Update config and re-run conversion.                   |
| Unicode errors                    | Non-UTF8 content in Excel cells           | Ensure workbook saved with UTF-8 compatible content.   |
| Duplicate keys merged             | Two rows resolve to same concatenated key | Fix duplicates in the worksheet.                       |

Increase verbosity by setting in config:

```yaml
log:
  level: 10 # Debug
```

---

## See Also

- `j2e.md` for the reverse operation (JSON → Excel)
- Main `README` for environment variables & config precedence

---

Happy localizing back to JSON! 🧩
