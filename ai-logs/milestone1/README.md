# AI Usage Index – Milestone 1

| File | Tool | Version | Date | What it covers |
|---|---|---|---|---|
| `02-extraction.txt` | Claude Code (model: Claude Opus 5.5) | 2.1.292 | 2026-11-09 | Repo check; testing the REST Countries API and finding v3.1 deprecated; switching to v5; API key storage (`.env`) and fixing the key leaked to GitHub; writing and running `src/extract.py`; checking the raw data (found 4 territories with empty-string ISO codes) |
| `03-flattening.txt` | Claude Code (model: Claude Opus 5.5) | 2.1.292 | 2026-11-10 | Choosing how to flatten lists (joined text + count vs explode vs separate tables); testing `pd.read_json`, `pd.json_normalize` and `read_csv(keep_default_na=False)` on our data; finding the Namibia `"NA"` trap and the countries with multiple capitals; writing and running `src/flatten.py`. The rest of this session (checking a teammate's review and fixing it) will be in the next transcript. |

## Notes
- `src/extract.py` was written with AI help. It uses `requests` and `python-dotenv`, which are outside the course scope, so it keeps its explanatory comments.
- Code from the flattening step onwards uses only pandas (plus `json`), as covered in the course.
- Every transcript was scanned for the API key before committing.
