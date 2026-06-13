# Scale-invariant transfer — percentile-ranked distance + centrality features

**Date:** 2026-06-13
**Notebooks:** `scale_invariant/notebooks/01_BCN_train_scale_invariant.ipynb` (train), `02_test_all_cities_scale_invariant.ipynb` (test all cities)
**Models:** `scale_invariant/models/*_si.pkl` — Barcelona, trained on the **10 percentile-ranked** distance + centrality features only.

## Why

The [ablation study](../ablation_study/ABLATION_STUDY_REPORT.md) showed Barcelona's noise signal lives almost
entirely in the 10 `distances` + `centrality` features — but the [transfer study](../deployment/BCN_MODEL_TRANSFER_REPORT.md)
showed those are exactly the features that go **out-of-distribution** across cities, because their raw values
depend on network size / urban fabric (closeness shrinks as a network grows; `dist_to_trunk` explodes in big
cities). This is **covariate shift**. This experiment implements the transfer report's recommended fix —
**solution (a): make those features scale-invariant by per-city percentile-rank normalization** — and measures
whether the signal-rich features then transfer.

## How the scale-invariant features are built

For each city independently, and each feature `f` in the 10 (`dist_to_{trunk,primary,secondary,tertiary,
residential,living_street}` + `betweenness, closeness_global, closeness_400, straightness`):

```python
df[f + '_pct'] = df[f].rank(pct=True)     # per-city percentile: fraction of the city's streets with value ≤ this one
```

`rank(pct=True)` replaces each street's raw value by its **percentile position within its own city** (the
empirical CDF, range (0,1], ties averaged). This is dimensionless and city-relative: *"this street is in the
90th percentile of closeness for its city"* means the same thing in Barcelona, Berlin or Zaragoza, regardless
of absolute scale or segment count. A model that learns "high closeness-percentile ⇒ louder" then applies
correctly everywhere. The 6 distances keep their meaning too (a street on a trunk ⇒ `dist_to_trunk`=0 ⇒ low
percentile in every city). The transform needs **no geospatial recomputation** — the raw columns already exist
in every city's dataset CSV, so this is pure pandas (no momepy reruns).

Because percentile rank is **monotonic**, it changes nothing *within* a single city — so it neither helps nor
hurts Barcelona's own held-out score. The entire effect is on **transfer**.

## Barcelona held-out — the transform preserves the signal

| Task / metric | raw `only-dist+centr` (ablation) | scale-invariant 10 |
|---|---|---|
| Classification accuracy — LogReg / XGB / RF | 0.582 / 0.742 / 0.751 | 0.599 / 0.742 / **0.748** |
| Regression R² — LinReg / XGB / RF | 0.362 / 0.679 / 0.696 | 0.416 / 0.679 / **0.694** |

The tree models are unchanged (monotonic transform); the **linear models slightly improve** (percentile ranks
are better-behaved than raw skewed distances for a linear fit). So the scale-invariant 10-feature model is just
as strong as the raw model on Barcelona — and essentially as strong as the full 18-feature model (RF 0.749 /
0.704). Any change on the other cities is therefore pure transfer effect.

## Transfer results — raw-18 vs scale-invariant-10 (Random Forest)

The raw-18 column is the original deployed model (reproduces the published transfer numbers exactly).

### Classification — accuracy

| City | raw-18 | SI-10 | Δ |
|---|---|---|---|
| Viladecans | 0.469 | 0.469 | 0.00 |
| Milan | 0.690 | **0.734** | +0.04 |
| Berlin | 0.301 | 0.222 | **−0.08** |
| Lyon | 0.533 | 0.490 | −0.04 |
| Zaragoza | 0.307 | **0.415** | **+0.11** |

### Regression — R² and MAE (dB)

| City | R² raw-18 | R² SI-10 | Δ R² | MAE raw-18 | MAE SI-10 | Δ MAE |
|---|---|---|---|---|---|---|
| Viladecans | −0.52 | **+0.29** | **+0.81** | 6.08 | **4.40** | **−1.68** |
| Milan | −3.83 | −3.13 | +0.71 | 5.41 | 4.56 | −0.85 |
| Berlin | +0.11 | −0.47 | **−0.58** | 6.89 | 8.85 | **+1.96** |
| Lyon | −0.56 | −0.72 | −0.16 | 6.50 | 6.64 | +0.14 |
| Zaragoza | −0.56 | **+0.02** | **+0.57** | 8.53 | **6.47** | **−2.05** |

(Linear and XGBoost models show the same pattern — full numbers in `results/si_transfer_comparison_{class,regre}.csv`.)

![Scale-invariant vs raw transfer](results/fig_si_vs_raw_transfer.png)

## Interpretation — scale-invariance fixes *covariate* shift, not *label* shift

The results split the cities cleanly by **what was actually wrong** with their transfer:

**Where the problem was covariate shift → scale-invariance is a big win.**
- **Viladecans** (tiny, 1.6k segments — raw closeness was 22σ out): regression R² goes **−0.52 → +0.29** (from
  worse-than-useless to genuinely predictive), MAE drops 1.7 dB, and the −3.6 dB underestimation bias shrinks to
  −0.8 dB. The model's signal now lands because Viladecans' "most central streets" are finally on the same scale
  as Barcelona's.
- **Zaragoza** (raw `dist_to_tertiary` was 4.7σ out): regression R² **−0.56 → +0.02**, MAE drops **2.05 dB**,
  classification accuracy **+0.11**, bias −7.3 → −4.4 dB. The single biggest improvement of any city.

**Where the problem was label shift or label definition → it does not help, and can hurt.**
- **Berlin** *regresses* (accuracy −0.08, R² +0.11 → −0.47, MAE +2 dB). Berlin's transfer failure was never
  mainly covariate — it is **label shift**: Berlin genuinely has a quiet acoustic environment (45% of streets at
  40–50 dB vs Barcelona's 54% at 60–70). Percentile-ranking the features makes Berlin's inputs look *more*
  Barcelona-like, so the model predicts *louder*, amplifying the pre-existing +3.5 dB overestimation to +7.3 dB.
  Correcting the feature scale cannot fix a genuinely different noise distribution.
- **Milan**: classification improves (0.69 → 0.73) as covariate alignment helps, but regression R² stays deeply
  negative — Milan's target is acoustic-zoning **legal limits**, not modeled dB. That is a target-definition
  mismatch, untouchable by feature normalization.
- **Lyon**: essentially flat. Lyon (commune, ~7k segments) is Barcelona-sized, so it had little covariate shift to
  correct in the first place; its residual gap is the **Lden-as-daytime** label definition, which SI does not touch.

## Conclusion

- **Solution (a) works for what it targets.** Per-city percentile-rank normalization makes the signal-rich
  distance + centrality features transfer, and it converts the two most scale-distorted cities (Viladecans,
  Zaragoza) from unusable (negative R²) to usable (positive R², MAE down ~2 dB), with no cost on Barcelona.
- **It is not a universal fix, and that is diagnostic.** Where it fails (Berlin) or is flat (Lyon, Milan
  regression), the remaining error is **label shift / label definition**, not covariate shift — a different
  problem that needs a different remedy (target harmonization, or a few hundred labeled target-city segments to
  recalibrate, as the transfer report notes). The clean split here actually *confirms* the covariate-shift
  diagnosis: scale-invariance helps exactly the cities the σ-analysis flagged as scale-distorted, and only those.
- **Recommended deployable model:** the scale-invariant 10-feature model for cities where the noise map is true
  modeled dB and the city differs from Barcelona mainly in size/fabric (Viladecans, Zaragoza, and any new small
  or medium city). For Berlin-like cases, scale-invariance must be paired with target-side calibration.

*Numbers from `results/si_transfer_comparison_{class,regre}.csv`; per-city scale-invariant predictions and RF
dB-error maps in `results/<xxx>_si_predictions_*.csv` and `results/<xxx>_si_map_db_diff_rf.html`.*
