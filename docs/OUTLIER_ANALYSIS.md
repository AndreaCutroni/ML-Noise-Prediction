# Outlier Detection in Regression Models

Identifies streets where model predictions are significantly wrong, links them to street geometry, and produces interactive maps for spatial investigation.

---

## What Is an Outlier

For each model and each street, the **residual** is computed as:

```
residual = noise_actual - noise_predicted
```

- **Positive residual** → model underestimates (street is louder than predicted)
- **Negative residual** → model overestimates (street is quieter than predicted)

A street is flagged as an outlier for a given model when `|residual| > 3 × std(residuals)`. A **consensus outlier** is a street flagged by 2 or more models simultaneously — the strongest and most reliable signal of a genuine anomaly.

---

## Why 3σ

| Threshold | Streets flagged | Interpretation |
|---|---|---|
| 2σ | ~5% of dataset | Many borderline cases |
| 3σ | ~0.3% of dataset | Genuinely unusual streets |
| 4σ | ~0.006% of dataset | Extreme cases only |

3σ was chosen as the working threshold — strict enough to exclude borderline misses, broad enough to surface meaningful spatial patterns.

---

## Data Inputs

| Source | Used For |
|---|---|
| `notebooks/_elena/data/bcn_noise_regre_ml_dataset.csv` | Features (18) + noise targets — 12,854 streets |
| `notebooks/_elena/data/bcn_osmnx_edges.gpkg` | Street geometry (OSMnx edges, EPSG:25831) |

**Join key:** `road_id` in the ML dataset = `{u}_{v}_{key}` constructed from the OSMnx edge node pairs.

---

## Models and Time Periods

| Models | Time Periods |
|---|---|
| Linear Regression, XGBoost, Random Forest | Day, Evening, Night |

All models use the same hyperparameters as `notebooks/_elena/04_SL_regression_*.ipynb` for comparability.  
Train/test split: 80/20, `random_state=42`. Residuals computed on the full dataset so every street can appear on the map.

---

## Results

### Outlier counts (consensus, 3σ)

| Period | LR threshold | XGB threshold | RF threshold | Consensus outliers |
|---|---|---|---|---|
| Day | ±15.9 dB | ±8.1 dB | ±6.5 dB | 127 |
| Evening | ±16.1 dB | ±8.1 dB | ±6.6 dB | 126 |
| Night | ±15.9 dB | ±8.1 dB | ±6.6 dB | 124 |

Linear Regression has a wider threshold because it distributes errors broadly — its residuals have higher variance. XGBoost and Random Forest are tighter, flagging more targeted failures.

### What was discovered during investigation

Searching for outliers surfaced a data quality issue: streets with `noise_actual = 0 dB` — physically impossible in a city — were being predicted at ~35–50 dB by all three models. These were placeholder values in Barcelona's strategic noise map for streets not included in the acoustic simulation.

**Action taken:** Created `bcn_noise_regre_ml_dataset_filtered.csv` by removing 229 streets flagged as consensus outliers at 3σ (12,854 → 12,625 streets). This file is used by the filtered regression notebooks.

---

## Output Files

```
outliers/
├── notebooks/
│   └── outlier_analysis.ipynb
└── results/
    ├── outliers_regression_day.csv
    ├── outliers_regression_evening.csv
    ├── outliers_regression_night.csv
    ├── map_outliers_day.html
    ├── map_outliers_evening.html
    └── map_outliers_night.html
```

### CSV schema

| Column | Description |
|---|---|
| `road_id` | Street segment identifier (`{u}_{v}_{key}`) |
| `noise_actual` | Ground truth noise level (dB) |
| `pred_lr` / `pred_xgb` / `pred_rf` | Model predictions (dB) |
| `resid_lr` / `resid_xgb` / `resid_rf` | Residuals per model (actual − predicted) |
| `outlier_lr` / `outlier_xgb` / `outlier_rf` | 1 if flagged, 0 otherwise |
| `consensus` | Count of models that flagged this street (0–3) |

### Interactive maps

One Folium HTML map per time period. All streets are shown for spatial context.

| Colour | Meaning |
|---|---|
| Yellow (thin) | Normal street — within threshold |
| Red (thick) | Consensus outlier — model underestimates (street is louder than predicted) |
| Blue (thick) | Consensus outlier — model overestimates (street is quieter than predicted) |

Clicking an outlier street opens a popup with:
- Street name and `road_id`
- Actual noise level
- Prediction and residual for each model
- Number of models that flagged it
- Clickable links to Google Maps and OpenStreetMap at street level

---

## Notebook

`outliers/notebooks/outlier_analysis.ipynb` — self-contained, reproducible. Re-running it regenerates all CSVs and maps from scratch using the source dataset.
