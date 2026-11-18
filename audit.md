# Audit

Dated log of editorial passes and verification runs. Newest first.

## 2026-11-18 — initial build

Scope: new paper written from seed material (an ideation conversation and a draft synthesis), replaced by a pre-registered empirical test on public data.

Timeline of the pre-registration:
  - 2026-11-18T18:59Z: analysis plan written into brief.md; SHA-256 08beb8370d1309bb6860c427520e7174255efe473b7863efeaa8474b0a3f7c6a. Before this point only non-outcome inputs had been inspected (Dorn data-page listing, ADHM shock columns, CBPP ratios, Welfare Rules Databook Table L5) and Dataverse metadata of the election datasets (file lists and licences, not values).
  - After 18:59Z: first download of election returns by `simulation/fetch_data.py --record`; the fetch log stores the brief hash at fetch time.
  - Deviations appended to brief.md after the outcome data were seen; none alters a specification, window, weight or decision rule.
  - 2026-11-18T19:15Z: first recorded run `analysis`, PASS, eleven declared inputs (archived as verification/analysis-20261118T195032621974Z.json).
  - 2026-11-18T19:50Z: second recorded run `analysis` (verification/analysis.json), PASS. Only change: results.json no longer lists CBPP-derived ratios for all 48 states (the CBPP terms bar derivative databases); the full table is used in memory for Figure 1. Every reported number is unchanged.

Built and verified:
  - simulation: fetch script with eleven pinned SHA-256 inputs; analysis package (2SLS with one- and two-way clustering, wild cluster bootstrap, all pre-registered specifications); 8 tests pass, including agreement with linearmodels and reproduction of the Welfare Rules Databook printed summary statistics.
  - claims: 266 claims (171 computation, 66 source, 29 definition, assumption or interpretation); every source claim `verified: false` with depth and note.
  - coverage self-audit (scratch script): 216 numerals checked, 173 bound to computation claims and 43 to source or definition claims, 0 uncovered; 9 spelled-out quantities, all covered; exempt: 140 dates, 23 citation locators, 17 identifiers, 8 formula constants, 1 magnitude word attached to a numeral.
  - refs: 60 entries, all cited; DOI identities match (advisory field differences only).
  - standards: no self-reference; abstract 245 words.
  - build: 18 pages, empty build log (no missing glyphs); every page rendered at 80 dpi and inspected by the author: figures legible at final size (text at least 8 pt), tables aligned, reference list complete. Fixes from the inspection: institutional names no longer repeated inside their own citations; nested quotation marks and title-casing corrected in three reference titles.
  - papers check (local): no FAIL; NEEDS_REVIEW for the 66 source claims, claim coverage, editorial review and visual review, which belong to an independent reviewer.
