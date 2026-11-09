import json
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
RAW_FILE = DATA_DIR / "raw" / "countries_raw.json"
SUBSET_FILE = DATA_DIR / "interim" / "countries_subset.json"
FLAT_FILE = DATA_DIR / "interim" / "countries_flat.csv"

FIELDS = ["names", "codes", "region", "subregion", "population", "area",
          "capitals", "languages", "currencies", "borders"]


def join_values(items, key):
    return "; ".join(item[key] for item in items)


raw = pd.read_json(RAW_FILE)
subset = raw[FIELDS]
subset.to_json(SUBSET_FILE, orient="records", force_ascii=False, indent=2)

with open(SUBSET_FILE, encoding="utf-8") as f:
    data = json.load(f)

df = pd.json_normalize(data)

flat = pd.DataFrame()
flat["name"] = df["names.common"]
flat["alpha_2"] = df["codes.alpha_2"]
flat["alpha_3"] = df["codes.alpha_3"]
flat["region"] = df["region"]
flat["subregion"] = df["subregion"]
flat["population"] = df["population"]
flat["area_km2"] = df["area.kilometers"]
flat["capital"] = df["capitals"].apply(join_values, key="name")
flat["capital_count"] = df["capitals"].str.len()
flat["languages"] = df["languages"].apply(join_values, key="name")
flat["language_count"] = df["languages"].str.len()
flat["currencies"] = df["currencies"].apply(join_values, key="code")
flat["currency_count"] = df["currencies"].str.len()
flat["borders"] = df["borders"].str.join("; ")
flat["border_count"] = df["borders"].str.len()

flat.to_csv(FLAT_FILE, index=False, encoding="utf-8")

print(f"Subset saved: {SUBSET_FILE.name} ({len(subset)} records, {len(FIELDS)} fields)")
print(f"Flat table saved: {FLAT_FILE.name} ({flat.shape[0]} rows, {flat.shape[1]} columns)")
