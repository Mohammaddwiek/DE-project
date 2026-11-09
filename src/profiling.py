from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FLAT_FILE = PROJECT_ROOT / "data" / "interim" / "countries_flat.csv"
OUTPUT_DIR = PROJECT_ROOT / "report" / "profiling"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(FLAT_FILE, keep_default_na=False, na_values=[""])

print("Shape:", df.shape)
print("Namibia alpha_2:", df.loc[df["name"] == "Namibia", "alpha_2"].item())
