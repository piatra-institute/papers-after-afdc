"""Specifications fixed in the project brief (see ../../brief.md, "Analysis plan") and checks added after review."""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

from . import data as D
from .estimators import iv2sls, ols, wild_cluster_bootstrap

CONTROLS = D.ADHM_CONTROLS_CZ + D.ADHM_CONTROLS_DEMOG + ["AA_R1992", "AA_R1996"]
CONTROLS_NO_ELECTION = D.ADHM_CONTROLS_CZ + D.ADHM_CONTROLS_DEMOG
BOOT_SEED = 20261118
BOOT_REPS = 9999
TWOWAY = "state+czone"


def state_table(p: pd.DataFrame) -> pd.DataFrame:
    cols = ["tpr_1996", "tpr_2008", "tpr_2016", "tpr_1979", "erosion", "erosion_2008",
            "pre_reform_decline", "benefit_1996", "benefit_2016_nominal", "benefit_2016_real96",
            "real_benefit_decline_pct", "state_R1996", "state_mean_shock", "south",
            "tpr_9394", "tpr_9900", "tpr_1314", "erosion_9394", "erosion_4yr", "log_poverty_growth"]
    return p.groupby("state")[cols].first()


def add_moderators(p: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Centred primary moderator and standardized alternatives (larger = less protection)."""
    st = state_table(p)
    p = p.copy()
    info = {}
    oriented = {
        "erosion": st["erosion"],
        "neg_tpr_2016": -st["tpr_2016"],
        "neg_real_benefit_2016": -st["benefit_2016_real96"],
        "real_benefit_decline_pct": st["real_benefit_decline_pct"],
        "neg_benefit_1996": -st["benefit_1996"],
        "erosion_2008": st["erosion_2008"],
        "pre_reform_decline": st["pre_reform_decline"],
        "erosion_9394": st["erosion_9394"],
        "erosion_4yr": st["erosion_4yr"],
    }
    for name, s in oriented.items():
        mu, sd = float(s.mean()), float(s.std(ddof=1))
        p[f"{name}_c"] = p["state"].map(s) - mu
        p[f"{name}_z"] = p[f"{name}_c"] / sd
        info[name] = {"state_mean": mu, "state_sd": sd, "min": float(s.min()), "max": float(s.max()),
                      "p25": float(s.quantile(0.25)), "p75": float(s.quantile(0.75))}
    corr = pd.DataFrame(oriented).corr()
    info["correlation_with_erosion"] = {k: float(corr.loc["erosion", k]) for k in oriented}
    # competing moderators, centred
    p["white_c"] = p["l_sh_pop_white"] - p["l_sh_pop_white"].mean()
    p["south_c"] = p["south"] - p["south"].mean()
    p["stateR1996_c"] = p["state"].map(st["state_R1996"]) - st["state_R1996"].mean()
    p["stateshock_c"] = p["state"].map(st["state_mean_shock"]) - st["state_mean_shock"].mean()
    info["competing_correlation_with_erosion_state_level"] = {
        "south": float(np.corrcoef(st["erosion"], st["south"])[0, 1]),
        "state_R1996": float(np.corrcoef(st["erosion"], st["state_R1996"])[0, 1]),
        "state_mean_shock": float(np.corrcoef(st["erosion"], st["state_mean_shock"])[0, 1]),
    }
    return p, info


def _state_dummies(p):
    return pd.get_dummies(p["state"], prefix="st", dtype=float)


def _region_dummies(p):
    return p[D.ADHM_REGIONS].astype(float).assign(const=1.0)


def clusters(p):
    return {"state": p["state"].to_numpy(), "czone": p["czone"].to_numpy()}


def run_iv(p, y, mods=("erosion_c",), shock="shock", iv="iv", controls=CONTROLS, fe="state",
           weighted=True, extra_endog=None, weight_col="weight"):
    """2SLS with endogenous [shock, shock*m for m in mods] and instruments [iv, iv*m]."""
    Xn = pd.DataFrame({shock: p[shock]})
    Ze = pd.DataFrame({iv: p[iv]})
    for m in mods:
        Xn[f"{shock}_x_{m}"] = p[shock] * p[m]
        Ze[f"{iv}_x_{m}"] = p[iv] * p[m]
    exog = p[list(controls)].astype(float)
    exog = pd.concat([exog, _state_dummies(p) if fe == "state" else _region_dummies(p)], axis=1)
    w = p[weight_col].to_numpy() if weighted else None
    fit = iv2sls(p[y].to_numpy(), Xn.to_numpy(), exog.to_numpy(), Ze.to_numpy(),
                 list(Xn.columns), list(exog.columns), w=w, clusters=clusters(p),
                 first_stage_cluster="state" if fe == "state" else "czone")
    return fit


def run_ols(p, y, regs, controls=CONTROLS, weighted=True):
    X = pd.concat([p[list(regs)].astype(float), p[list(controls)].astype(float), _state_dummies(p)], axis=1)
    w = p["weight"].to_numpy() if weighted else None
    return ols(p[y].to_numpy(), X.to_numpy(), list(X.columns), w=w, clusters=clusters(p)), X, w


def summarize(fit, name, kinds=(TWOWAY, "state", "czone")):
    out = {"coef": float(fit.coef[fit.index(name)])}
    for k in kinds:
        df = fit.nclusters[k] - 1
        lo, hi = fit.ci(name, k, df=df)
        out[k] = {"se": fit.se(name, k), "ci95": [lo, hi], "p": fit.pvalue(name, k, df=df),
                  "t_df": df}
    return out


def interaction_block(fit, mod, info_mod=None):
    name = f"shock_x_{mod}"
    blk = {"gamma": summarize(fit, name), "beta_at_mean": summarize(fit, "shock"), "nobs": fit.nobs,
           "clusters": fit.nclusters, "first_stage": fit.first_stage}
    return blk


def outcome(p, a, b, src="MEDSL"):
    if src == "MEDSL":
        return p[f"R{b}"] - p[f"R{a}"]
    return p[f"AA_R{b}"] - p[f"AA_R{a}"]


def binned_effects(p, y, mod="erosion"):
    """Descriptive: shock effect by tercile of the moderator (states split 16/16/16)."""
    st = state_table(p)
    ranks = st[mod].rank(method="first")
    terc = pd.cut(ranks, [0, 16, 32, 48], labels=[0, 1, 2]).astype(int)
    p = p.copy()
    p["terc"] = p["state"].map(terc)
    Xn = pd.DataFrame({f"shock_t{k}": p["shock"] * (p["terc"] == k) for k in range(3)})
    Ze = pd.DataFrame({f"iv_t{k}": p["iv"] * (p["terc"] == k) for k in range(3)})
    exog = pd.concat([p[CONTROLS].astype(float), _state_dummies(p)], axis=1)
    fit = iv2sls(p[y].to_numpy(), Xn.to_numpy(), exog.to_numpy(), Ze.to_numpy(), list(Xn.columns),
                 list(exog.columns), w=p["weight"].to_numpy(), clusters=clusters(p))
    out = []
    for k in range(3):
        states = sorted(terc[terc == k].index)
        s = summarize(fit, f"shock_t{k}", kinds=(TWOWAY,))
        out.append({"tercile": k + 1, "states": states, "mean_erosion": float(st.loc[states, mod].mean()),
                    "min_erosion": float(st.loc[states, mod].min()), "max_erosion": float(st.loc[states, mod].max()),
                    "effect": s["coef"], "ci95": s[TWOWAY]["ci95"], "se": s[TWOWAY]["se"]})
    return out


def bridge(p, fit, info, fec):
    """Net Democratic-minus-Republican margin change from setting erosion to M*."""
    g = float(fit.coef[fit.index("shock_x_erosion_c")])
    df = fit.nclusters[TWOWAY] - 1
    lo, hi = fit.ci("shock_x_erosion_c", TWOWAY, df=df)
    mins = info["erosion"]["min"]
    res = {"gamma": g, "gamma_ci95": [lo, hi], "counterfactuals": {}}
    st_min_name = state_table(p)["erosion"].idxmin()
    for label, mstar in [("retain_1996", 0.0), ("least_eroded_state", mins)]:
        rows = {}
        for st_name, po in D.STATE_PO.items():
            q = p[p["state"] == st_name]
            S = float(np.sum(2 * q["shock"] * (q["erosion"] - mstar) * q["twoparty2016"] / 100))
            margin = int(fec.loc[fec["state_po"] == po, "trump_margin"].iloc[0])
            vals = sorted([g * S, lo * S, hi * S])
            rows[po] = {"state_erosion": float(q["erosion"].iloc[0]), "exposure_sum_S": S,
                        "net_dem_margin_change": g * S, "ci95": [lo * S, hi * S],
                        "trump_margin_fec": margin, "gamma_needed_to_flip": margin / S,
                        "point_exceeds_margin": bool(g * S > margin),
                        "ci_includes_flip": bool(max(lo * S, hi * S) > margin),
                        "ci_upper_over_margin": max(lo * S, hi * S) / margin,
                        "twoparty_votes_2016": int(q["twoparty2016"].sum()),
                        "counties": int(len(q))}
        res["counterfactuals"][label] = {"mstar": mstar, "states": rows}
    res["least_eroded_state"] = st_min_name
    return res


def adhm_replication(p):
    y = "dR_2000_2016"
    fit = run_iv(p, y, mods=(), controls=CONTROLS, fe="region")
    s = summarize(fit, "shock", kinds=("czone",))
    return {"coef": s["coef"], "se_cz": s["czone"]["se"], "published_coef": 1.71, "published_se": 0.90,
            "nobs": fit.nobs, "first_stage_F_cz": fit.first_stage["shock"]["F_cluster"]}


def main_effect_state_fe(p, y):
    fit = run_iv(p, y, mods=())
    return summarize(fit, "shock")


def adhm_own_file():
    """Validation only: ADHM Table 5, panel B, column 6 on ADHM's published analysis file
    (its Leip-derived vote shares are read here and nowhere else)."""
    import io
    import zipfile
    with zipfile.ZipFile(D.RAW_FILES["adhm"]) as z:
        a = pd.read_stata(io.BytesIO(z.read("2-FinalDataPackage/dta/president_2000_2016.dta")))
    out = {"published_coef": 1.71, "published_se": 0.90}
    for label, keep in [("all", np.ones(len(a), bool)), ("no_dc", (a["cty_fips"].astype(int) != 11001).to_numpy())]:
        b = a[keep]
        y = (b["shnr_pres2016"] - b["shnr_pres2000"]).to_numpy()
        ctr = D.ADHM_CONTROLS_CZ + D.ADHM_CONTROLS_DEMOG + ["shnr_pres1992", "shnr_pres1996"]
        exog = pd.concat([b[ctr].astype(float), b[D.ADHM_REGIONS].astype(float).assign(const=1.0)], axis=1)
        fit = iv2sls(y, b[["d_imp_usch_pd_0008"]].to_numpy(float), exog.to_numpy(), b[["d_imp_otch_lag_pd_0008"]].to_numpy(float),
                     ["shock"], list(exog.columns), w=b["totvote_2000pres"].to_numpy(float),
                     clusters={"czone": b["czone"].to_numpy()}, first_stage_cluster="czone")
        res = {"coef": float(fit.coef[0]), "se_cz": fit.se("shock", "czone"), "nobs": fit.nobs}
        if label == "all":
            out.update(res)
        else:
            out["no_dc"] = res
    return out
