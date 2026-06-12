# Testing the Barcelona-trained noise models on other cities

**Date:** 2026-06-12
**Models:** Logistic Regression, XGBoost, Random Forest — trained on `notebooks/_elena/data/bcn_noise_class_ml_dataset.csv`, target **`noise_day`**, saved as pickles in `notebooks/_elena/models/` (see `07_SL_save_model_classification.ipynb`).
**Test notebooks:** `deployment/<City>/notebooks/03_<XXX>_test_bcn_model.ipynb` → results in `deployment/<City>/results/` (predictions CSV + interactive error map HTML).

Noise classes: `0: <40 dB, 1: 40–50, 2: 50–60, 3: 60–70, 4: ≥70`.

---

## Results

### Exact-class accuracy

| Model | Barcelona (held-out 20%) | Viladecans | Milan | Berlin |
|---|---|---|---|---|
| Logistic Regression | 0.606 | **0.558** | 0.650 | 0.265 |
| XGBoost | 0.741 | 0.524 | 0.611 | 0.282 |
| Random Forest | **0.749** | 0.469 | **0.690** | **0.301** |

### Macro F1 / within ±1 class / mean signed error (predicted − real)

| City | Best macro F1 | Within ±1 class (RF) | Signed error range |
|---|---|---|---|
| Viladecans | 0.385 (LogReg) | 0.93 | −0.04 … +0.19 |
| Milan | 0.204 (RF) | 0.99 | −0.31 … +0.16 |
| Berlin | 0.229 (RF) | 0.88 | **+0.68 … +0.87** |

### Real `noise_day` class distribution per city

| Class | Barcelona | Viladecans | Milan | Berlin |
|---|---|---|---|---|
| 0 (<40 dB) | 1% | 0% | 0% | 3% |
| 1 (40–50) | 5% | 10% | 0% | **45%** |
| 2 (50–60) | 29% | 42% | 5% | 32% |
| 3 (60–70) | **54%** | 37% | **94%** | 17% |
| 4 (≥70) | 12% | 11% | 1% | 3% |

---

## What worked

- **The pipeline transfers mechanically without friction.** Because Milan, Viladecans and Berlin were rebuilt to the exact Barcelona schema (same 22 columns, same feature computation methods), the pickled scaler + `feature_columns.pkl` + models apply to any city dataset in three lines (`reindex columns → scaler.transform → model.predict`).
- **The models capture the noise *gradient* everywhere.** 88–99% of predictions land within ±1 class of the truth in every city. Big loud arterials are consistently predicted louder than small residential streets — the learned relationship between road category/centrality/POIs and noise is qualitatively right.
- **Milan and Viladecans are usable results.** ~0.5–0.7 exact accuracy with near-zero systematic bias (signed error ±0.2 classes).
- **Generalization gap is visible and interpretable.** On Viladecans the simple Logistic Regression (0.558) beats Random Forest (0.469): RF memorizes Barcelona-specific patterns (it had 0.998 train accuracy) that don't hold elsewhere, while the smoother linear boundary transfers better. This is a textbook overfitting-to-source signal.

## What didn't work

- **Exact-class accuracy drops everywhere** (0.75 → 0.47–0.69 in Milan/Viladecans, → 0.30 in Berlin).
- **Berlin fails.** All three models systematically overestimate by ~0.7–0.9 classes; Logistic Regression never predicts class 0 or 1 at all, while 48% of Berlin's real streets are in those classes.
- **Milan's headline accuracy is misleading.** Milan's "real" values are 94% class 3, so the trivial baseline "always predict 3" scores 0.94 — better than any model (RF: 0.69, predicting class 2 for ~30% of streets). Macro F1 (~0.20) shows the models don't resolve Milan's (tiny) class variance either.
- **Minority classes are missed.** Class 0 and 4 recall is poor in every target city (see classification reports in the notebooks).

## Causes

**1. Covariate shift: network-scale-dependent features go out of distribution.**
The scaler was fit on Barcelona. Mean |z-score| of each city's features under that scaler (≈1.0 means "looks like Barcelona"):

| Feature | BCN | VIL | MIL | BER |
|---|---|---|---|---|
| dist_to_trunk | 0.9 | 3.7 | 1.3 | **14.7** |
| dist_to_primary | 0.7 | 4.3 | 0.7 | 1.4 |
| closeness_global | 0.8 | **10.1** | 1.1 | 3.5 |
| closeness_400 | 0.8 | **22.2** | 0.9 | 1.9 |
| betweenness | 0.6 | 1.8 | 0.7 | 0.6 |
| width | 0.9 | 0.9 | 0.8 | 0.6 |
| green / signals | 0.6–0.8 | 0.6–0.7 | 0.6–0.8 | 0.5–0.6 |

Global closeness/betweenness and `dist_to_*` are **functions of city size**: in tiny Viladecans (1.6k segments) closeness values are ~10–22 σ above Barcelona's; in huge Berlin (71k segments) closeness shrinks and distances to trunk roads explode (up to ~20 km, 15 σ). Milan (~22k segments, similar metropolitan structure) is the only city that stays in-distribution — and it's where accuracy is highest. Local, per-street features (width, green, signals, POIs) transfer fine everywhere.

**2. Label shift: the cities' noise maps describe different acoustic worlds.**
Barcelona's map says 54% of streets are 60–70 dB; Berlin's says 45% are 40–50 dB. A model trained on Barcelona has a strong prior toward classes 2–3 and reproduces it abroad (Berlin RF predicts 96% class 2–3), which alone explains Berlin's +0.7-class bias. Part of this is real urbanism (Barcelona's dense compact blocks vs Berlin's wide streets and greenery), part is **methodology of the source maps** — each city's strategic noise map uses its own calculation model, coverage and rounding.

**3. Label quality: Milan's targets aren't measurements.**
Milan's noise values come from acoustic zoning *legal limits* (94% one class), not modeled dB like Barcelona/Viladecans/Berlin. Testing against them mostly measures "did the model predict the legal limit", not real noise. Viladecans (real modeled dB, 4 occupied classes, real evening period) is the cleanest external test; Berlin (real modeled dB, 5 occupied classes) is the hardest.

**4. Residual overfitting of the tree models.** RF/XGBoost reach ~0.97–1.00 train accuracy on Barcelona; their advantage over Logistic Regression disappears (Milan, Berlin) or inverts (Viladecans) out-of-domain.

## Recommendations

1. **Use scale-invariant features**: rank-normalize or percentile-scale centralities and `dist_to_*` per city (or fit the scaler on the target city's features) so "the most central street in town" means the same thing in every city.
2. **Prefer Viladecans and Berlin for evaluation**; treat Milan's numbers with caution until a modeled-dB noise map replaces the zoning limits.
3. **Report within-±1-class and macro F1** alongside accuracy — exact-class accuracy on 10-dB bins is harsh and dominated by boundary effects.
4. If per-city calibration is acceptable, a small **fine-tuning step** (refit on a few hundred labeled segments of the target city) would likely fix Berlin's bias.

## Notes / caveats

- Berlin's dataset carries one extra column (`dist_to_main`) not in the Barcelona schema; the test selects features by name so it is ignored, but for strict parity it should be dropped in `01_BER_create_dataset_class.ipynb`.
- ~14% of Viladecans segments (222/1,613) lie >50 m from any noise-map line (rural/coastal south); their "real" values are nearest-neighbour extrapolations (`distance` column in `VIL_noise_streets.gpkg`).
- Viladecans' noise map is the 2017 round (valid 2017–2022); the 2022–2027 map is viewer-only so far.
- Pickles are bound to the `data-encoding` env (sklearn 1.8.0, xgboost 3.x) — load them with the same environment.
