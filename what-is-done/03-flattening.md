# Step 3 - Flattening

**Date:** 2026-11-10
**Script:** `src/flatten.py` (pandas + json only)
**Input:** `data/raw/countries_raw.json`
**Output:** `data/interim/countries_subset.json`, `data/interim/countries_flat.csv`

## What was done
1. **Subset.** We kept only the 10 fields the syllabus needs, plus identification, and saved them to `countries_subset.json`. That file is still nested.
2. **Flatten.** `pd.json_normalize` turned the nested dicts into columns, for example `area` → `area.kilometers` and `names` → `names.common`.
3. **Lists.** Each list became joined text plus a count column (option A).
4. **Save.** The result is `countries_flat.csv`: **254 rows × 15 columns**, one row per country.

## Decisions
| Decision | Choice | Reason |
|---|---|---|
| How to store lists | **Option A: joined text + count** | One row per country keeps the statistics correct. Option B (explode) would repeat each country's population once per list item, e.g. Jordan ×5 for its 5 borders, which makes sums and averages wrong. Option C (separate tables) is cleaner database design but more complex. The syllabus asks to flatten into "a usable table", and one row per country is enough for profiling and charts. |
| Which fields | Only syllabus fields: languages, currencies, borders, population, area, region, subregion, capital. Plus `name`, `alpha_2`, `alpha_3` to identify rows. | Stops `json_normalize` from creating 443 columns. Extras such as gini, coordinates and timezones were left out. |
| Subset file first | Yes (`countries_subset.json`) | We can inspect the smaller nested data before flattening. |
| Where to save | `data/interim/` | Derived files are neither raw nor clean. `data/raw/` holds only untouched source data (changed after the teammate review). |
| List separator | `"; "` | A comma can't be used, because the capital `"Washington, D.C."` contains one (changed after the teammate review). |
| Which piece of each list | language **name**, currency **code**, capital **name**, borders as alpha-3 codes | Readable and short |
| Capitals | **All capitals joined + `capital_count`** instead of only the "primary" one | Bolivia, Eswatini, Palestine and South Africa have 2-3 capitals and **none is marked primary**. Keeping only the primary capital would leave their capital empty. |

## Why not `pd.read_json` or `pd.read_csv` alone (tested)
- `pd.read_json` loads the data, but the dicts and lists stay inside cells. `df["area"].mean()` fails with `TypeError: unsupported operand type(s) for +: 'dict' and 'dict'`.
- `pd.json_normalize` flattens the dicts but **not the lists**, which is why step 3 above is needed.
- `pd.read_csv` cannot read the JSON file (`ParserError`).

## Result: columns
`name, alpha_2, alpha_3, region, subregion, population, area_km2, capital, capital_count, languages, language_count, currencies, currency_count, borders, border_count`

## Verification
- The population total in the flat table equals the total in the raw file, so no row was duplicated or lost.
- The border count total equals the total number of borders in the raw file, so no list items were lost.
- **Namibia's ISO code `"NA"` is preserved** when the CSV is read with `keep_default_na=False, na_values=[""]`.

## Analysis and issues found (for profiling)
Missing values when the CSV is read correctly:

| Column | Missing | Note |
|---|---|---|
| `alpha_2`, `alpha_3` | 4 | Abkhazia, Northern Cyprus, Somaliland, South Ossetia. Their empty-string codes now show up as real missing values. |
| `subregion` | 5 | e.g. Antarctica |
| `capital` | 5 | e.g. Antarctica |
| `currencies` | 3 | |
| `languages` | 1 | Antarctica |
| `borders` | 86 | **Not really missing.** Islands such as Japan, Iceland and Australia have no land borders (`border_count = 0`). |

1. **"Missing" vs "not applicable".** An empty `borders` cell means "no neighbours", which is a true fact, not lost data. The cleaning step must not drop or impute these.
2. **The Namibia trap.** Plain `pd.read_csv` turns the code `"NA"` into a missing value. The flat CSV must always be read with `keep_default_na=False, na_values=[""]`.
3. **Antarctica** has a population of 1,300 and an area of 14 million km², but no capital, languages or currencies. It's a likely outlier and a keep-or-remove decision for cleaning.
4. `area_km2` is stored as a float because 3 records have decimal areas.

## How to reproduce
```
python src/flatten.py
```

## Fixes after teammate review (2026-11-10)
A teammate reviewed the work. Each point was checked against the files and data before acting:

| Point | Verdict | Action |
|---|---|---|
| pandas missing from `requirements.txt` | True. It worked only because pandas was already installed locally. | Added `pandas>=2.0` |
| `"Washington, D.C."` breaks the capital column | True. Splitting on `", "` gave `['Washington', 'D.C.']`. It was the only value with a comma. | Separator changed to `"; "` for all list columns. Verified that the split count equals the count column for every row. |
| Notes said "the syllabus asks for one table" | Overstated | Reworded to quote the syllabus ("a usable table") |
| Lists as joined text might look "not fully flattened" | Judgment call | Kept option A. No extra long tables (team decision). |
| Derived files in `data/raw/` | Valid convention point | Moved to `data/interim/` |
| `countries_subset.json` duplicates raw data | True (checked: identical for the 10 fields) | Kept on purpose, so we can inspect the nested subset |
| README has no run instructions | True | Planned for step 9 |
