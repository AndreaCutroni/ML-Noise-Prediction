# Linear Regression — Results Analysis

**Model:** Linear Regression  
**Target:** `noise_day` (daytime street noise, in dB)  
**Dataset:** `bcn_noise_ml_dataset.csv` — 16,772 street segments, Barcelona  

---

## Results

| Metric | Value |
|---|---|
| MAE (Mean Absolute Error) | **4.68 dB** |
| R² (R-squared) | **0.386** |

---

## What These Numbers Mean

### MAE = 4.68 dB — The Average Mistake

MAE is the average gap between what the model predicted and what the real noise level was.

On average, the model is **4.68 decibels off** per street.

To put that in perspective:
- The human ear starts noticing a difference at around **3 dB**
- A jump of **10 dB** sounds roughly *twice as loud*

So a 4.68 dB error is noticeable. If a street is actually **65 dB**, the model might say it is **60 dB or 70 dB**. That is not precise enough to be relied on for real decision-making.

---

### R² = 0.386 — How Much the Model Explains

R² answers: *"How much of the noise variation across streets does your model actually explain?"*

All 16,772 streets have different noise levels — some quiet, some very loud. Something causes that variation (road width, traffic, trees, buildings, etc.). R² = 0.386 means:

> The model explains **38.6%** of why streets differ in noise.  
> The remaining **61.4%** is still a mystery to it.

| R² value | Meaning |
|---|---|
| 1.0 | Perfect — every prediction is exact |
| 0.386 | Partial — the model captures less than half the picture |
| 0.0 | Useless — no better than guessing the average every time |

---

## Why the Model is Struggling

Linear regression fits a straight line through the data. Urban noise does not behave in a straight line:

- A wide road is noisier — **but only if it also carries heavy traffic**. Those two things multiply each other, they do not simply add up.
- Trees reduce noise — **but only slightly**, and their effect disappears near a motorway.
- `road_category` steps are uneven — the jump from a residential street to an arterial road is a massive noise increase, not a gentle linear step.

The model cannot see any of this. It tries its best with a flat surface across all features, but the real relationship is curved and conditional.

---

## Residual Analysis

A **residual** is simply: `actual noise − predicted noise`. If the model were perfect, every
residual would be 0. The two plots below reveal where and how the model is failing.

---

### Left Plot — Residuals vs Predicted

The most striking feature is the **diagonal stripes** running across the plot.

**Why the stripes exist:** `noise_day` is not recorded in fine detail — it comes in
**jumps of 5 dB** (45, 50, 55, 60, 65, 70, 75 dB). The model however predicts *continuous*
numbers like 58.3, 61.7, etc. For any given predicted value on the X-axis, there are only a
handful of possible actual values. Each stripe is one actual noise level. The stripes slope
downward because as the predicted value increases, the residual for each fixed actual value
decreases.

> In short: **the target variable is discrete but the model predicts continuous values** —
> the stripes are a fingerprint of that mismatch.

**The cluster of points with residuals of −40 to −60 dB** (bottom left) is serious. These
are streets where the model predicted something like 65 dB but the real noise was only
10–25 dB. The model is wildly overestimating some quiet streets — probably because they have
wide roads or high road categories but are actually quiet for reasons the model cannot see
(e.g. no actual traffic, surrounded by parks).

A good residual plot would show a **random cloud** of dots scattered evenly above and below
the zero line, with no pattern. These stripes confirm the opposite.

---

### Right Plot — Distribution of Residuals

The histogram shows how often each size of error occurs.

- The bulk of errors sit between **−10 and +10 dB** — the model is roughly in the right
  ballpark for most streets.
- There is a long **tail stretching to −60 dB** on the left — these are the same badly
  overestimated streets from the left plot.
- A **perfect model** would produce a narrow bell shape centred exactly at 0. What we have
  is skewed heavily to the left, meaning the model's mistakes are not symmetric — it
  overestimates more often and more severely than it underestimates.

---

### Summary

| Observation | What it means |
|---|---|
| Diagonal stripes | Target noise is discrete (5 dB steps); linear model cannot handle this naturally |
| Points at −40 to −60 dB | Model badly overestimates some quiet streets |
| Left-skewed histogram | Errors are not random — the model has a systematic bias |
| No random cloud | Clear sign that a straight-line model is missing non-linear structure |

All of this reinforces the MAE and R² conclusion — the patterns in the residuals are exactly
what would be expected to disappear once we switch to a non-linear model like Random Forest.

---

## Feature Coefficient Analysis

Each bar in the coefficient plot answers: **"if this feature increases by 1 step, how many
dB does the model add or subtract from its prediction?"**

- **Blue bar (right)** = feature pushes predicted noise **up** (louder)
- **Orange bar (left)** = feature pushes predicted noise **down** (quieter)
- **Longer bar** = stronger influence on the prediction

---

### Top Drivers of Noise (Positive Coefficients)

| Feature | Coefficient | Plain English |
|---|---|---|
| `road_width` | +1.1 dB | Wider road → louder. More lanes, more traffic. |
| `catastral_bldg_floors_mean_50m` | +1.05 dB | Taller buildings nearby → louder. Denser urban areas with more traffic and sound bouncing off walls. |
| `edge_betweenness` | +0.85 dB | Network centrality score — how many city routes pass through this street. High score = busy junction = noisier. |
| `signal_count_50` | +0.65 dB | More traffic signals → more cars stopping and starting → louder. |
| `transport_count_50` | +0.5 dB | More bus stops / metro entrances nearby → more activity → louder. |

---

### Top Reducers of Noise (Negative Coefficients)

| Feature | Coefficient | Plain English |
|---|---|---|
| `road_category_5` | −6.0 dB | Relative to category 1 (busiest roads), category 5 streets are much quieter. Category 1 is the baseline — all others are compared to it. |
| `road_category_6` | −3.5 dB | Same logic — quieter than category 1. |
| `road_category_4` | −2.5 dB | Progressively closer to category 1 in loudness. |
| `osm_green_pct_50m` | −2.0 dB | More green space within 50m → quieter. Parks absorb sound and attract less traffic. |
| `openness` | −1.6 dB | More open street (not enclosed by tall buildings) → sound dissipates freely instead of bouncing. |
| `slope_pct` | −1.5 dB | Steeper streets are quieter — in Barcelona these tend to be hillside roads (Tibidabo, Montjuïc) with less through-traffic. |
| `osm_residential_pct_50m` | −1.0 dB | More residential land nearby → quieter neighbourhoods with less commercial activity. |

---

### Surprising Results

**`tree_count_50` is slightly positive (+0.02 dB)** — you would expect trees to reduce noise.
The coefficient is near zero so it barely matters, but the slight positive value is likely
because trees in Barcelona are planted *along busy roads*. The model sees "trees = busy road"
rather than "trees = quieter". This is a classic case of **correlation being confused with
causation** — the model cannot tell the difference.

**`road_length` is negative (−0.8 dB)** — longer streets being quieter seems odd. In
Barcelona this likely reflects that longer continuous streets tend to be in the outer,
less-dense parts of the city.

---

### The Road Category Pattern

`road_category_2` through `road_category_6` are all negative because `road_category_1` was
used as the **baseline** during one-hot encoding. Every other category is compared *against*
category 1 — the loudest road type. A negative coefficient simply means "quieter than a
category 1 road".

---

### Caveat

These coefficients describe what the **linear model learned** — not necessarily the truth.
With R² = 0.386 the model only explains 38% of the variation, so these weights are a rough
approximation. A Random Forest will give more reliable feature importances once trained.

---

## Conclusion

| | Achieved | Target |
|---|---|---|
| MAE | 4.68 dB | < 3 dB |
| R² | 0.386 | > 0.7 |

**Linear regression is not sufficient for this problem** — but this is expected and useful. It confirms that the relationship between street features and noise levels is genuinely non-linear.

### Next Step — Random Forest

Random Forest trains hundreds of decision trees and averages their predictions. It handles non-linear relationships and feature interactions automatically, without needing any extra configuration. It is the recommended next model to try (see `docs/LINEAR_REGRESSION.md`, Part 4 Option B).

Expected improvement: R² above 0.7 and MAE below 3 dB.
