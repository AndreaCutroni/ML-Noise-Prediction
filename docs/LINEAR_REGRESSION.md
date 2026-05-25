# Proposal: Noise Prediction with Machine Learning

## What Are We Trying to Do?

We want to predict how loud a street in Barcelona is (its noise level in decibels) using
characteristics of that street — like how wide it is, how many trees are nearby, what kind
of buildings surround it, and so on.

Our dataset (`bcn_noise_ml_dataset.csv`) has **16,772 street segments** and contains three
target noise measurements (what we want to predict):

| Column | Meaning |
|---|---|
| `noise_day` | Average daytime noise (dB) |
| `noise_evening` | Average evening noise (dB) |
| `noise_night` | Average nighttime noise (dB) |

And **46 input features** (the information we use to make predictions), including:
- Road properties: `road_length`, `road_category`, `one_way`, `road_width`, `distance_to_road`
- Surroundings: `slope_pct`, `openness`, `edge_betweenness`
- Land use within 50m: `osm_commercial_pct_50m`, `osm_green_pct_50m`, `osm_residential_pct_50m`, etc.
- Buildings: `catastral_bldg_floors_mean_50m`, `catastral_bldg_floors_max_100m`, etc.
- Counts of trees, signals, POIs, transport stops (at 10m, 20m, 50m buffers)
- Building use categories at 100m and 150m buffers

---

## Part 1 — What is Linear Regression?

### The Core Idea

Imagine you want to predict how noisy a street will be. You notice that wider roads tend
to be noisier. If you plotted **road width** on the X-axis and **noise level** on the Y-axis
for every street, you would see a scatter of dots that roughly goes upward — the wider the
road, the louder it tends to be.

**Linear regression draws the best possible straight line through those dots.**

Once you have that line, you can pick any road width, look where it falls on the line, and
read off a predicted noise value. That is the entire idea.

### With Multiple Features (Multiple Linear Regression)

We have 46 features, not just one. The math extends naturally:

```
noise_day = w1 × road_width
           + w2 × road_length
           + w3 × tree_count_50
           + w4 × road_category
           + ...
           + bias
```

Each feature gets a **weight** (also called a coefficient). The model learns what weight to
give each feature so that its predictions are as close as possible to the real noise values.
A large positive weight means "the more of this, the louder"; a large negative weight means
"the more of this, the quieter".

### What "Training" Means

We split the dataset into two parts:
- **Training set (~80%)** — the model studies these rows and learns the weights.
- **Test set (~20%)** — we hide these rows from the model, ask it to predict, and see how
  close its guesses are to reality.

### How We Measure Error

Two common metrics:
- **MAE (Mean Absolute Error)** — on average, how many dB off is each prediction?
  A MAE of 3 dB means predictions are off by about 3 dB on average. Easy to understand.
- **R² (R-squared)** — ranges from 0 to 1. R² = 0.8 means the model explains 80% of the
  variation in noise. Closer to 1 is better.

### Why Linear Regression Might Give Bad Results Here

Noise in cities is not a simple straight-line phenomenon:
- A road with 0 trees and a road with 100 trees might both be loud if they are next to a
  motorway — the tree effect is **conditional** on other features.
- The relationship between `road_category` (1, 2, 3…) and noise is probably not a simple
  multiply — going from category 1 to 2 may be a much bigger jump than from 2 to 3.
- Interactions between features (e.g., a wide road *and* high traffic category together)
  multiply the noise effect, not add it.

Linear regression cannot capture these interactions by itself. That is why non-linear
models are worth trying.

---

## Part 2 — Data Encoding (Required Before Any Model)

Raw data needs to be prepared before feeding it into a model. The following encoding steps
are needed:

### 2.1 — Ignore Non-Feature Columns

`street_id`, `fid`, and `TRAM` are identifiers, not features. You do not need to drop them
— just never include them when you define `X`. The original DataFrame stays untouched.

### 2.2 — Handle Categorical Columns

`road_category` contains category numbers (1, 2, 3…). Even though it looks numeric, the
numbers are **labels**, not quantities. We should convert it with **One-Hot Encoding**:
instead of one column with values 1/2/3, we create separate binary columns:
`road_category_1`, `road_category_2`, `road_category_3`, each containing 0 or 1.

`one_way` is already binary (0 or 1) — no change needed.

### 2.3 — Feature Scaling (Standardization)

Features have very different ranges:
- `road_length` can be 30–500 metres
- `openness` is between 0 and 1
- `poi_count_50` can be 0–50

Linear regression is sensitive to scale — a feature with large numbers will appear more
important just because its values are larger. We **standardize** each feature to have mean
= 0 and standard deviation = 1 (called `StandardScaler` in scikit-learn).

### 2.4 — Check for Missing Values

Before training, verify no columns have NaN values. If they do, either drop those rows or
fill them with the column mean/median.

### 2.5 — Choose the Target

We will start by predicting **`noise_day`** (daytime noise). Evening and night follow the
same process and can be done later.

---

## Part 3 — Implementation Plan

### Step 1: Setup Notebook

Create `notebooks/analysis/linear_regression.ipynb`.

Install/import: `pandas`, `numpy`, `scikit-learn`, `matplotlib`, `seaborn`.

### Step 2: Load and Inspect the Data

```python
import pandas as pd
df = pd.read_csv('data/machine_learning/bcn_noise_ml_dataset.csv')
df.info()
df.describe()
df[['noise_day', 'noise_evening', 'noise_night']].hist()
```

### Step 3: Data Encoding

```python
# Select only the columns we want as features — ID columns are simply never included
ignore = ['street_id', 'fid', 'TRAM', 'noise_day', 'noise_evening', 'noise_night']
feature_cols = [col for col in df.columns if col not in ignore]

X = df[feature_cols].copy()
y = df['noise_day']

# One-hot encode road_category on X only
X = pd.get_dummies(X, columns=['road_category'], drop_first=True)

# Train/test split
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Scale features
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test  = scaler.transform(X_test)
```

### Step 4: Train Linear Regression

```python
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score

model = LinearRegression()
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
print("MAE:", mean_absolute_error(y_test, y_pred))
print("R²:", r2_score(y_test, y_pred))
```

### Step 5: Visualise Results

- Scatter plot: predicted vs actual noise values (a perfect model gives a diagonal line).
- Plot feature coefficients to see which features the model found most important.
- Plot residuals (errors) — if they show a pattern, the model is missing something the
  linear formula cannot capture.

---

## Part 4 — Non-Linear Models (If Linear Regression Underperforms)

If R² is below ~0.6 or MAE is above ~5 dB, we try these models in order of complexity:

### Option A — Decision Tree Regressor

A tree splits the data step-by-step using rules like "if road_width > 20 AND road_category
is 1, then noise is around 68 dB". Captures non-linear patterns automatically. Easy to
interpret but can overfit.

```python
from sklearn.tree import DecisionTreeRegressor
tree = DecisionTreeRegressor(max_depth=10, random_state=42)
tree.fit(X_train, y_train)
```

### Option B — Random Forest Regressor (Recommended First Non-Linear Try)

Trains hundreds of decision trees on random subsets of the data and averages their
predictions. More robust than a single tree and handles complex feature interactions well.
Typically gives a significant improvement over linear regression for this type of data.

```python
from sklearn.ensemble import RandomForestRegressor
rf = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
rf.fit(X_train, y_train)
```

Random Forest also gives **feature importances** — a ranked list of which features matter
most. This is useful for understanding what drives noise levels.

### Option C — Gradient Boosting (XGBoost / LightGBM)

Builds trees sequentially, each one correcting the errors of the previous one. Usually the
best-performing model for structured/tabular data. Slightly harder to tune.

```python
from sklearn.ensemble import GradientBoostingRegressor
gb = GradientBoostingRegressor(n_estimators=200, learning_rate=0.1, max_depth=5)
gb.fit(X_train, y_train)
```

---

## Part 5 — Comparison Table

At the end of the notebook, compare all models in a summary table:

| Model | MAE (dB) | R² |
|---|---|---|
| Linear Regression | ? | ? |
| Decision Tree | ? | ? |
| Random Forest | ? | ? |
| Gradient Boosting | ? | ? |

Fill in results after running each model.

---

## Deliverables

| Item | Location |
|---|---|
| Main notebook | `notebooks/analysis/linear_regression.ipynb` |
| Dataset used | `data/machine_learning/bcn_noise_ml_dataset.csv` |
| This proposal | `proposal.md` |

---

## Summary of Steps

1. Load `bcn_noise_ml_dataset.csv` (16,772 rows, 49 columns)
2. Encode the data: select feature columns (ignoring IDs), one-hot `road_category`, scale features
3. Train/test split (80/20)
4. Train Linear Regression → report MAE and R²
5. If results are poor, try Random Forest → report MAE and R²
6. If time allows, try Gradient Boosting → compare all three
7. Plot predictions vs actuals and feature importances
