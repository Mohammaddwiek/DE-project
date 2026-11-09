# Step 2 - Extraction

**Date:** 2026-11-09
**Script:** `src/extract.py`
**Output:** `data/raw/countries_raw.json`, `data/raw/extraction_metadata.json`

## What was done
Downloaded every country from the REST Countries API and saved the response unchanged as the raw dataset. All later steps (flattening, profiling, cleaning) read this file and never call the API again.

## Why
- **Raw stays raw.** The raw file is an untouched copy of the source. If a later step goes wrong, we rerun it from this file.
- **Stable data.** Population is updated by the API every few hours. Working from one saved snapshot means our results don't change between runs or before the defense.
- **The source can disappear.** The old API version (v3.1) was shut down without warning (see below). With the raw file in the repo, the pipeline still works.

## Decisions
| Decision | Choice | Reason |
|---|---|---|
| API version | **v5** (`https://api.restcountries.com/countries/v5`) | The v3.1 endpoints we tested (`/all`, `/all?fields=...`, `/alpha/JOR`) redirect (301) to a file with the error *"This API version has been deprecated"*. They return no data. |
| API key storage | `.env` file, listed in `.gitignore`; `.env.example` committed as a template | The key is a secret and must not be on GitHub. Anyone rerunning the pipeline uses their own key. |
| Fields | All fields except `names.translations` | Raw data should be complete. Translations (the name in ~25 languages) are not needed and make the file much bigger. |
| Pagination | `limit=100` (free-plan max), `offset` 0 → 100 → 200, stop when `meta.more` is false | The API returns at most 100 countries per request. |
| Re-running | Skip the download if the raw file exists; `--force` re-downloads | We download once and then work on a fixed snapshot. |
| Metadata | Save download time, source, count and number of requests | So the report can state exactly which snapshot was used. |
| Politeness | 1-second pause between requests | Well below the API's 20 requests / 10 seconds limit. |

## Result
```
request 1: offset 0,   got 100 countries (100 of 254 so far)
request 2: offset 100, got 100 countries (200 of 254 so far)
request 3: offset 200, got 54 countries  (254 of 254 so far)
```
- **254 records**, downloaded 2026-11-09 20:25:58 UTC, in 3 requests. The file is 1.68 MB.
- The count matches the API's own `meta.total`, which the script checks automatically.
- 34 top-level fields, present in every record, including `names`, `codes`, `region`, `subregion`, `population`, `area`, `languages`, `currencies`, `borders` and `capitals`.
- `names.translations` was removed as intended.
- Running the script a second time correctly skipped the download.

## Analysis and issues found (for profiling)
1. **254, not 249.** The API docs' example shows 249. The real dataset also includes disputed or partially recognised territories.
2. **Hidden missing values: empty strings.** Abkhazia, Northern Cyprus, Somaliland and South Ossetia have `alpha_3 = ''` and `alpha_2 = ''` (`iso_status: unassigned`). My first check counted only `None` and wrongly reported "0 missing". **Lesson: missing data can be `None`, `''`, `[]` or `{}`. Profiling must check for all of them.** These 4 are why there are only 251 unique alpha-3 codes for 254 records. This matters for joining datasets by ISO code later.
3. **Not only countries.** The `classification` field shows 193 sovereign UN members plus dependencies (overseas territories, collectivities and so on). We need to decide in cleaning whether to keep them all or flag them.
4. **Fields with no real data:**
   - `leaders` is a paid-plan field. On the free plan it contains only an "upgrade" message.
   - `assets` is empty.
   - `_meta` is an API timestamp.

   These are candidates to drop during flattening.

## Security incident (and fix)
The API key was accidentally committed to the public repo twice: `.env.API_KEY` in commit `6bc4870`, and `.env` in commits `d2d80b2` and `8e0da76`.
- Fix applied: `.gitignore` now contains `.env`, and `.env` was removed from tracking (commit `44b4b7a`).
- The key is **still visible in the Git history**. The real fix is to **regenerate the key** on restcountries.com. Deleting a file does not remove it from history.
- Lesson: `.gitignore` must exist **before** the secret file is created. Also, the pattern `.env` matches only a file named exactly `.env`, not `.env.API_KEY`.

## How to reproduce
```
pip install -r requirements.txt
copy .env.example .env      # then paste your own key into .env
python src/extract.py       # add --force to download a fresh snapshot
```
