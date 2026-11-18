"""Run every pre-registered analysis and write output/results.json and the figures.

Reads only frozen inputs (data/raw/ written by fetch_data.py, data/wrd_table_l5.csv).
"""
from __future__ import annotations

import hashlib
import json
import platform
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from afdc import analysis as A  # noqa: E402
from afdc import data as D  # noqa: E402
from afdc.estimators import wild_cluster_bootstrap  # noqa: E402

OUT = HERE / "output"
FIG = HERE.parent / "paper" / "figures"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    OUT.mkdir(exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)
    p, diag = D.build_panel()
    p, modinfo = A.add_moderators(p)
    for a, b in [(2000, 2016), (2012, 2016), (2000, 2008), (2000, 2012)]:
        p[f"dR_{a}_{b}"] = A.outcome(p, a, b)
    p["dR_1992_1996"] = A.outcome(p, 1992, 1996, src="AA")
    p["dR_1996_2000"] = A.outcome(p, 1996, 2000, src="AA")

    R: dict = {"inputs": {k: {"file": str(v.relative_to(HERE)), "sha256": sha256(v)} for k, v in D.RAW_FILES.items()},
               "environment": {"python": platform.python_version(), "numpy": np.__version__, "pandas": pd.__version__},
               "sample": diag, "moderators": modinfo}
    st = A.state_table(p)
    full_states = {s: {k: (float(v) if pd.notna(v) else None) for k, v in row.items()} for s, row in st.iterrows()}
    # The CBPP terms bar derivative databases: CBPP-derived ratios are written only for the
    # states named in the paper; the full table is used in memory for Figure 1 only.
    named = {"Michigan", "Wisconsin", "Pennsylvania", "Oregon", "Missouri"}
    cbpp_fields = {"tpr_1996", "tpr_2008", "tpr_2016", "tpr_1979", "erosion", "erosion_2008", "pre_reform_decline"}
    R["state_table"] = {s: {k: v for k, v in row.items()
                            if (k not in cbpp_fields or s in named) and k != "state_mean_shock"}
                        for s, row in full_states.items()}
    R["state_table_note"] = ("CBPP-derived ratios are reported only for the five states named in the paper; "
                             "the ADHM-derived state mean shock is omitted.")

    # descriptive statistics
    w = p["weight"]
    R["descriptives"] = {
        "shock_weighted_mean": float(np.average(p["shock"], weights=w)),
        "shock_county_p25": float(p["shock"].quantile(0.25)),
        "shock_county_p75": float(p["shock"].quantile(0.75)),
        "dR_2000_2016_weighted_mean": float(np.average(p["dR_2000_2016"], weights=w)),
        "dR_2000_2016_weighted_sd": float(np.sqrt(np.cov(p["dR_2000_2016"], aweights=w))),
        "dR_2012_2016_weighted_mean": float(np.average(p["dR_2012_2016"], weights=w)),
        "erosion_state_mean": modinfo["erosion"]["state_mean"],
        "erosion_state_sd": modinfo["erosion"]["state_sd"],
        "tpr_1996_state_mean": float(st["tpr_1996"].mean()),
        "tpr_2016_state_mean": float(st["tpr_2016"].mean()),
        "states_with_erosion_positive": int((st["erosion"] > 0).sum()),
        "real_benefit_decline_state_mean": float(st["real_benefit_decline_pct"].mean()),
        "states_real_benefit_fell": int((st["real_benefit_decline_pct"] > 0).sum()),
        "cpi_deflator_2016_to_1996": float(p["cpi_deflator_2016_to_1996"].iloc[0]),
        "cbp_shock_weighted_mean": float(np.average(p["cbp_shock"], weights=w)),
        "corr_shock_cbp_shock_county": float(np.corrcoef(p["shock"], p["cbp_shock"])[0, 1]),
        "corr_erosion_tpr1996_states": float(np.corrcoef(st["erosion"], st["tpr_1996"])[0, 1]),
        "corr_erosion_tpr2016_states": float(np.corrcoef(st["erosion"], st["tpr_2016"])[0, 1]),
    }

    # V1: ADHM replication with open returns; V1b: the estimation code on ADHM's own file
    R["V1_adhm_replication"] = A.adhm_replication(p)
    R["V1b_adhm_own_file"] = A.adhm_own_file()
    # V2: MEDSL vs FEC for the three states
    fec = D.load_fec_margins()
    med = D.load_medsl()
    med16 = med[med["year"] == 2016].copy()
    med16["state_fips"] = med16["fips"] // 1000
    v2 = {}
    inv_state = {v: k for k, v in D.STATE_FIPS.items()}
    for st_name, po in D.STATE_PO.items():
        m = med16[med16["state_fips"] == inv_state[st_name]]
        f = fec[fec["state_po"] == po].iloc[0]
        v2[po] = {"medsl_trump": int(m["rep"].sum()), "medsl_clinton": int(m["dem"].sum()),
                  "fec_trump": int(f["trump"]), "fec_clinton": int(f["clinton"]),
                  "fec_trump_margin": int(f["trump_margin"]),
                  "medsl_trump_margin": int(m["rep"].sum() - m["dem"].sum())}
    v2["three_state_fec_margin_sum"] = int(sum(v2[po]["fec_trump_margin"] for po in D.STATE_PO.values()))
    R["V2_fec_check"] = v2

    # Primary specification
    prim = A.run_iv(p, "dR_2000_2016")
    R["primary"] = A.interaction_block(prim, "erosion_c")
    g = R["primary"]["gamma"]["coef"]
    R["primary"]["gamma_per_state_sd"] = g * modinfo["erosion"]["state_sd"]
    R["primary"]["gamma_per_sd_ci95"] = [c * modinfo["erosion"]["state_sd"] for c in R["primary"]["gamma"][A.TWOWAY]["ci95"]]
    iqr = modinfo["erosion"]["p75"] - modinfo["erosion"]["p25"]
    R["primary"]["effect_diff_p75_vs_p25"] = g * iqr
    R["primary"]["effect_diff_p75_vs_p25_ci95"] = [c * iqr for c in R["primary"]["gamma"][A.TWOWAY]["ci95"]]
    R["primary"]["erosion_iqr"] = iqr
    R["primary"]["shock_effect_at_p25_erosion"] = R["primary"]["beta_at_mean"]["coef"] + g * (modinfo["erosion"]["p25"] - modinfo["erosion"]["state_mean"])
    R["primary"]["shock_effect_at_p75_erosion"] = R["primary"]["beta_at_mean"]["coef"] + g * (modinfo["erosion"]["p75"] - modinfo["erosion"]["state_mean"])
    R["main_effect_state_fe_2000_2016"] = A.main_effect_state_fe(p, "dR_2000_2016")
    # Not pre-registered, descriptive: precision of the primary interaction
    from scipy import stats as _st
    se = R["primary"]["gamma"][A.TWOWAY]["se"]
    mult = float(_st.t.ppf(0.975, R["primary"]["gamma"][A.TWOWAY]["t_df"]) + _st.norm.ppf(0.80))
    R["primary"]["mde80"] = {"multiplier": mult, "gamma": mult * se,
                             "per_state_sd": mult * se * modinfo["erosion"]["state_sd"],
                             "note": "two-sided 5% test, 80% power, using the estimated two-way SE; descriptive, not pre-registered"}

    # Secondary window and time profile
    R["windows"] = {}
    for y in ["dR_2012_2016", "dR_2000_2008", "dR_2000_2012", "dR_2000_2016"]:
        f = A.run_iv(p, y)
        blk = A.interaction_block(f, "erosion_c")
        blk["gamma_per_state_sd"] = blk["gamma"]["coef"] * modinfo["erosion"]["state_sd"]
        R["windows"][y] = blk

    # R1 OLS, R2 unweighted
    f, X, wv = A.run_ols(p.assign(shock_x_erosion_c=p["shock"] * p["erosion_c"]), "dR_2000_2016",
                         ["shock", "shock_x_erosion_c"])
    R["R1_ols"] = {"gamma": A.summarize(f, "shock_x_erosion_c"), "beta_at_mean": A.summarize(f, "shock")}
    f = A.run_iv(p, "dR_2000_2016", weighted=False)
    R["R2_unweighted"] = A.interaction_block(f, "erosion_c")

    # R3 wild cluster bootstrap on the reduced form
    q = p.assign(iv_x_erosion_c=p["iv"] * p["erosion_c"])
    f, X, wv = A.run_ols(q, "dR_2000_2016", ["iv", "iv_x_erosion_c"])
    R["R3_reduced_form"] = {"gamma_rf": A.summarize(f, "iv_x_erosion_c")}
    R["R3_reduced_form"]["wild_bootstrap_state"] = wild_cluster_bootstrap(
        q["dR_2000_2016"].to_numpy(), X.to_numpy(), list(X.columns), "iv_x_erosion_c",
        q["state"].to_numpy(), w=wv, reps=A.BOOT_REPS, seed=A.BOOT_SEED)

    # R4 alternative moderators (standardized; larger = less protection)
    R["R4_alt_moderators"] = {}
    for m in ["erosion", "neg_tpr_2016", "neg_real_benefit_2016", "real_benefit_decline_pct",
              "neg_benefit_1996", "erosion_2008"]:
        f = A.run_iv(p, "dR_2000_2016", mods=(f"{m}_z",))
        R["R4_alt_moderators"][m] = A.interaction_block(f, f"{m}_z")

    # R5 competing moderators
    R["R5_competing"] = {}
    comp = {"white": "white_c", "south": "south_c", "state_R1996": "stateR1996_c", "state_mean_shock": "stateshock_c"}
    for k, c in comp.items():
        f = A.run_iv(p, "dR_2000_2016", mods=("erosion_c", c))
        R["R5_competing"][k] = {"gamma": A.summarize(f, "shock_x_erosion_c"), "competitor": A.summarize(f, f"shock_x_{c}"),
                                "first_stage": f.first_stage}
    f = A.run_iv(p, "dR_2000_2016", mods=("erosion_c",) + tuple(comp.values()))
    R["R5_competing"]["joint"] = {"gamma": A.summarize(f, "shock_x_erosion_c"),
                                  "competitors": {k: A.summarize(f, f"shock_x_{c}") for k, c in comp.items()}}

    # R6 County Business Patterns shock
    q = p.assign(cbp_shock_x_erosion_c=p["cbp_shock"] * p["erosion_c"])
    f, _, _ = A.run_ols(q, "dR_2000_2016", ["cbp_shock", "cbp_shock_x_erosion_c"])
    R["R6_cbp"] = {"ols": {"gamma": A.summarize(f, "cbp_shock_x_erosion_c"), "beta_at_mean": A.summarize(f, "cbp_shock")}}
    f = A.run_iv(p, "dR_2000_2016", shock="cbp_shock")
    R["R6_cbp"]["iv"] = {"gamma": A.summarize(f, "cbp_shock_x_erosion_c"), "beta_at_mean": A.summarize(f, "cbp_shock"),
                         "first_stage": f.first_stage}

    # R7 leave one state out
    loo = {}
    for s in sorted(p["state"].unique()):
        f = A.run_iv(p[p["state"] != s], "dR_2000_2016")
        loo[s] = float(f.coef[f.index("shock_x_erosion_c")])
    R["R7_leave_one_state_out"] = {"min": min(loo.values()), "max": max(loo.values()),
                                   "argmin": min(loo, key=loo.get), "argmax": max(loo, key=loo.get), "all": loo}

    # F1 placebo outcomes, F2 placebo moderator
    R["F1_placebo"] = {}
    for y in ["dR_1992_1996", "dR_1996_2000"]:
        f = A.run_iv(p, y, controls=A.CONTROLS_NO_ELECTION)
        blk = A.interaction_block(f, "erosion_c")
        blk["gamma_per_state_sd"] = blk["gamma"]["coef"] * modinfo["erosion"]["state_sd"]
        R["F1_placebo"][y] = blk
    f = A.run_iv(p, "dR_2000_2016", mods=("pre_reform_decline_z",))
    R["F2_placebo_moderator"] = A.interaction_block(f, "pre_reform_decline_z")

    # Binned (descriptive) and bridge
    R["binned_terciles"] = A.binned_effects(p, "dR_2000_2016")
    R["bridge"] = A.bridge(p, prim, modinfo, fec)

    # Per-standard-deviation summary of every interaction (Figure 2 and the robustness table)
    sd = modinfo["erosion"]["state_sd"]
    TW = A.TWOWAY

    def row(key, label, blk, scale, group, unit="trade shock"):
        return {"key": key, "label": label, "group": group, "shock_unit": unit,
                "coef": blk["coef"] * scale, "ci95": [c * scale for c in blk[TW]["ci95"]],
                "p": blk[TW]["p"], "coef_natural": blk["coef"], "ci95_natural": blk[TW]["ci95"]}

    rows = [row("primary", "Primary: 2SLS, 2000–2016", R["primary"]["gamma"], sd, "main"),
            row("w2012", "Secondary window, 2012–2016", R["windows"]["dR_2012_2016"]["gamma"], sd, "window"),
            row("w2008", "Window 2000–2008", R["windows"]["dR_2000_2008"]["gamma"], sd, "window"),
            row("w2012b", "Window 2000–2012", R["windows"]["dR_2000_2012"]["gamma"], sd, "window"),
            row("ols", "OLS", R["R1_ols"]["gamma"], sd, "robust"),
            row("unweighted", "Unweighted 2SLS", R["R2_unweighted"]["gamma"], sd, "robust")]
    labels = {"neg_tpr_2016": "Moderator: low 2015–16 ratio", "neg_real_benefit_2016": "Moderator: low real 2016 benefit",
              "real_benefit_decline_pct": "Moderator: real benefit decline", "neg_benefit_1996": "Moderator: low 1996 AFDC benefit",
              "erosion_2008": "Moderator: erosion to 2007–08"}
    for k, lab in labels.items():
        rows.append(row(f"alt_{k}", lab, R["R4_alt_moderators"][k]["gamma"], 1.0, "moderator"))
    for k, lab in [("white", "white share"), ("south", "South"), ("state_R1996", "1996 state vote"),
                   ("state_mean_shock", "state mean shock")]:
        rows.append(row(f"comp_{k}", f"With shock × {lab}", R["R5_competing"][k]["gamma"], sd, "competing"))
    rows.append(row("comp_joint", "With all four competitors", R["R5_competing"]["joint"]["gamma"], sd, "competing"))
    rows.append(row("cbp_ols", "CBP shock, OLS", R["R6_cbp"]["ols"]["gamma"], sd, "cbp", "CBP manufacturing loss"))
    rows.append(row("cbp_iv", "CBP shock, 2SLS", R["R6_cbp"]["iv"]["gamma"], sd, "cbp", "CBP manufacturing loss"))
    rows.append(row("placebo_9296", "Placebo outcome 1992–1996", R["F1_placebo"]["dR_1992_1996"]["gamma"], sd, "placebo"))
    rows.append(row("placebo_9600", "Placebo outcome 1996–2000", R["F1_placebo"]["dR_1996_2000"]["gamma"], sd, "placebo"))
    rows.append(row("placebo_mod", "Placebo moderator: 1979–1996 decline", R["F2_placebo_moderator"]["gamma"], 1.0, "placebo"))
    R["robustness_rows"] = {r["key"]: r for r in rows}
    R["robustness_order"] = [r["key"] for r in rows]

    # covariance for the figure's confidence band
    i, j = prim.index("shock"), prim.index("shock_x_erosion_c")
    V = prim.vcov[A.TWOWAY]
    R["primary"]["vcov_beta_gamma_twoway"] = [[float(V[i, i]), float(V[i, j])], [float(V[j, i]), float(V[j, j])]]

    (OUT / "results.json").write_text(json.dumps(R, indent=1, sort_keys=True) + "\n")
    from afdc import figures
    figures.make_all(R, FIG, states=full_states)
    print(json.dumps({"primary_gamma": R["primary"]["gamma"], "V1": R["V1_adhm_replication"]}, indent=1))


if __name__ == "__main__":
    main()
