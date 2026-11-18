# Source provenance

Identity and support are recorded separately. Every DOI in references.yaml was resolved with `curl https://api.crossref.org/works/<DOI>` (DataCite for the two Dataverse DOIs) on 2026-11-18; authors, title, year, venue, volume, issue and pages follow those records. Abstracts came from the Crossref record where deposited, otherwise from Semantic Scholar or OpenAlex. Primary documents were read at govinfo.gov, clerk.house.gov and senate.gov (Internet Archive capture). Temporary retrieval files are outside the repository; SHA-256 values of the full texts read are given where they matter. `papers refs --verify` records the machine identity check separately. Every source claim in claims.yaml keeps `verified: false` for the independent reviewer.

## Primary documents

| ID | Material inspected | Depth and use |
| --- | --- | --- |
| prwora1996 | govinfo HTML of P.L. 104-193 (SHA-256 5accfc2a…). Sec. 103 new secs. 401(b), 408(a)(1), 408(a)(7); Statutes at Large page markers 2113, 2134, 2137 | Fulltext. Quotes in claims.yaml. The paper does not describe exceptions to the 60-month limit (hardship exemptions up to 20 percent of the caseload) beyond calling the limit federal. |
| hr4605 | govinfo HTML of H.R. 4605 as introduced (SHA-256 478a827b…), long title, table of contents, proposed sec. 492 | Fulltext. Only the 24-month WORK transition and the long title are used. |
| s1117 | govinfo HTML of S. 1117 as introduced (SHA-256 ba6a5d9f…), proposed secs. 400, 402(c)(1), 404, 413 | Fulltext. "Sum sufficient" appropriation, FMAP matching and the 60-month limit with the 7.5 percent unemployment exemption are quoted. Other hardship exemptions (work, other hardship capped at 15 percent) exist and are not described. |
| clinton1995veto | govinfo Public Papers 1995 Book II, pp. 1853–1855 | Fulltext. Used only for the veto of H.R. 2491 and its Title XII welfare provisions. |
| clinton1996veto | govinfo Public Papers 1996 Book I, pp. 22–23 | Fulltext. The quoted phrase about economic downturn spans the page break. |
| clinton1996signing | govinfo Public Papers 1996 Book II, pp. 1328–1330 | Fulltext. Contingency-funding objection on p. 1329. |
| houserc383 | clerk.house.gov/Votes/1996383 (SHA-256 3ccb5f7a…) | Fulltext: totals and party table. |
| senatevote262 | senate.gov page through the Internet Archive capture of 2026-02-11 (SHA-256 99d8046d…); the live site refused automated clients | Fulltext: totals; party breakdown counted from the alphabetical member list by script (R 53 yea; D 25 yea, 21 nay, 1 not voting). |
| crs2019 | everycrsreport.com HTML mirror of CRS R45966 (full text); author block lists Gene Falk, Mariam Ghavalyan and Jameson A. Carter | Fulltext: Summary, Figure 7 text, Table 4. The congress.gov PDF endpoint returned an HTML page to the script; the mirror reproduces the report text. Static TRIM3 accounting; the paper does not treat it as causal. |

## Data

| ID | Material inspected | Licence and use |
| --- | --- | --- |
| medsl2018 | GitHub MEDSL/county-returns commit f44e3fc, countypres_2000-2016.csv (git blob eea9214, SHA-256 01711110…) and its codebook; Dataverse metadata of doi:10.7910/DVN/VOQCHQ (version 20, CC0 1.0, guestbook 458 on file access) | CC0 1.0. Identity verified through DataCite (title now "County Presidential Election Returns 2000-2024", publication year 2018); the entry title gives the 2000–2016 release used. Two problems found and corrected in code: `totalvotes` repeated for same-name Virginia cities; Kansas City, MO reported separately from 2004. |
| algara2021data, amlani2021 | Dataverse files 5028532 (presidential Rdata, SHA-256 c3ad5e87…) and 5028533 (codebook); Electoral Studies identity | CC0 1.0. Used for 1988–2000. Floyd County, Indiana, 2016 differs from MEDSL and FEC by 6,000 Democratic votes; 2016 values from this source are not used. |
| adhmdata2020 | ADHM file archive (SHA-256 c3cb574c…): Readme.pdf, do-files, president_2000_2016.dta columns | No licence stated. Shock, instrument and controls used; Leip-derived vote shares read only for validation V1b. Readme p. 2 states the Leip data are "available for purchase". |
| cbpp2025 | 2025-04-11-TPR-1978-2023.xls (SHA-256 d6ef9b16…), sheets "50-State Ratios 1979-2023" and "State TPR, 2-year avg"; cbpp.org terms of use (Internet Archive capture 2026-11-16) | Terms: noncommercial reproduction with attribution; no derivative databases. Not redistributed. Reference title follows the sheet heading with the file name; no separate publication title was found. |
| wrd2017 | OPRE Report 2017-82 PDF (SHA-256 7cfeca53…), Table L5 pp. 245–246, notes, public-domain statement | Public domain. Transcribed to simulation/data/wrd_table_l5.csv; transcription checked against printed means and medians. |
| fec2017 | federalelections2016.xlsx (SHA-256 b4a1d138…), Table 2 and publication sheet (December 2017, updated February 2018 and January 2023) | Public domain. |
| cbp2000 | cbp00co.zip, cbp08co.zip (Census) | Public domain. Suppressed cells imputed at size-class midpoints. The reference date is the later data year. |
| blscpi | BLS public API v1, series CUUR0000SA0, July 1996 157.0 and July 2016 240.628 | Public domain. |

## Literature

| ID | Inspected | Depth and limit of use |
| --- | --- | --- |
| autor2020 | Author-hosted version of record (SHA-256 ad185946…) and online appendix | Fulltext. Table 5 panel B, its notes (p. 3176), footnote 25 (p. 3153), Section V. The text calls the full-controls column 6 while the printed table has five columns; the paper cites the number, 1.71 (0.90), not the column label. |
| autor2013 | Author-hosted PDF (SHA-256 a7add127…) | Fulltext. Abstract and the transfers discussion on pp. 2148–2149. |
| autordorn2013 | Crossref identity | Identity. Cited only as the origin of the county to commuting-zone crosswalk, per the Dorn data page. |
| margalit2011, kim2021psrm, kim2021cps, swank2003, halikiopoulou2016, vlandas2022, gingrich2019, milner2021, fetzer2019, rodrik1998, bisbee2020, jensen2017, baccini2021, choi2024, che2022, colantone2018apsr, colantone2018ajps, pierson1993, soss1999, mettler2004, campbell2012, corman2017, soss2001, parolin2021, bitler2016, blank2002, moffitt2015, mutz2018, morgan2018, margalit2019, nizalova2016, bun2019, cameron2011, sanderson2016, adao2019, borusyak2022 | Crossref identity plus deposited abstract, or the Semantic Scholar/OpenAlex abstract where Crossref had none | Abstract. Each use in the paper is limited to what the abstract states; no page or table locators are given for these works. Corman et al.'s 3 to 4 points and Parolin's 52, 21 and 27 percent are quoted from the abstracts. |
| balcazar2026 | Working-paper PDF from the first author's website (title page, abstract, introduction; PDF creation date 2026-03-02) | Fulltext of the pages used; not peer reviewed; no DOI. |
| ruggie1982 | Crossref identity and abstract | Abstract. The abstract does not use the phrase "embedded liberalism", which appears in the title; the paper attributes the well-known thesis to Ruggie in prose and binds no source claim to it. |
| cameron2008 | Crossref identity | Identity. Cited for the wild cluster bootstrap procedure only. |

## Search and selection

Closest-work searches used Crossref keyword queries, OpenAlex (rate-limited during the session) and three web searches. Leads from the web searches (Kim and Pelc 2021; the Balcazar and Lee working paper; Milner 2021; Vlandas and Halikiopoulou 2022) were checked against Crossref or read at source before citation. No study was found that tests state AFDC/TANF erosion as a moderator of the political response to trade shocks; this is a statement about the search, not a proof of absence.

## Transcription changes

Reference titles follow the registry records with these changes: Crossref's HTML entities (`&amp;`) are written as `&`; the MathML `F` in Sanderson and Windmeijer's title is written as plain F; the Vlandas and Halikiopoulou title keeps its curly quotes. No arrows or other glyphs outside the build font occur in titles.
