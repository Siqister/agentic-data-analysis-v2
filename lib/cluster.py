"""Clusters from several Indicators' tables (architecture.md § 4.4, Clusters).

k-means on z-scores of the inputs, with extreme values kept (no clipping; chunk 6a). Clusters are
numbered by their members' median of the first input; they're never named."""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, silhouette_score

N_INIT = 50          # k-means restarts (fixed here, not in specs)
DIAGNOSTIC_K = range(2, 9)
RESAMPLES = 50       # bootstrap resamples for stability


def assign(tables: dict[str, pd.DataFrame], cfg: dict) -> pd.DataFrame:
    """One row per unit: estimate = cluster number (blank if any input is blank), moe blank,
    one column per input (its estimate as published), and a note naming each blank input.

    `tables` maps each builds_on ID to its table at this geography, in builds_on order."""
    t = inputs(tables)
    ids = list(tables)
    ok = t[ids].notna().all(axis=1)
    if cfg["k"] > ok.sum():
        raise ValueError(f"k = {cfg['k']} is more than the {ok.sum()} units with every input")
    labels = fit(features(t.loc[ok], ids, cfg), cfg["k"], cfg["seed"])
    t["estimate"] = pd.array([pd.NA] * len(t), dtype="Int64")
    t.loc[ok, "estimate"] = number(t.loc[ok, ids], labels)
    t["moe"] = np.nan
    return t


def inputs(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """geography_id, geography_name, one column per input, and `note` listing each blank input."""
    ids = list(tables)
    first = tables[ids[0]]
    t = first[["geography_id", "geography_name"]].copy()
    notes = pd.Series([[] for _ in range(len(t))], index=t.index)
    for i, tab in tables.items():
        if set(tab["geography_id"]) != set(t["geography_id"]):
            raise ValueError(f"{i}'s table doesn't have the same units as {ids[0]}'s")
        m = t[["geography_id"]].merge(tab[["geography_id", "estimate", "note"]], on="geography_id", how="left")
        t[i] = m["estimate"].to_numpy()
        for k in np.flatnonzero(m["estimate"].isna().to_numpy()):
            note = m["note"].iloc[k]
            notes.iloc[k].append(f"{i}: {note if isinstance(note, str) and note else 'no value'}")
    t["note"] = notes.map("; ".join)
    return t


def features(t: pd.DataFrame, ids: list[str], cfg: dict) -> np.ndarray:
    """The inputs, logged where `cfg['log']` says, as z-scores over these units (population SD)."""
    cols = []
    for i in ids:
        v = t[i].to_numpy(dtype=float)
        if i in (cfg.get("log") or []):
            if (v <= 0).any():
                raise ValueError(f"{i} has values that aren't positive, so it can't be logged")
            v = np.log(v)
        sd = v.std(ddof=0)
        if sd == 0:
            raise ValueError(f"{i} has the same value for every unit, so it can't be scaled")
        cols.append((v - v.mean()) / sd)
    return np.column_stack(cols)


def fit(x: np.ndarray, k: int, seed: int) -> np.ndarray:
    """k-means labels (0 … k−1), with the run-time checks: no empty cluster, and every unit
    nearest its own cluster's center."""
    km = KMeans(n_clusters=k, random_state=seed, n_init=N_INIT, algorithm="lloyd").fit(x)
    labels = km.labels_
    if len(np.unique(labels)) != k:
        raise ValueError(f"k-means left a cluster empty (k = {k})")
    d = ((x[:, None, :] - km.cluster_centers_[None, :, :]) ** 2).sum(axis=2)
    if (d[np.arange(len(x)), labels] > d.min(axis=1) + 1e-9).any():
        raise ValueError("a unit isn't nearest its own cluster's center")
    return labels


def number(values: pd.DataFrame, labels: np.ndarray) -> np.ndarray:
    """Cluster numbers 1 … k, in ascending order of the members' median of the first input
    (as published); ties go by the next input."""
    med = values.groupby(labels).median()
    order = med.sort_values(list(values.columns)).index
    rank = {label: n + 1 for n, label in enumerate(order)}
    return np.array([rank[label] for label in labels])


def summary(t: pd.DataFrame, ids: list[str], cfg: dict) -> dict:
    """The manifest's `clusters` block (architecture.md § 8)."""
    ok = t["estimate"].notna()
    med = t.loc[ok].groupby("estimate")[ids].median()
    size = t.loc[ok, "estimate"].value_counts()
    return {
        "method": cfg["method"], "k": cfg["k"], "seed": cfg["seed"], "log": list(cfg.get("log") or []),
        "units_clustered": int(ok.sum()), "units_not_clustered": int((~ok).sum()),
        "clusters": [{"cluster": int(n), "size": int(size[n]), "medians": {i: float(med.loc[n, i]) for i in ids}}
                     for n in sorted(med.index)],
    }


def diagnostics(t: pd.DataFrame, ids: list[str], cfg: dict) -> pd.DataFrame:
    """One row per k from 2 to 8 with the spec's other settings: inertia, mean silhouette,
    stability (mean adjusted Rand index over seeded bootstrap resamples) and sizes by cluster number."""
    vals = t.loc[t[ids].notna().all(axis=1), ids]
    x = features(vals, ids, cfg)
    rows = []
    for k in DIAGNOSTIC_K:
        if k > len(x):
            break
        km = KMeans(n_clusters=k, random_state=cfg["seed"], n_init=N_INIT, algorithm="lloyd").fit(x)
        rng = np.random.default_rng(cfg["seed"])
        ari = []
        for _ in range(RESAMPLES):
            idx = rng.integers(0, len(x), len(x))
            boot = KMeans(n_clusters=k, random_state=cfg["seed"], n_init=N_INIT, algorithm="lloyd").fit(x[idx])
            ari.append(adjusted_rand_score(km.labels_, boot.predict(x)))
        sizes = np.bincount(number(vals, km.labels_))[1:]
        rows.append({"k": k, "spec_k": k == cfg["k"], "inertia": km.inertia_,
                     "silhouette": silhouette_score(x, km.labels_), "stability": float(np.mean(ari)),
                     "sizes": " ".join(map(str, sizes))})
    return pd.DataFrame(rows)
