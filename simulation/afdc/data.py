"""Build the county analysis panel from the frozen raw inputs.

Every reader here works on files written by fetch_data.py (data/raw/) or on the
committed transcription data/wrd_table_l5.csv. Nothing is downloaded.
"""
from __future__ import annotations

import io
import json
import re
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent.parent
RAW = HERE / "data" / "raw"
DATA = HERE / "data"

# 1990-definition county codes used by the ADHM sample (mapping fixed in the brief).
FIPS_TO_1990 = {46102: 46113, 12086: 12025, 51515: 51019, 51560: 51005, 51780: 51083}
EXCLUDED_FIPS = {8014}  # Broomfield, created 2001; excluded as in ADHM

STATE_FIPS = {
    1: "Alabama", 2: "Alaska", 4: "Arizona", 5: "Arkansas", 6: "California", 8: "Colorado",
    9: "Connecticut", 10: "Delaware", 11: "District of Columbia", 12: "Florida", 13: "Georgia",
    15: "Hawaii", 16: "Idaho", 17: "Illinois", 18: "Indiana", 19: "Iowa", 20: "Kansas",
    21: "Kentucky", 22: "Louisiana", 23: "Maine", 24: "Maryland", 25: "Massachusetts",
    26: "Michigan", 27: "Minnesota", 28: "Mississippi", 29: "Missouri", 30: "Montana",
    31: "Nebraska", 32: "Nevada", 33: "New Hampshire", 34: "New Jersey", 35: "New Mexico",
    36: "New York", 37: "North Carolina", 38: "North Dakota", 39: "Ohio", 40: "Oklahoma",
    41: "Oregon", 42: "Pennsylvania", 44: "Rhode Island", 45: "South Carolina",
    46: "South Dakota", 47: "Tennessee", 48: "Texas", 49: "Utah", 50: "Vermont",
    51: "Virginia", 53: "Washington", 54: "West Virginia", 55: "Wisconsin", 56: "Wyoming",
}
STATE_PO = {"Michigan": "MI", "Wisconsin": "WI", "Pennsylvania": "PA"}

ADHM_CONTROLS_CZ = ["l_shind_manuf_cbp", "l_sh_routine33", "l_task_outsource"]
ADHM_CONTROLS_DEMOG = [
    "l_sh_pop_f", "l_sh_pop_edu_c", "l_sh_fborn", "l_sh_pop_age_1019", "l_sh_pop_age_2029",
    "l_sh_pop_age_3039", "l_sh_pop_age_4049", "l_sh_pop_age_5059", "l_sh_pop_age_6069",
    "l_sh_pop_age_7079", "l_sh_pop_age_8000", "l_sh_pop_white", "l_sh_pop_black",
    "l_sh_pop_asian", "l_sh_pop_hispanic",
]
ADHM_REGIONS = ["reg_midatl", "reg_encen", "reg_wncen", "reg_satl", "reg_escen", "reg_wscen",
                "reg_mount", "reg_pacif"]

RAW_FILES = {
    "adhm": RAW / "ADHM-PoliticalPolarization-FileArchive.zip",
    "cw": RAW / "cw_cty_czone.zip",
    "medsl": RAW / "countypres_2000-2016.csv",
    "aa": RAW / "dataverse_shareable_presidential_county_returns_1868_2020.Rdata",
    "cbpp": RAW / "2025-04-11-TPR-1978-2023.xls",
    "cbp2000": RAW / "cbp00co.zip",
    "cbp2008": RAW / "cbp08co.zip",
    "fec": RAW / "federalelections2016.xlsx",
    "cpi": RAW / "bls_cpiu_july_1996_2016.json",
    "cpi_monthly": RAW / "bls_cpiu_monthly_2000_2008.json",
    "bea_ca35": RAW / "bea_ca35_2011.zip",
    "bea_ca13": RAW / "bea_ca1-3_2011.zip",
    "wrd": DATA / "wrd_table_l5.csv",
}


def to_1990(fips: pd.Series) -> pd.Series:
    f = fips.astype(int)
    return f.map(lambda x: FIPS_TO_1990.get(x, x))


# --------------------------------------------------------------------------- shock and controls

def load_adhm() -> pd.DataFrame:
    """Trade shock, instrument and 2000 controls. Vote-share columns (Leip-derived) are not read."""
    keep = ["cty_fips", "czone", "d_imp_usch_pd_0008", "d_imp_otch_lag_pd_0008", "totvote_2000pres"] \
        + ADHM_CONTROLS_CZ + ADHM_CONTROLS_DEMOG + ADHM_REGIONS
    with zipfile.ZipFile(RAW_FILES["adhm"]) as z:
        raw = z.read("2-FinalDataPackage/dta/president_2000_2016.dta")
    df = pd.read_stata(io.BytesIO(raw), columns=keep)
    df["cty_fips"] = df["cty_fips"].astype(int)
    df["czone"] = df["czone"].astype(int)
    df["state_fips"] = df["cty_fips"] // 1000
    df = df.rename(columns={"d_imp_usch_pd_0008": "shock", "d_imp_otch_lag_pd_0008": "iv",
                            "totvote_2000pres": "adhm_totvote_2000"})
    df["reg_neweng"] = 1.0 - df[ADHM_REGIONS].sum(axis=1)
    df["south"] = df[["reg_satl", "reg_escen", "reg_wscen"]].sum(axis=1)
    return df


def load_crosswalk() -> pd.DataFrame:
    with zipfile.ZipFile(RAW_FILES["cw"]) as z:
        cw = pd.read_stata(io.BytesIO(z.read("cw_cty_czone.dta")))
    cw["cty_fips"] = cw["cty_fips"].astype(int)
    cw["czone"] = cw["czone"].astype(int)
    return cw


# --------------------------------------------------------------------------- election returns

def load_medsl() -> pd.DataFrame:
    """County-year Republican, Democratic and total votes, 2000-2016, 1990 county codes."""
    m = pd.read_csv(RAW_FILES["medsl"], dtype={"FIPS": "Int64"})
    m = m[m["FIPS"].notna()].copy()
    # Kansas City, Missouri (reporting unit 36000, 2004-2016) votes within Jackson County.
    m["fips"] = to_1990(m["FIPS"].astype(int).replace({36000: 29095}))
    m = m[~m["fips"].isin(EXCLUDED_FIPS)]
    m["candidatevotes"] = m["candidatevotes"].fillna(0)
    rep = m[m["party"] == "republican"].groupby(["year", "fips"])["candidatevotes"].sum()
    dem = m[m["party"] == "democrat"].groupby(["year", "fips"])["candidatevotes"].sum()
    # Total presidential votes are summed over candidate rows (including "Other"). The
    # file's totalvotes field repeats the county value for same-name Virginia cities.
    tot = m.groupby(["year", "fips"])["candidatevotes"].sum()
    out = pd.concat({"rep": rep, "dem": dem, "total": tot}, axis=1).reset_index()
    return out


def load_algara_amlani() -> pd.DataFrame:
    import pyreadr

    r = pyreadr.read_r(str(RAW_FILES["aa"]))
    a = r["pres_elections_release"]
    a = a[a["election_year"].isin([1988, 1992, 1996, 2000, 2016])].copy()
    a = a[a["fips"].str.fullmatch(r"\d{5}")]
    a["fips"] = to_1990(a["fips"].astype(int))
    a = a[~a["fips"].isin(EXCLUDED_FIPS)]
    g = a.groupby(["election_year", "fips"]).agg(rep=("republican_raw_votes", "sum"),
                                                 dem=("democratic_raw_votes", "sum"),
                                                 total=("raw_county_vote_totals", "sum")).reset_index()
    return g.rename(columns={"election_year": "year"})


def rep_share(df: pd.DataFrame) -> pd.Series:
    return 100 * df["rep"] / (df["rep"] + df["dem"])


def load_fec_margins() -> pd.DataFrame:
    d = pd.read_excel(RAW_FILES["fec"], "Table 2. Electoral &  Pop Vote", header=None)
    d = d.iloc[4:, [0, 3, 4, 5, 6]]
    d.columns = ["state_po", "trump", "clinton", "others", "total"]
    d = d[d["state_po"].isin(STATE_PO.values())].copy()
    for c in ["trump", "clinton", "others", "total"]:
        d[c] = d[c].astype(int)
    d["trump_margin"] = d["trump"] - d["clinton"]
    return d.reset_index(drop=True)


# --------------------------------------------------------------------------- moderators

def load_cbpp() -> pd.DataFrame:
    raw = pd.read_excel(RAW_FILES["cbpp"], "50-State Ratios 1979-2023", header=None)
    hdr = raw.iloc[1].tolist()
    d = raw.iloc[2:].copy()
    d.columns = ["state"] + hdr[1:]
    d = d[d["state"].isin(STATE_FIPS.values())].set_index("state")
    d = d.apply(pd.to_numeric, errors="coerce")
    return d


def load_cbpp_poverty() -> pd.DataFrame:
    raw = pd.read_excel(RAW_FILES["cbpp"], "Poverty (2 yr)", header=None)
    hdr = raw.iloc[1].tolist()
    d = raw.iloc[2:].copy()
    d.columns = ["state"] + hdr[1:]
    d = d[d["state"].isin(STATE_FIPS.values())].set_index("state")
    return d.apply(pd.to_numeric, errors="coerce")


def load_cpi() -> dict[int, float]:
    obs = json.loads(RAW_FILES["cpi"].read_text())["observations"]
    return {o["year"]: float(o["value"]) for o in obs}


def state_moderators() -> pd.DataFrame:
    """State-level moderators in natural units (larger = less cash protection where noted)."""
    t = load_cbpp()
    w = pd.read_csv(RAW_FILES["wrd"]).set_index("state")
    cpi = load_cpi()
    defl = cpi[1996] / cpi[2016]
    s = pd.DataFrame(index=t.index)
    s["tpr_1996"] = t["95-96"]
    s["tpr_2008"] = t["07-08"]
    s["tpr_2016"] = t["15-16"]
    s["tpr_1979"] = t["78-79"]
    s["tpr_9394"] = t["93-94"]
    s["tpr_9900"] = t["99-00"]
    s["tpr_1314"] = t["13-14"]
    s["erosion"] = s["tpr_1996"] - s["tpr_2016"]
    s["erosion_2008"] = s["tpr_1996"] - s["tpr_2008"]
    s["pre_reform_decline"] = s["tpr_1979"] - s["tpr_1996"]
    # revision round 1 (post hoc): alternative bases and averaging windows
    s["erosion_9394"] = s["tpr_9394"] - s["tpr_2016"]
    s["erosion_4yr"] = (t["93-94"] + t["95-96"]) / 2 - (t["13-14"] + t["15-16"]) / 2
    pov = load_cbpp_poverty()
    s["log_poverty_growth"] = np.log(pov["15-16"] / pov["95-96"])
    s["benefit_1996"] = w["benefit_july1996"]
    s["benefit_2016_nominal"] = w["benefit_july2016"]
    s["benefit_2016_real96"] = w["benefit_july2016"] * defl
    s["real_benefit_decline_pct"] = 100 * (1 - s["benefit_2016_real96"] / s["benefit_1996"])
    s["cpi_deflator_2016_to_1996"] = defl
    return s


# --------------------------------------------------------------------------- County Business Patterns

CBP_MIDPOINT = {"A": 10, "B": 60, "C": 175, "E": 375, "F": 750, "G": 1750, "H": 3750, "I": 7500,
                "J": 17500, "K": 37500, "L": 75000, "M": 100000}


def _cbp_county(path: Path) -> pd.DataFrame:
    with zipfile.ZipFile(path) as z:
        name = [n for n in z.namelist() if n.lower().endswith(".txt")][0]
        d = pd.read_csv(io.BytesIO(z.read(name)), dtype=str)
    d.columns = [c.lower() for c in d.columns]
    d = d[d["naics"].isin(["------", "31----"])].copy()
    emp = pd.to_numeric(d["emp"], errors="coerce").fillna(0)
    flag = d["empflag"].fillna("").str.strip()
    imputed = flag.map(CBP_MIDPOINT)
    d["emp_imp"] = np.where(flag.isin(CBP_MIDPOINT.keys()), imputed, emp)
    d["fips"] = (d["fipstate"].astype(int) * 1000 + d["fipscty"].astype(int))
    d = d[d["fipscty"].astype(int) != 999]  # statewide records
    d["fips"] = to_1990(d["fips"])
    d.loc[d["fips"] == 8014, "fips"] = 8013  # Broomfield to Boulder for CZ aggregation
    piv = d.pivot_table(index="fips", columns="naics", values="emp_imp", aggfunc="sum").fillna(0)
    return piv.rename(columns={"------": "total", "31----": "mfg"})


def cbp_shock() -> pd.DataFrame:
    """CZ decline in manufacturing employment 2000-2008 as a percentage of 2000 total employment."""
    cw = load_crosswalk().set_index("cty_fips")["czone"]
    c00 = _cbp_county(RAW_FILES["cbp2000"])
    c08 = _cbp_county(RAW_FILES["cbp2008"])
    df = pd.DataFrame({"mfg2000": c00["mfg"], "tot2000": c00["total"]}).join(
        c08[["mfg"]].rename(columns={"mfg": "mfg2008"}), how="outer").fillna(0)
    df["czone"] = df.index.map(cw)
    unmatched = int(df["czone"].isna().sum())
    cz = df.dropna(subset=["czone"]).groupby("czone")[["mfg2000", "mfg2008", "tot2000"]].sum()
    cz["cbp_shock"] = 100 * (cz["mfg2000"] - cz["mfg2008"]) / cz["tot2000"]
    cz.index = cz.index.astype(int)
    cz.attrs["unmatched_counties"] = unmatched
    return cz


# --------------------------------------------------------------------------- panel

def build_panel() -> tuple[pd.DataFrame, dict]:
    adhm = load_adhm()
    medsl = load_medsl()
    aa = load_algara_amlani()
    mods = state_moderators()

    p = adhm.copy()
    p["state"] = p["state_fips"].map(STATE_FIPS)
    diag = {"adhm_counties": int(len(p))}

    for yr in [2000, 2008, 2012, 2016]:
        m = medsl[medsl["year"] == yr].set_index("fips")
        p[f"R{yr}"] = p["cty_fips"].map(rep_share(m))
        p[f"twoparty{yr}"] = p["cty_fips"].map(m["rep"] + m["dem"])
        p[f"total{yr}"] = p["cty_fips"].map(m["total"])
        p[f"repvotes{yr}"] = p["cty_fips"].map(m["rep"])
        p[f"demvotes{yr}"] = p["cty_fips"].map(m["dem"])
    for yr in [1988, 1992, 1996, 2000, 2016]:
        a = aa[aa["year"] == yr].set_index("fips")
        p[f"AA_R{yr}"] = p["cty_fips"].map(rep_share(a))
        p[f"AA_twoparty{yr}"] = p["cty_fips"].map(a["rep"] + a["dem"])

    # state 1996 Republican two-party share from county sums
    a96 = aa[aa["year"] == 1996].copy()
    a96["state_fips"] = a96["fips"] // 1000
    st96 = a96.groupby("state_fips")[["rep", "dem"]].sum()
    p["state_R1996"] = p["state_fips"].map(100 * st96["rep"] / (st96["rep"] + st96["dem"]))

    p = p.join(mods, on="state")
    cz = cbp_shock()
    p["cbp_shock"] = p["czone"].map(cz["cbp_shock"])
    diag["cbp_unmatched_counties"] = cz.attrs["unmatched_counties"]

    p["weight"] = p["total2000"]
    # analysis sample: contiguous states with a CBPP value (drops DC)
    p = p[p["state"].notna() & p["erosion"].notna()].copy()
    diag["sample_counties_before_missing"] = int(len(p))
    need = ["R2000", "R2016", "AA_R1992", "AA_R1996", "weight", "cbp_shock"]
    missing = p[p[need].isna().any(axis=1)]
    diag["dropped_missing"] = missing["cty_fips"].tolist()
    p = p.dropna(subset=need)
    diag["sample_counties"] = int(len(p))
    diag["states"] = int(p["state"].nunique())
    diag["czones"] = int(p["czone"].nunique())
    # weighted state mean of the shock (competing moderator listed in the brief)
    sm = p.groupby("state").apply(lambda g: np.average(g["shock"], weights=g["weight"]), include_groups=False)
    p["state_mean_shock"] = p["state"].map(sm)
    return p.reset_index(drop=True), diag


# --------------------------------------------------------------------------- BEA transfers (revision round 1)

def _bea_lines(path: Path, lines: dict[str, str], years=("2000", "2008")) -> pd.DataFrame:
    """County values from an April 2011 BEA regional zip (one CSV per state).
    (L) means less than $50,000 and is set to the midpoint, $25,000; other codes are missing."""
    frames = []
    with zipfile.ZipFile(path) as z:
        for n in z.namelist():
            if not re.fullmatch(r"CA[0-9-]+_[A-Z]{2}\.csv", n):
                continue
            d = pd.read_csv(io.BytesIO(z.read(n)), dtype=str, encoding="latin-1")
            d = d[d["Line code"].notna()]
            d["code"] = d["Line code"].str.strip()
            d = d[d["code"].isin(lines)]
            d["fips"] = pd.to_numeric(d["FIPS"].str.strip(), errors="coerce")
            frames.append(d)
    d = pd.concat(frames)
    d = d[d["fips"].notna() & (d["fips"] % 1000 != 0)]
    out = {}
    for code, name in lines.items():
        q = d[d["code"] == code].set_index("fips")
        for y in years:
            v = q[y].str.strip().replace({"(L)": "25"})
            out[f"{name}{y}"] = pd.to_numeric(v, errors="coerce")
    res = pd.DataFrame(out)
    res.index = to_1990(pd.Series(res.index.astype(int), index=res.index)).values
    return res.groupby(level=0).sum(min_count=1)


def load_bea_transfers() -> pd.DataFrame:
    """Per-capita county transfers in 2000 dollars, 2000 and 2008, from the April 2011 BEA release."""
    tr = _bea_lines(RAW_FILES["bea_ca35"], {"140": "fa", "170": "ui", "150": "snap"})
    pop = _bea_lines(RAW_FILES["bea_ca13"], {"2": "pop"})
    obs = json.loads(RAW_FILES["cpi_monthly"].read_text())["observations"]
    cpi = {y: np.mean([float(o["value"]) for o in obs if o["year"] == y]) for y in (2000, 2008)}
    defl = cpi[2000] / cpi[2008]
    df = tr.join(pop, how="inner")
    for k in ("fa", "ui", "snap"):
        pc00 = 1000 * df[f"{k}2000"] / df["pop2000"]
        pc08 = 1000 * df[f"{k}2008"] * defl / df["pop2008"]
        df[f"{k}_pc2000"] = pc00
        df[f"d_{k}_pc"] = pc08 - pc00
    df.attrs["cpi_2000"] = cpi[2000]
    df.attrs["cpi_2008"] = cpi[2008]
    return df
