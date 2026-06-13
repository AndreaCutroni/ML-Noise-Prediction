# Regression Analysis: Models × Time Periods

Barcelona street noise prediction — three regression models evaluated across daytime, evening, and night targets.

---

## Results

### Test-set R² (how much variance the model explains)

| Model | Day | Evening | Night |
|---|---|---|---|
| Linear Regression | 0.391 | 0.367 | 0.331 |
| XGBoost | 0.698 | 0.680 | 0.651 |
| Random Forest | **0.727** | **0.691** | **0.666** |

### MAE — Mean Absolute Error (average prediction error in dB)

| Model | Day | Evening | Night |
|---|---|---|---|
| Linear Regression | 4.71 dB | 4.86 dB | 5.94 dB |
| XGBoost | 3.37 dB | 3.44 dB | 4.25 dB |
| Random Forest | **3.05 dB** | **3.14 dB** | **3.82 dB** |

### RMSE — Root Mean Squared Error (penalises large errors more)

| Model | Day | Evening | Night |
|---|---|---|---|
| Linear Regression | 7.16 dB | 7.56 dB | 9.53 dB |
| XGBoost | 5.04 dB | 5.37 dB | 6.88 dB |
| Random Forest | **4.79 dB** | **5.28 dB** | **6.74 dB** |

### Train vs Test R² (overfitting check)

| Model | Train (Day) | Test (Day) | Gap |
|---|---|---|---|
| Linear Regression | 0.398 | 0.391 | 0.007 |
| XGBoost | 0.928 | 0.698 | 0.230 |
| Random Forest | 0.955 | 0.727 | 0.228 |

---

## Analysis

### 1. Model ranking is consistent across all time periods

Random Forest > XGBoost > Linear Regression — on every metric, every time period. The ranking never changes, which means the structural advantages of each model (non-linearity, ensemble variance reduction) hold regardless of which noise target is used.

### 2. All models degrade from day → evening → night

Night is the hardest to predict. Linear Regression's MAE jumps from 4.71 dB (day) to 5.94 dB (night) — a 26% degradation. Random Forest degrades less (3.05 → 3.82 dB, +25%) and XGBoost similarly.

**Why night is harder:**
Night noise is dominated by intermittent events (individual vehicles, nightlife) rather than the steady traffic flow that day/evening noise reflects. The urban morphology and infrastructure features in this dataset were designed to explain persistent noise exposure, not sporadic peaks. The lower R² at night (0.33–0.67 vs 0.39–0.73 at day) confirms the model has less explanatory power when noise behaviour is less predictable.

### 3. Linear Regression barely overfits — but is consistently weak

Train R² ≈ Test R² for Linear Regression across all periods (gap < 0.01). This means the model has seen everything it is capable of learning from the data. Its weakness is not overfitting — it is underfitting. The relationship between urban features and noise is non-linear, and a linear model cannot capture that complexity regardless of how much data it sees.

**Implication for deployment:** Linear Regression is the most stable model when transferring to other cities (Berlin, Milan, Lyon) precisely because its simplicity prevents it from overfitting Barcelona-specific noise patterns. But its absolute error (4.71–5.94 dB) is too high for operational use.

### 4. Tree-based models overfit significantly

Both XGBoost and Random Forest have train R² > 0.92 but test R² of 0.65–0.73 — a gap of ~0.23 across all periods. This is a consistent and substantial overfitting signal. The models have memorised fine-grained patterns in the Barcelona training streets that do not fully generalise, even to other Barcelona streets in the held-out 20%.

This overfitting becomes critical during cross-city deployment (see `BCN_MODEL_TRANSFER_REPORT.md`): the Barcelona-trained tree models perform poorly in Berlin and Lyon because the overfitted patterns are city-specific.

### 5. Random Forest vs XGBoost — small real-world difference

Random Forest outperforms XGBoost on test R² by 0.015–0.029 across the three periods. In MAE terms this is 0.3–0.4 dB. For a noise mapping application this difference is practically negligible (regulatory noise thresholds are defined in 5 dB bands). Both models provide similar operational value; the choice between them should be driven by deployment and interpretability needs rather than raw accuracy.

---

## Summary

| | Best model | Hardest period | Key limitation |
|---|---|---|---|
| Accuracy | Random Forest | Night | Overfitting (train/test gap ~0.23) |
| Stability | Linear Regression | Night | Underfitting (R² caps at ~0.39) |
| Deployment | Linear Regression | Night | Weak but generalises cross-city |

The core tension in this project: tree-based models are accurate enough for Barcelona but overfit too much to transfer reliably. Linear Regression is stable enough to transfer but not accurate enough to be useful. Closing this gap is the motivation for exploring Graph ML as a next step — street network structure (topology, connectivity) is not captured by tabular features alone.

---

## Setup

- Dataset: `data/machine_learning/bcn_noise_ml_dataset.csv` — 16,772 Barcelona street segments
- Train/test split: 80/20, random_state=42
- Preprocessing: StandardScaler on all features
- Features: 60 columns (road morphology, building height, land use, centrality, trees, traffic, POIs)
- Notebooks: `notebooks/_elena/04_SL_regression_day/evening/night.ipynb`
