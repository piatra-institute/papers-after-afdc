"""Weighted OLS and 2SLS with one-way and two-way cluster-robust inference.

Conventions
-----------
* Analytic weights enter by scaling every row by sqrt(w), as in Stata's aweights.
* One-way cluster-robust variance: c * B M B with c = G/(G-1) * (N-1)/(N-K),
  the finite-sample factor used by Stata's regress/ivregress.
* Two-way variance (Cameron, Gelbach and Miller 2011): V_a + V_b - V_ab, each
  term with its own G; if the sum is not positive semi-definite the negative
  eigenvalues are set to zero, as CGM suggest.
* 2SLS bread uses the projected regressors Xhat, residuals use the structural X.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from scipy import stats


@dataclass
class Fit:
    names: list[str]
    coef: np.ndarray
    vcov: dict[str, np.ndarray]
    nobs: int
    nclusters: dict[str, int]
    first_stage: dict = field(default_factory=dict)

    def index(self, name: str) -> int:
        return self.names.index(name)

    def se(self, name: str, kind: str) -> float:
        k = self.index(name)
        return float(np.sqrt(self.vcov[kind][k, k]))

    def ci(self, name: str, kind: str, level: float = 0.95, df: int | None = None) -> tuple[float, float]:
        b = float(self.coef[self.index(name)])
        s = self.se(name, kind)
        q = stats.t.ppf(0.5 + level / 2, df) if df else stats.norm.ppf(0.5 + level / 2)
        return b - q * s, b + q * s

    def pvalue(self, name: str, kind: str, df: int | None = None) -> float:
        t = float(self.coef[self.index(name)]) / self.se(name, kind)
        return float(2 * (stats.t.sf(abs(t), df) if df else stats.norm.sf(abs(t))))


def _cluster_meat(scores: np.ndarray, groups: np.ndarray) -> tuple[np.ndarray, int]:
    """Sum over clusters of (sum of scores in cluster)(...)'."""
    codes, inv = np.unique(groups, return_inverse=True)
    G = len(codes)
    S = np.zeros((G, scores.shape[1]))
    np.add.at(S, inv, scores)
    return S.T @ S, G


def _psd(v: np.ndarray) -> np.ndarray:
    vals, vecs = np.linalg.eigh((v + v.T) / 2)
    if vals.min() >= 0:
        return v
    vals = np.clip(vals, 0, None)
    return (vecs * vals) @ vecs.T


def cluster_vcov(Xb: np.ndarray, u: np.ndarray, bread: np.ndarray, clusters: dict[str, np.ndarray]) -> tuple[dict, dict]:
    """Return one-way vcovs for each clustering and two-way for the first pair.

    Xb is the (weighted) matrix whose rows times residuals form the scores:
    X for OLS, Xhat for 2SLS.
    """
    N, K = Xb.shape
    scores = Xb * u[:, None]
    out, ng = {}, {}
    for name, g in clusters.items():
        meat, G = _cluster_meat(scores, g)
        c = G / (G - 1) * (N - 1) / (N - K)
        out[name] = c * bread @ meat @ bread
        ng[name] = G
    names = list(clusters)
    if len(names) >= 2:
        a, b = names[0], names[1]
        inter = np.char.add(np.char.add(clusters[a].astype(str), "|"), clusters[b].astype(str))
        meat_ab, G_ab = _cluster_meat(scores, inter)
        c_ab = G_ab / (G_ab - 1) * (N - 1) / (N - K)
        v2 = out[a] + out[b] - c_ab * bread @ meat_ab @ bread
        out[f"{a}+{b}"] = _psd(v2)
        ng[f"{a}+{b}"] = min(ng[a], ng[b])
    # heteroskedasticity-robust (HC1) for reference
    meat_hc = scores.T @ scores
    out["hc1"] = N / (N - K) * bread @ meat_hc @ bread
    return out, ng


def ols(y, X, names, w=None, clusters=None) -> Fit:
    y = np.asarray(y, float)
    X = np.asarray(X, float)
    sw = np.sqrt(np.asarray(w, float)) if w is not None else np.ones(len(y))
    Xw, yw = X * sw[:, None], y * sw
    XtX_inv = np.linalg.inv(Xw.T @ Xw)
    b = XtX_inv @ Xw.T @ yw
    u = yw - Xw @ b
    v, ng = cluster_vcov(Xw, u, XtX_inv, clusters or {})
    return Fit(list(names), b, v, len(y), ng)


def iv2sls(y, X_endog, X_exog, Z_excl, endog_names, exog_names, w=None, clusters=None,
           first_stage_cluster: str | None = None) -> Fit:
    """2SLS of y on [X_endog, X_exog] with instruments [Z_excl, X_exog]."""
    y = np.asarray(y, float)
    Xn = np.asarray(X_endog, float)
    Xx = np.asarray(X_exog, float)
    Ze = np.asarray(Z_excl, float)
    sw = np.sqrt(np.asarray(w, float)) if w is not None else np.ones(len(y))
    X = np.hstack([Xn, Xx]) * sw[:, None]
    Z = np.hstack([Ze, Xx]) * sw[:, None]
    yw = y * sw
    ZtZ_inv = np.linalg.inv(Z.T @ Z)
    Xhat = Z @ (ZtZ_inv @ (Z.T @ X))
    bread = np.linalg.inv(Xhat.T @ X)
    b = bread @ (Xhat.T @ yw)
    u = yw - X @ b
    bread_sym = np.linalg.inv(Xhat.T @ Xhat)
    v, ng = cluster_vcov(Xhat, u, bread_sym, clusters or {})
    fit = Fit(list(endog_names) + list(exog_names), b, v, len(y), ng)
    fit.first_stage = first_stage_stats(Xn, Xx, Ze, sw, clusters, first_stage_cluster, endog_names)
    return fit


def _wald_F(coef, vcov, idx):
    b = coef[idx]
    V = vcov[np.ix_(idx, idx)]
    return float(b @ np.linalg.solve(V, b) / len(idx))


def first_stage_stats(Xn, Xx, Ze, sw, clusters, cluster_name, endog_names) -> dict:
    """Cluster-robust first-stage F for each endogenous regressor, plus the
    Sanderson-Windmeijer conditional F when there is more than one."""
    out = {}
    if not clusters or cluster_name is None:
        return out
    g = {cluster_name: clusters[cluster_name]}
    L = Ze.shape[1]
    Zfull = np.hstack([Ze, Xx])
    names_z = [f"z{j}" for j in range(L)] + [f"x{j}" for j in range(Xx.shape[1])]
    idx = list(range(L))
    k = Xn.shape[1]
    for j in range(k):
        fs = ols(Xn[:, j], Zfull, names_z, w=sw ** 2, clusters=g)
        F = _wald_F(fs.coef, fs.vcov[cluster_name], idx)
        entry = {"F_cluster": F}
        if k > 1:
            others = [i for i in range(k) if i != j]
            # 2SLS of x_j on the other endogenous regressors, instrumented by Z
            fit = iv2sls_noinfo(Xn[:, j], Xn[:, others], Xx, Ze, sw)
            resid = Xn[:, j] - np.hstack([Xn[:, others], Xx]) @ fit
            fs2 = ols(resid, Zfull, names_z, w=sw ** 2, clusters=g)
            Fsw = _wald_F(fs2.coef, fs2.vcov[cluster_name], idx) * L / (L - k + 1)
            entry["F_sanderson_windmeijer_cluster"] = Fsw
        out[endog_names[j]] = entry
    return out


def iv2sls_noinfo(y, Xn, Xx, Ze, sw):
    X = np.hstack([Xn, Xx]) * sw[:, None]
    Z = np.hstack([Ze, Xx]) * sw[:, None]
    yw = y * sw
    Xhat = Z @ np.linalg.lstsq(Z, X, rcond=None)[0]
    return np.linalg.solve(Xhat.T @ X, Xhat.T @ yw)


def wild_cluster_bootstrap(y, X, names, test: str, clusters, w=None, reps: int = 9999, seed: int = 0) -> dict:
    """Restricted (null-imposed) wild cluster bootstrap-t for one OLS coefficient,
    Rademacher weights drawn by cluster (Cameron, Gelbach and Miller 2008)."""
    y = np.asarray(y, float)
    X = np.asarray(X, float)
    sw = np.sqrt(np.asarray(w, float)) if w is not None else np.ones(len(y))
    Xw, yw = X * sw[:, None], y * sw
    k = names.index(test)
    N, K = Xw.shape
    codes, inv = np.unique(clusters, return_inverse=True)
    G = len(codes)
    c = G / (G - 1) * (N - 1) / (N - K)
    A = np.linalg.solve(Xw.T @ Xw, Xw.T)  # K x N, beta = A y
    a_k = A[k]

    def t_stat(yv):
        b = A @ yv
        u = yv - Xw @ b
        s = np.zeros(G)
        np.add.at(s, inv, a_k * u)
        return b[k] / np.sqrt(c * (s @ s))

    t_obs = t_stat(yw)
    keep = [i for i in range(K) if i != k]
    Xr = Xw[:, keep]
    br = np.linalg.lstsq(Xr, yw, rcond=None)[0]
    fitted_r = Xr @ br
    u_r = yw - fitted_r
    rng = np.random.default_rng(seed)
    t_boot = np.empty(reps)
    for r in range(reps):
        v = rng.choice([-1.0, 1.0], size=G)[inv]
        t_boot[r] = t_stat(fitted_r + v * u_r)
    p = float((np.sum(np.abs(t_boot) >= abs(t_obs)) + 1) / (reps + 1))
    return {"t": float(t_obs), "p_value": p, "reps": reps, "clusters": int(G), "seed": seed,
            "weights": "Rademacher", "null_imposed": True}
