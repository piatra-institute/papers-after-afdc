"""Estimator checks on synthetic data with known parameters."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from afdc.estimators import iv2sls, ols, wild_cluster_bootstrap  # noqa: E402


def synthetic(n=4000, G=40, seed=1):
    rng = np.random.default_rng(seed)
    g = rng.integers(0, G, n)
    h = rng.integers(0, 150, n)
    m = rng.normal(size=G)[g]                      # cluster-level moderator
    z = rng.normal(size=n) + 0.3 * rng.normal(size=150)[h]
    u = rng.normal(size=n) + 0.5 * rng.normal(size=G)[g]
    x = 0.8 * z + 0.5 * u + rng.normal(size=n)     # endogenous
    c = rng.normal(size=n)
    y = 1.0 + 2.0 * x + 0.5 * x * m + 0.3 * c + u
    w = rng.uniform(0.5, 2.0, n)
    return dict(g=g, h=h, m=m, z=z, x=x, c=c, y=y, w=w)


def test_ols_recovers_exogenous_model():
    rng = np.random.default_rng(0)
    n = 5000
    X = np.column_stack([np.ones(n), rng.normal(size=n), rng.normal(size=n)])
    y = X @ np.array([1.0, -2.0, 0.5]) + rng.normal(size=n)
    fit = ols(y, X, ["c", "a", "b"], clusters={"g": rng.integers(0, 50, n)})
    assert np.allclose(fit.coef, [1.0, -2.0, 0.5], atol=0.06)


def test_2sls_recovers_interaction_and_ols_is_biased():
    d = synthetic()
    Xn = np.column_stack([d["x"], d["x"] * d["m"]])
    Ze = np.column_stack([d["z"], d["z"] * d["m"]])
    Xx = np.column_stack([np.ones_like(d["y"]), d["c"]])
    fit = iv2sls(d["y"], Xn, Xx, Ze, ["x", "xm"], ["const", "c"], w=d["w"],
                 clusters={"g": d["g"], "h": d["h"]}, first_stage_cluster="g")
    assert abs(fit.coef[0] - 2.0) < 0.1
    assert abs(fit.coef[1] - 0.5) < 0.1
    o = ols(d["y"], np.column_stack([Xn, Xx]), ["x", "xm", "const", "c"], w=d["w"])
    assert o.coef[0] - 2.0 > 0.15  # OLS is biased upward by construction
    assert fit.first_stage["x"]["F_cluster"] > 50


def test_matches_linearmodels_point_estimates_and_cluster_se():
    from linearmodels.iv import IV2SLS

    d = synthetic(seed=3)
    df = pd.DataFrame(d)
    df["xm"], df["zm"] = df.x * df.m, df.z * df.m
    exog = df[["c"]].assign(const=1.0)
    lm = IV2SLS(df.y, exog, df[["x", "xm"]], df[["z", "zm"]], weights=df.w).fit(
        cov_type="clustered", clusters=df.g, debiased=False)
    fit = iv2sls(df.y.to_numpy(), df[["x", "xm"]].to_numpy(), exog.to_numpy(), df[["z", "zm"]].to_numpy(),
                 ["x", "xm"], ["c", "const"], w=df.w.to_numpy(), clusters={"g": df.g.to_numpy()})
    assert np.allclose(fit.coef[:2], lm.params[["x", "xm"]].to_numpy(), rtol=1e-8)
    # linearmodels without debiasing applies no finite-sample factor; ours applies G/(G-1)(N-1)/(N-K)
    N, K, G = len(df), 4, df.g.nunique()
    factor = np.sqrt(G / (G - 1) * (N - 1) / (N - K))
    assert np.allclose(np.array([fit.se("x", "g"), fit.se("xm", "g")]) / factor,
                       lm.std_errors[["x", "xm"]].to_numpy(), rtol=1e-6)


def test_twoway_vcov_is_psd_and_exceeds_hc1():
    d = synthetic(seed=5)
    X = np.column_stack([np.ones_like(d["y"]), d["x"], d["c"]])
    fit = ols(d["y"], X, ["const", "x", "c"], clusters={"g": d["g"], "h": d["h"]})
    V = fit.vcov["g+h"]
    assert np.linalg.eigvalsh(V).min() >= -1e-12
    assert fit.se("x", "g+h") >= 0.9 * fit.se("x", "hc1")


def test_wild_bootstrap_rejects_true_effect_and_is_reproducible():
    rng = np.random.default_rng(7)
    n, G = 3000, 40
    g = rng.integers(0, G, n)
    m = rng.normal(size=G)[g]
    x = rng.normal(size=n)
    e = rng.normal(size=n) + rng.normal(size=G)[g]
    X = np.column_stack([np.ones(n), x, x * m])
    y_null = 1 + x + e
    y_alt = 1 + x + 0.4 * x * m + e
    r1 = wild_cluster_bootstrap(y_alt, X, ["c", "x", "xm"], "xm", g, reps=499, seed=11)
    r2 = wild_cluster_bootstrap(y_alt, X, ["c", "x", "xm"], "xm", g, reps=499, seed=11)
    r0 = wild_cluster_bootstrap(y_null, X, ["c", "x", "xm"], "xm", g, reps=499, seed=11)
    assert r1 == r2
    assert r1["p_value"] < 0.01
    assert r0["p_value"] > 0.01
