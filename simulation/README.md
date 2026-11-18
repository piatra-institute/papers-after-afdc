# Analysis

Moderation test of the presidential-vote response to the China trade shock by state cash-assistance erosion after 1996. The analysis plan is in `../brief.md` and was fixed before any election returns were downloaded.

## Steps

1. `uv run python fetch_data.py` downloads every external input into `data/raw/` and checks each against a pinned SHA-256. It is the only networked step. It appends an entry to `data/fetch-log.json` with the time, the hash of `../brief.md` and each file's status. The first version of the script overwrote the log; only its last entry (2026-11-18T19:03:25Z) survives, and the log is self-recorded, not an external timestamp.
2. `uv run python run_all.py` builds the county panel, runs every specification of the brief and the analyses added after review and writes `output/results.json` and the three figures in `../paper/figures/`. It reads only `data/raw/` and `data/wrd_table_l5.csv`.
3. `uv run pytest -q` checks the estimators on synthetic data (including agreement with `linearmodels`) and the frozen inputs (Welfare Rules Databook summary statistics, official totals, moderator definitions).

The recorded run was made with `papers run after-afdc --id analysis --cwd simulation --artifact simulation/output/results.json --artifact paper/figures/fig1_moderation.png --artifact paper/figures/fig2_robustness.png --artifact paper/figures/fig3_bridge.png` and one `--input` for each of the 13 files in `data/raw/` plus `data/wrd_table_l5.csv`; the receipt is `../verification/analysis.json`.

## Layout

- `afdc/data.py`: readers for each source, FIPS mapping to 1990 counties, moderators, County Business Patterns aggregation, BEA transfers (with `(L)` cells set to $25,000), panel assembly.
- `afdc/estimators.py`: weighted OLS and 2SLS, one- and two-way cluster-robust variances (Cameron, Gelbach and Miller), first-stage and Sanderson–Windmeijer F statistics, restricted wild cluster bootstrap.
- `afdc/analysis.py`: the specifications of the brief, the descriptive terciles, the post-review sensitivity checks and the bridge to 2016 margins.
- `afdc/figures.py`: figures drawn at the 6.5-inch text width.
- `data/wrd_table_l5.csv`: transcription of Table L5 of the 2016 Welfare Rules Databook (public domain). California and Massachusetts use the non-exempt standard; Wisconsin 2016 uses the Community Service Jobs payment.

## Inputs and redistribution

| Input | Source | Licence | In repository |
| --- | --- | --- | --- |
| County presidential returns 2000–2016 | MIT Election Data and Science Lab, GitHub MEDSL/county-returns commit f44e3fc (same dataset as doi:10.7910/DVN/VOQCHQ) | CC0 1.0 | No (re-fetched) |
| County presidential returns 1868–2020 | Algara and Amlani, doi:10.7910/DVN/DGUMFI v1.1 | CC0 1.0 | No (re-fetched) |
| China-shock exposure, instrument, 2000 controls | Autor, Dorn, Hanson and Majlesi file archive, ddorn.net | None stated | No |
| County to commuting-zone crosswalk | ddorn.net (Autor and Dorn 2013) | None stated | No |
| State AFDC/TANF-to-poverty ratios | Center on Budget and Policy Priorities, spreadsheet of 2025-04-11 via the Internet Archive | Noncommercial reproduction with attribution; no derivative databases | No |
| Maximum benefits, July 1996 and 2016 | Welfare Rules Databook 2016, OPRE Report 2017-82 | Public domain | Transcription only |
| County Business Patterns 2000, 2008 | US Census Bureau | Public domain | No (re-fetched) |
| 2016 official returns | Federal Election Commission, Federal Elections 2016 | Public domain | No (re-fetched) |
| CPI-U, July 1996 and 2016; monthly 2000 and 2008 | Bureau of Labor Statistics API | Public domain | No (re-fetched) |
| County transfer receipts (CA35) and population (CA1-3), April 2011 release | Bureau of Economic Analysis, via the Internet Archive (the current tables no longer report family assistance separately) | Public domain | No (re-fetched) |

`output/results.json` reports CBPP-derived ratios only for the five states named in the paper and summary statistics for the rest, because the CBPP terms bar derivative databases; Figure 1 uses the full table in memory.

The election file on Harvard Dataverse now requires a guestbook form that collects personal details; the script uses the laboratory's public GitHub copy of the same release instead. Two corrections to that file are applied in `afdc/data.py` and documented in `../brief.md`.
