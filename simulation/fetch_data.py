"""Download every external input, verify it against a pinned SHA-256, and log the fetch.

This script is the only part of the project that uses the network. The recorded
analysis (run_all.py) reads the files it writes under data/raw/, which are
gitignored because several sources do not permit redistribution. Re-running this
script reproduces identical bytes or stops with a checksum error.

Usage:
    uv run python fetch_data.py            # download missing files, verify all
    uv run python fetch_data.py --record   # print hashes of new files instead of failing

The fetch log records the SHA-256 of ../brief.md at the time of download, so the
order "analysis plan first, outcome data second" can be checked against audit.md.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import sys
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "data" / "raw"
LOG = HERE / "data" / "fetch-log.json"
BRIEF = HERE.parent / "brief.md"
UA = "Mozilla/5.0 (compatible; research-data-client)"

WAYBACK = "http://web.archive.org/web"

SOURCES = [
    {
        "name": "adhm_archive",
        "file": "ADHM-PoliticalPolarization-FileArchive.zip",
        "url": "https://www.ddorn.net/data/ADHM-PoliticalPolarization-FileArchive.zip",
        "sha256": "c3cb574c63d05f0cd1607ffd4a35c1b758cdf1658a18b0d21b6a72d97bb82258",
        "licence": "Public download from David Dorn's data page; no licence stated; cite ADHM (2020). Not redistributed.",
        "role": "CZ trade shock 2000-2008, instrument, CZ and county 2000 controls (vote-share columns not used)",
    },
    {
        "name": "cw_cty_czone",
        "file": "cw_cty_czone.zip",
        "url": "https://www.ddorn.net/data/cw_cty_czone.zip",
        "sha256": "0843c69c6598ec01311d131e08996a9805e17e2cc7cedbd2d72d617193ed6b9a",
        "licence": "Public download from David Dorn's data page; no licence stated; cite Autor and Dorn (2013). Not redistributed.",
        "role": "1990 county to 1990 commuting-zone crosswalk (used for County Business Patterns aggregation)",
    },
    {
        "name": "medsl_county",
        "file": "countypres_2000-2016.csv",
        "url": "https://raw.githubusercontent.com/MEDSL/county-returns/f44e3fc105ab3a229b810d769349436bff9bd580/countypres_2000-2016.csv",
        "sha256": "017111108d12cd68c1ad75cab5c18f15103d021de7e8a895bf13c6ef2ad3e887",
        "licence": "MIT Election Data and Science Lab; the Harvard Dataverse release of this dataset (doi:10.7910/DVN/VOQCHQ) is CC0 1.0.",
        "role": "County presidential returns 2000-2016 (outcomes, 2000 weights, 2016 two-party votes)",
    },
    {
        "name": "algara_amlani_pres",
        "file": "dataverse_shareable_presidential_county_returns_1868_2020.Rdata",
        "url": "https://dataverse.harvard.edu/api/access/datafile/5028532",
        "sha256": "c3ad5e87a6dfd8aaf25725ca43b47e86c1cfe828958f6371fe096543906c1687",
        "licence": "CC0 1.0 (Harvard Dataverse doi:10.7910/DVN/DGUMFI, version 1.1).",
        "role": "County presidential returns 1988-2000 (placebo outcomes, 1992/1996 controls, state 1996 shares, cross-check)",
    },
    {
        "name": "algara_amlani_manual",
        "file": "County_Level_Dataset_Manual_READ_ME.pdf",
        "url": "https://dataverse.harvard.edu/api/access/datafile/5028533",
        "sha256": "0143e6dc05cf6d86db8b100ce7f3d2f981d1bc2f563d3f0119b92f4511cfab1e",
        "licence": "CC0 1.0 (same dataset).",
        "role": "Codebook (documentation only)",
    },
    {
        "name": "cbpp_tpr",
        "file": "2025-04-11-TPR-1978-2023.xls",
        "url": f"{WAYBACK}/20250420040351id_/https://www.cbpp.org/sites/default/files/2025-04-11-TPR-1978-2023.xls",
        "sha256": "d6ef9b16745e927c1fcdd567da1e9b08d661c8f8a180c9d65dd92e1c3ec0e27b",
        "licence": "Center on Budget and Policy Priorities; noncommercial reproduction with attribution, no derivative databases (cbpp.org terms of use). Retrieved from the Internet Archive capture because cbpp.org refuses automated clients. Not redistributed.",
        "role": "State AFDC/TANF-to-poverty ratios, two-year averages, 1978-79 to 2022-23 (moderator)",
    },
    {
        "name": "wrd_2016",
        "file": "2016_welfare_rules_databook.pdf",
        "url": f"{WAYBACK}/20250113180305id_/https://www.acf.hhs.gov/sites/default/files/documents/opre/2016_welfare_rules_databook_final_10_30_17_b508_2.pdf",
        "sha256": "7cfeca5375d2ddbcf016ba19a0d8516f05bb5560b70b5b0d59056a8c36668140",
        "licence": "Public domain (OPRE Report 2017-82 states: 'This report is in the public domain').",
        "role": "Table L5 maximum benefits, July 1996 and July 2016 (transcribed to data/wrd_table_l5.csv)",
    },
    {
        "name": "cbp_2000",
        "file": "cbp00co.zip",
        "url": "https://www2.census.gov/programs-surveys/cbp/datasets/2000/cbp00co.zip",
        "sha256": "a57c70e9561c475edb9307eb241e84aea880e2df35666d33d46ebe385992f9cd",
        "licence": "U.S. Census Bureau County Business Patterns; public domain (U.S. government work).",
        "role": "County manufacturing and total employment, 2000 (alternative shock)",
    },
    {
        "name": "cbp_2008",
        "file": "cbp08co.zip",
        "url": "https://www2.census.gov/programs-surveys/cbp/datasets/2008/cbp08co.zip",
        "sha256": "baa2e780c028b03cecc80542a0a43cfc7c81c95673a676f7baa913a97ad5ca38",
        "licence": "U.S. Census Bureau County Business Patterns; public domain (U.S. government work).",
        "role": "County manufacturing employment, 2008 (alternative shock)",
    },
    {
        "name": "fec_2016",
        "file": "federalelections2016.xlsx",
        "url": "https://www.fec.gov/documents/1890/federalelections2016.xlsx",
        "sha256": "b4a1d1383602bc388cfbdf1fbea2476476d32e0b44b44236d3a3910fa9782eb6",
        "licence": "Federal Election Commission, Federal Elections 2016; public domain (U.S. government work).",
        "role": "Official 2016 presidential popular vote by state (margins for the bridge)",
    },
]

# The BLS API response embeds a response time, so the series values are
# normalised before hashing.
CPI_QUERIES = [("CUUR0000SA0", "1996"), ("CUUR0000SA0", "2016")]
CPI_FILE = "bls_cpiu_july_1996_2016.json"
CPI_SHA256 = "e4525f426049ab5290d0fdcc04095bcbb7e786da7664da53cdc8cca8b705af77"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def get(url: str, data: bytes | None = None, headers: dict | None = None) -> bytes:
    hdr = {"User-Agent": UA}
    hdr.update(headers or {})
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, data=data, headers=hdr)
            with urllib.request.urlopen(req, timeout=180) as r:
                return r.read()
        except OSError:
            if attempt == 3:
                raise
            time.sleep(2 * (attempt + 1))
    raise RuntimeError("unreachable")


def fetch_cpi(dest: Path) -> None:
    rows = []
    for series, year in CPI_QUERIES:
        body = json.dumps({"seriesid": [series], "startyear": year, "endyear": year}).encode()
        raw = json.loads(get("https://api.bls.gov/publicAPI/v1/timeseries/data/", body,
                             {"Content-Type": "application/json"}))
        if raw.get("status") != "REQUEST_SUCCEEDED":
            raise RuntimeError(f"BLS request failed: {raw.get('message')}")
        for obs in raw["Results"]["series"][0]["data"]:
            if obs["periodName"] == "July":
                rows.append({"series": series, "year": int(obs["year"]), "period": "July",
                             "value": obs["value"]})
    rows.sort(key=lambda r: r["year"])
    dest.write_text(json.dumps({"source": "U.S. Bureau of Labor Statistics, CPI-U, U.S. city average, all items, not seasonally adjusted (public domain)",
                                "observations": rows}, indent=1, sort_keys=True) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--record", action="store_true", help="report hashes of unpinned files instead of failing")
    args = ap.parse_args()
    RAW.mkdir(parents=True, exist_ok=True)
    log = {
        "fetched_at_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "brief_md_sha256_at_fetch": sha256(BRIEF),
        "files": [],
    }
    ok = True
    entries = list(SOURCES) + [{"name": "bls_cpi", "file": CPI_FILE, "url": "https://api.bls.gov/publicAPI/v1/timeseries/data/ (POST, normalised)",
                                 "sha256": CPI_SHA256, "licence": "U.S. Bureau of Labor Statistics; public domain.",
                                 "role": "July CPI-U, 1996 and 2016 (real benefit deflator)"}]
    for src in entries:
        dest = RAW / src["file"]
        if not dest.exists():
            print(f"downloading {src['name']} ...", flush=True)
            if src["name"] == "bls_cpi":
                fetch_cpi(dest)
            else:
                dest.write_bytes(get(src["url"]))
        digest = sha256(dest)
        status = "verified"
        if src["sha256"] is None:
            status = "unpinned"
            print(f"UNPINNED {src['name']}: {digest}")
            if not args.record:
                ok = False
        elif digest != src["sha256"]:
            status = "MISMATCH"
            ok = False
            print(f"MISMATCH {src['name']}: expected {src['sha256']}, got {digest}")
        log["files"].append({"name": src["name"], "file": f"data/raw/{src['file']}", "url": src["url"],
                             "sha256": digest, "bytes": dest.stat().st_size, "status": status,
                             "licence": src["licence"], "role": src["role"]})
    LOG.write_text(json.dumps(log, indent=1) + "\n")
    print("fetch log written to", LOG)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
