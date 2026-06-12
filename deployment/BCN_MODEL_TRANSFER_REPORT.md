# Testing the Barcelona-trained noise models on other cities

**Date:** 2026-06-12 (regression transfer added 2026-06-13)
**Classification models:** Logistic Regression, XGBoost, Random Forest — trained on `notebooks/_elena/data/bcn_noise_class_ml_dataset.csv`, target **`noise_day` class**, saved as pickles in `notebooks/_elena/models/` (see `07_SL_save_model_classification.ipynb`).
**Regression models:** Linear Regression, XGBoost, Random Forest — trained on `notebooks/_elena/data/bcn_noise_regre_ml_dataset.csv`, target **`noise_day` in dB**, saved with the `_regre` suffix (see `07_SL_save_model_regression.ipynb`).
**Test notebooks:** `deployment/<City>/notebooks/<XXX>_test_bcn_model_class.ipynb` and `<XXX>_test_bcn_model_regre.ipynb` → results in `deployment/<City>/results/` (predictions CSV + interactive error map HTML).

Noise classes: `0: <40 dB, 1: 40–50, 2: 50–60, 3: 60–70, 4: ≥70`.

---

## Results — classification (predicting the `noise_day` class)

### Exact-class accuracy

| Model | Barcelona (held-out 20%) | Viladecans | Milan | Berlin | Lyon |
|---|---|---|---|---|---|
| Logistic Regression | 0.606 | **0.558** | 0.650 | 0.265 | **0.534** |
| XGBoost | 0.741 | 0.524 | 0.611 | 0.282 | 0.512 |
| Random Forest | **0.749** | 0.469 | **0.690** | **0.301** | 0.533 |

### Macro F1 / within ±1 class / mean signed error (predicted − real)

| City | Best macro F1 | Within ±1 class (RF) | Signed error range |
|---|---|---|---|
| Viladecans | 0.385 (LogReg) | 0.93 | −0.04 … +0.19 |
| Milan | 0.204 (RF) | 0.99 | −0.31 … +0.16 |
| Berlin | 0.229 (RF) | 0.88 | **+0.68 … +0.87** |
| Lyon | 0.350 (XGBoost) | 0.99 | −0.26 … −0.06 |

### Real `noise_day` class distribution per city

| Class | Barcelona | Viladecans | Milan | Berlin | Lyon |
|---|---|---|---|---|---|
| 0 (<40 dB) | 1% | 0% | 0% | 3% | 0% |
| 1 (40–50) | 5% | 10% | 0% | **45%** | 1% |
| 2 (50–60) | 29% | 42% | 5% | 32% | 24% |
| 3 (60–70) | **54%** | 37% | **94%** | 17% | 48% |
| 4 (≥70) | 12% | 11% | 1% | 3% | **27%** |

---

## Results — regression (predicting `noise_day` in dB)

The three regressors from `04_SL_regression.ipynb` (pickled by `07_SL_save_model_regression.ipynb`) were applied to each city's `<xxx>_noise_regre_ml_dataset.csv` — the same 22-column schema, but with real dB values instead of the 0–4 classes. The dB values come from the **same noise-map join/sampling as the class pipeline** (stored in `<XXX>_noise_streets.gpkg`, extracted by `<XXX>_OSM_roads_noise_regre.ipynb`), so segments and features are identical to the classification datasets.

**Barcelona held-out 20% baseline:** Linear Regression R² 0.461 / MAE 4.10 dB · XGBoost R² 0.681 / MAE 3.06 dB · Random Forest R² 0.704 / MAE 2.90 dB.

### MAE in dB (mean signed error, predicted − real)

| Model | Viladecans | Milan | Berlin | Lyon |
|---|---|---|---|---|
| Linear Regression | **4.67** (+1.1) | **4.82** (+1.7) | 8.42 (+6.4) | **5.03** (−3.9) |
| XGBoost | 8.74 (−7.0) | 4.94 (−4.0) | **6.47** (+2.9) | 7.14 (−6.3) |
| Random Forest | 6.08 (−3.6) | 5.41 (−5.0) | 6.90 (+3.5) | 6.50 (−5.8) |

R² is negative almost everywhere out-of-domain (Milan −3.1…−3.8 because the zoning-limit target has almost no variance to explain; Viladecans/Lyon −1.8…0.06; Berlin −0.37…+0.17), so MAE and bias are the meaningful numbers here.

### Derived-class accuracy (predicted dB binned back into the 0–4 classes)

| Model | Viladecans | Milan | Berlin | Lyon |
|---|---|---|---|---|
| Linear Regression | **0.578** | **0.604** | 0.315 | **0.446** |
| XGBoost | 0.357 | 0.465 | **0.389** | 0.371 |
| Random Forest | 0.485 | 0.350 | 0.337 | 0.397 |

Within ±1 class (Linear Regression): Viladecans 0.96, Milan 0.99, Berlin 0.85, Lyon 0.98.

### Reading

- **Linear Regression is the transfer winner, even more clearly than in classification.** Lowest MAE in 3 of 4 cities with a small bias (+1–2 dB) in Viladecans/Milan; its derived-class accuracy in Viladecans (0.578) beats the best classification model there (LogReg, 0.558).
- **The tree regressors collapse out of domain.** XGBoost/RF, far ahead on Barcelona (R² 0.68–0.70 vs 0.46), underestimate the other cities by 4–7 dB: trees cannot extrapolate outside the feature ranges they were grown on, so out-of-distribution inputs (centralities, `dist_to_*`) fall into the nearest Barcelona-like leaves.
- **Berlin is the exception that proves the covariate-shift story.** It's the only city where the trees beat the linear model: Berlin's ~15 σ `dist_to_trunk` values get multiplied by Barcelona-fitted linear coefficients (+6.4 dB bias), while the trees saturate. Even so, the regression XGBoost's derived-class accuracy (0.389) beats every classification model on Berlin (best: RF 0.301) — predicting continuous dB and binning afterwards is the better way to transfer to Berlin.
- **The signed errors mirror the classification biases:** Berlin overestimated (+3…+6 dB), Lyon underestimated (−4…−6 dB — the Lden-as-day effect), Viladecans and Milan nearly unbiased with the linear model.

---

## What worked

- **The pipeline transfers mechanically without friction.** Because Milan, Viladecans and Berlin were rebuilt to the exact Barcelona schema (same 22 columns, same feature computation methods), the pickled scaler + `feature_columns.pkl` + models apply to any city dataset in three lines (`reindex columns → scaler.transform → model.predict`).
- **The models capture the noise *gradient* everywhere.** 88–99% of predictions land within ±1 class of the truth in every city. Big loud arterials are consistently predicted louder than small residential streets — the learned relationship between road category/centrality/POIs and noise is qualitatively right.
- **Milan, Viladecans and Lyon are usable results.** ~0.5–0.7 exact accuracy with small systematic bias (signed error within ±0.3 classes). Lyon is the cleanest external test so far: real modeled dB (10 m raster), all-classes-occupied target, 0.53 accuracy / 0.99 within ±1, and the best external macro F1 (0.35, XGBoost).
- **Generalization gap is visible and interpretable.** On Viladecans the simple Logistic Regression (0.558) beats Random Forest (0.469): RF memorizes Barcelona-specific patterns (it had 0.998 train accuracy) that don't hold elsewhere, while the smoother linear boundary transfers better. This is a textbook overfitting-to-source signal.

## What didn't work

- **Exact-class accuracy drops everywhere** (0.75 → 0.47–0.69 in Milan/Viladecans, → 0.30 in Berlin).
- **Berlin fails.** All three models systematically overestimate by ~0.7–0.9 classes; Logistic Regression never predicts class 0 or 1 at all, while 48% of Berlin's real streets are in those classes.
- **Milan's headline accuracy is misleading.** Milan's "real" values are 94% class 3, so the trivial baseline "always predict 3" scores 0.94 — better than any model (RF: 0.69, predicting class 2 for ~30% of streets). Macro F1 (~0.20) shows the models don't resolve Milan's (tiny) class variance either.
- **Minority classes are missed.** Class 0 and 4 recall is poor in every target city (see classification reports in the notebooks).

## Causes

**1. Covariate shift: network-scale-dependent features go out of distribution.**
The scaler was fit on Barcelona. Mean |z-score| of each city's features under that scaler (≈1.0 means "looks like Barcelona"):

| Feature | BCN | VIL | MIL | BER | LYO |
|---|---|---|---|---|---|
| dist_to_trunk | 0.9 | 3.7 | 1.3 | **14.7** | 1.4 |
| dist_to_primary | 0.7 | 4.3 | 0.7 | 1.4 | 0.7 |
| closeness_global | 0.8 | **10.1** | 1.1 | 3.5 | 1.7 |
| closeness_400 | 0.8 | **22.2** | 0.9 | 1.9 | 2.3 |
| betweenness | 0.6 | 1.8 | 0.7 | 0.6 | 0.9 |
| width | 0.9 | 0.9 | 0.8 | 0.6 | 0.8 |
| green / signals | 0.6–0.8 | 0.6–0.7 | 0.6–0.8 | 0.5–0.6 | 0.4–0.8 |

Global closeness/betweenness and `dist_to_*` are **functions of city size**: in tiny Viladecans (1.6k segments) closeness values are ~10–22 σ above Barcelona's; in huge Berlin (71k segments) closeness shrinks and distances to trunk roads explode (up to ~20 km, 15 σ). Milan (~22k segments, similar metropolitan structure) is the only city that stays in-distribution — and it's where accuracy is highest. Local, per-street features (width, green, signals, POIs) transfer fine everywhere.

**2. Label shift: the cities' noise maps describe different acoustic worlds.**
Barcelona's map says 54% of streets are 60–70 dB; Berlin's says 45% are 40–50 dB. A model trained on Barcelona has a strong prior toward classes 2–3 and reproduces it abroad (Berlin RF predicts 96% class 2–3), which alone explains Berlin's +0.7-class bias. Part of this is real urbanism (Barcelona's dense compact blocks vs Berlin's wide streets and greenery), part is **methodology of the source maps** — each city's strategic noise map uses its own calculation model, coverage and rounding.

**3. Label quality and definition: not all "noise_day" values mean the same thing.**
Milan's noise values come from acoustic zoning *legal limits* (94% one class), not modeled dB like Barcelona/Viladecans/Berlin/Lyon. Testing against them mostly measures "did the model predict the legal limit", not real noise. Lyon has a subtler version of the problem: it publishes only **Lden** (24h composite that up-weights evening +5 dB and night +10 dB), which was used as `db_day`. Lden runs a few dB above a plain daytime level, which inflates Lyon's class-4 share (27% real vs 3.6% predicted by RF) and explains the mild *under*-estimation bias (−0.2 classes) — the mirror image of Berlin's overestimation. Viladecans and Lyon are the cleanest external tests; Berlin (real modeled dB, 5 occupied classes, strong label shift) is the hardest.

**4. Residual overfitting of the tree models.** RF/XGBoost reach ~0.97–1.00 train accuracy on Barcelona; their advantage over Logistic Regression disappears (Milan, Berlin) or inverts (Viladecans) out-of-domain.

## Recommendations

1. **Use scale-invariant features**: rank-normalize or percentile-scale centralities and `dist_to_*` per city (or fit the scaler on the target city's features) so "the most central street in town" means the same thing in every city.
2. **Prefer Viladecans and Berlin for evaluation**; treat Milan's numbers with caution until a modeled-dB noise map replaces the zoning limits.
3. **Report within-±1-class and macro F1** alongside accuracy — exact-class accuracy on 10-dB bins is harsh and dominated by boundary effects.
4. If per-city calibration is acceptable, a small **fine-tuning step** (refit on a few hundred labeled segments of the target city) would likely fix Berlin's bias.

## Notes / caveats

- Berlin's feature CSV carries one extra column (`dist_to_main`) not in the Barcelona schema; both `01_BER_create_dataset_class.ipynb` and `01_BER_create_dataset_regre.ipynb` drop it, so the exported datasets match Barcelona's 22 columns exactly.
- Regression artifacts: `Sscaler_regre.pkl`, `feature_columns_regre.pkl`, `linreg/xgb/rf_regre_model.pkl` in `notebooks/_elena/models/`. The city regression datasets keep `noise_day/evening/night` as float dB (continuous in Lyon/Berlin, 5-dB steps in Viladecans, zoning limits in Milan).
- ~14% of Viladecans segments (222/1,613) lie >50 m from any noise-map line (rural/coastal south); their "real" values are nearest-neighbour extrapolations (`distance` column in `VIL_noise_streets.gpkg`).
- Viladecans' noise map is the 2017 round (valid 2017–2022); the 2022–2027 map is viewer-only so far.
- Lyon's data is the Plan bruit de la Métropole de Lyon 2022 (data.grandlyon.com / Acoucité, Licence Ouverte): continuous dB GeoTIFF rasters (10 m, EPSG:2154) sampled at street midpoints; road-traffic noise only; Lden→`db_day`/`db_evening`, Ln→`db_night`. Scope limited to the Lyon commune (7,159 segments) to keep momepy's global centralities tractable.
- Pickles are bound to the `data-encoding` env (sklearn 1.8.0, xgboost 3.x) — load them with the same environment.
