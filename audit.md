# Audit

Dated log of editorial passes and verification runs. Newest first.

## 2026-11-18 — closure round (fix round 2)

Scope: six minor points from closure-round1.json; responses in revision/2026-11/ledger/after-afdc/fix-round2.json.

Changes:
  - The transfer first stage is stated as non-detection with its intervals, in the abstract, the introduction and the discussion (N1).
  - "pre-registered" removed from the metadata genre (the only metadata edit) and from docstrings, comments and one results note in run_all.py, analysis.py and data.py; re-recorded (N3).
  - The CBP estimate is no longer read as evidence against the hypothesis; the post-treatment check "speaks to" the alternative (N4).
  - The reliability correction is called an approximation, with the shared CPS sample across adjacent windows explained (N5).
  - wrd-table locator corrected to pp. 246-247; two rationales now say Table 3 (N6).
  - The BEA citation moved next to the agency name; Table 1 moved after the paragraph that discusses it (visual).
  - Title, status and web_blurb untouched (N2: owner's decisions).

Verification:
  - recorded run `analysis` re-run 2026-11-18T21:03Z (code comments and one results note changed; every number unchanged; previous receipt archived).
  - claims: 372 (254 computation, 71 source, 47 other); 70 source claims byte-identical to round 1, wrd-table changed in its locator only; all `verified: false`.
  - coverage self-audit: 301 numerals, 256 bound to computation claims and 45 to source or definition claims, 0 uncovered; 16 spelled-out quantities, all covered.
  - refs: 66, no mismatch; standards: abstract 250 words; build: 21 pages, empty log; papers check: no FAIL.

## 2026-11-18 — revision round 1 (independent Claude referee)

Scope: response to referee-claude.json (F1-F11) and the suggested first-stage extension; per-finding responses in revision/2026-11/ledger/after-afdc/fix-round1.json.

Changes:
  - Process claims rewritten (F1): no "pre-registered"; the paper states that the ADHM archive (which contains Leip vote shares) and the moderator data were opened before the plan, that the open returns were downloaded after it, and that the ordering is self-recorded. The plan hash 08beb837... is shown to be reproducible from brief.md. fetch_data.py now appends to the fetch log instead of overwriting it.
  - Bound restated with its spread (F2): upper bounds per SD 0.20 to 1.03 across specifications of the moderator, 3.12 for the real-benefit decline; "rules out" removed; new moderator-by-control interactions.
  - DC decomposition of the replication gap (F3); CPS noise discussion, reliability bound and three measurement variants (F4); waivers, Ziliak et al. (2000), the 1993-94 base, early erosion share and the post-treatment check (F5); placebo, sign and window wording (F6, F7); abstract scope and units (F8); CBP 2SLS estimate, Sanderson-Windmeijer F and CBP rows in Figure 2 (F9); Hays et al. (2005), Walter (2010), Blanchard, Bown and Chor (2024), Hainmueller, Mummolo and Xu (2019) added after registry checks (F10, F11).
  - Extension: first-stage test with BEA CA35 (April 2011 release via the Internet Archive): family assistance did not measurably respond to the shock (0.98 dollars per capita per point, interval -6.36 to 8.32) and erosion did not moderate it. Subtitle changed to "No Detectable Cash-Assistance Channel from the China Shock to the Presidential Vote".

Verification:
  - recorded run `analysis` re-run 2026-11-18T20:30Z with 14 declared inputs (three new: BEA CA35 and CA1-3 April 2011, BLS monthly CPI 2000 and 2008); previous receipt archived; 9 tests pass.
  - claims: 365 (248 computation, 71 source, 46 other), all source claims `verified: false`.
  - coverage self-audit: 295 numerals, 250 bound to computation claims and 45 to source or definition claims, 0 uncovered; 14 spelled-out quantities, all covered (the audit now also catches hyphenated fractions such as four-fifths, and exempts clock times).
  - refs: 66 entries, all cited, no identity mismatch; standards: abstract 242 words, no self-reference.


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
