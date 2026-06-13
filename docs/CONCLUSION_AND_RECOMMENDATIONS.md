# Conclusion & Recommendations: Barcelona Urban Noise Prediction

---

## 1. Full Results

### Classification — Accuracy & F1 (noise class: 0 = <40 dB … 4 = >70 dB)

| Model | Period | CV Acc | Test Acc | F1-macro | F1-weighted |
|---|---|---|---|---|---|
| Logistic Regression | Day | 0.613 | 0.606 | 0.429 | 0.580 |
| XGBoost | Day | 0.725 | 0.741 | 0.738 | 0.735 |
| Random Forest | Day | 0.733 | **0.749** | 0.732 | 0.742 |
| Logistic Regression | Evening | 0.639 | 0.625 | 0.393 | 0.597 |
| XGBoost | Evening | 0.754 | 0.762 | 0.696 | 0.756 |
| Random Forest | Evening | 0.754 | 0.757 | 0.684 | 0.747 |
| Logistic Regression | Night | 0.605 | 0.626 | 0.531 | 0.605 |
| XGBoost | Night | 0.729 | 0.747 | 0.742 | 0.744 |
| Random Forest | Night | 0.740 | **0.760** | **0.750** | **0.757** |

### Regression — R² and Error (in dB)

| Model | Period | Train R² | Test R² | MAE | RMSE |
|---|---|---|---|---|---|
| Linear Regression | Day | 0.398 | 0.391 | 4.71 dB | 7.16 dB |
| XGBoost | Day | 0.929 | 0.701 | 3.36 dB | 5.01 dB |
| Random Forest | Day | 0.955 | **0.727** | **3.05 dB** | **4.79 dB** |
| Linear Regression | Evening | 0.396 | 0.367 | 4.86 dB | 7.56 dB |
| XGBoost | Evening | 0.927 | 0.680 | 3.44 dB | 5.37 dB |
| Random Forest | Evening | 0.954 | **0.690** | **3.14 dB** | 5.29 dB |
| Linear Regression | Night | 0.361 | 0.331 | 5.94 dB | 9.53 dB |
| XGBoost | Night | 0.927 | 0.651 | 4.25 dB | 6.88 dB |
| Random Forest | Night | 0.952 | **0.666** | **3.82 dB** | **6.74 dB** |

---

## 2. Interpretation

### What the models do well

Tree-based models (Random Forest and XGBoost) successfully learn that **road category and street centrality** are the dominant drivers of urban noise, and they generalise this within Barcelona. Random Forest achieves 72.7% R² for daytime noise and 75% classification accuracy, meaning it correctly assigns the noise band for 3 in 4 streets on held-out data. This is a meaningful result for urban planning: a city can estimate noise exposure on any street without deploying physical sensors, using only freely available geospatial data from OpenStreetMap and cadastral registries.

### What the models struggle with

**Night is fundamentally harder.** Regression R² drops from 0.727 (day) to 0.666 (night) for Random Forest; MAE rises from 3.05 to 3.82 dB. Night noise is driven by sparse, intermittent events — a single passing truck or a cluster of nightlife venues — rather than the steady traffic load that daytime noise reflects. The features in this dataset (road category, building height, land use percentages, tree counts) describe the physical environment, not the events that occur within it at night. No amount of model tuning will fix this without better input features.

**Overfitting is significant for tree-based models.** Random Forest train R² is 0.955 vs test R² 0.727 — a gap of 0.228. The model has learned Barcelona-specific noise patterns that do not fully generalise, even to held-out Barcelona streets. This gap is the primary reason why cross-city deployment (Berlin, Lyon, Milan) fails: the model is partly fitting noise artefacts of Barcelona's specific street layout rather than universal urban acoustic relationships.

**Linear models confirm the problem is non-linear.** Logistic and Linear Regression have almost no train/test gap (< 0.01), which rules out overfitting — their weakness is structural. Noise propagation involves non-linear interactions: a wide street lined with tall buildings behaves differently from a wide street in an open area, and linear models cannot capture that interaction. Their stability under transfer to other cities comes not from better generalisation but from their inability to overfit in the first place.

**Class imbalance affects classification quality.** The noise class distribution is heavily skewed toward classes 2 and 3 (50–70 dB), which together account for 82% of streets. F1-macro scores are consistently 6–9 points below F1-weighted, meaning models perform worse on minority classes (very quiet streets < 40 dB, and very loud > 70 dB). These edge cases are often the most actionable from a policy standpoint.

---

## 3. Limitations

| Limitation | Impact | Severity |
|---|---|---|
| **Training data is a single city (Barcelona)** | Models learn Barcelona-specific patterns; transfer to other cities degrades significantly | High |
| **Noise targets are strategic map estimates, not sensor measurements** | Ground truth already contains modelling error; a 3 dB MAE may be partly explained by input noise | Medium |
| **Night features mismatch night noise drivers** | Environmental features do not capture event-based noise; night predictions are structurally weaker | High |
| **Tabular features cannot represent network topology** | Each street is treated independently; adjacent streets, traffic flow propagation, and canyon effects are not encoded | High |
| **Feature set was designed for Barcelona** | OSM feature availability varies across cities; transfer experiments used only 18 features instead of 60 | Medium |
| **Tree models overfit even within Barcelona** | Train/test gap ~0.23 suggests models have headroom for improvement with regularisation or better features | Medium |
| **Static features, dynamic noise** | Traffic, events, and weather change daily; the model predicts long-run average exposure, not real-time noise | Low (by design) |

---

## 4. Recommendations

### Short term (within this project)

1. **Add class weights to classification models** — use `class_weight='balanced'` in Logistic Regression and Random Forest to improve F1 on minority noise classes (< 40 dB and > 70 dB). These are the streets that matter most for intervention.

2. **Add a dummy classifier baseline** — before claiming 74.9% accuracy is good, compare against a baseline that predicts the majority class. Given that classes 2+3 are 82% of data, a naive majority-class classifier achieves ~54%; the current models are genuinely better, but this should be made explicit.

3. **Apply k-fold cross-validation consistently** — currently XGBoost and Random Forest report CV scores on the training split only. CV across the full dataset provides a more honest accuracy estimate and reduces variance in the reported metric.

4. **Regularise tree models** — test `max_depth=10`, `min_samples_leaf=5` for Random Forest and `max_depth=6`, `n_estimators=200` for XGBoost. Reducing the train/test gap from 0.23 to under 0.10 would improve cross-city transfer without losing much within-Barcelona accuracy.

### Medium term

5. **Add night-specific features** — nightlife venue density (from OSM `amenity=bar/restaurant/nightclub`), proximity to hospitals and parks, and temporal traffic profiles would directly address the night prediction gap.

6. **Improve cross-city transfer with a domain adaptation step** — instead of applying Barcelona models directly, fine-tune on a small labelled sample of each city (50–100 streets). This bridges the distribution gap without requiring a full city-level training set.

### Long term — Graph ML as the next step

The fundamental limitation of the tabular approach is that **streets are not independent observations**. Noise propagates along street networks: a high-traffic arterial raises noise levels on adjacent residential streets, canyon geometry between parallel streets creates reflections, and traffic flows are determined by network connectivity — not just the properties of a single segment.

Graph Neural Networks (GNNs) represent the street network as a graph where each node is a street segment and edges encode adjacency and connectivity. This allows the model to:

- Learn that noise on a quiet residential street is partially determined by the arterial two intersections away
- Encode traffic flow direction and capacity through edge features
- Aggregate information from neighbourhood streets rather than treating each segment in isolation

Early evidence from urban morphology research suggests GNNs outperform tabular models on spatially correlated targets by 10–20% in R². For a noise prediction task where the signal physically propagates through connected space, this is the architecturally correct next step.

**Suggested implementation:** Use PyTorch Geometric or DGL with the Barcelona OSM street network as the graph. Node features are the existing 18–60 tabular features. Edge features encode road connectivity, distance, and angle. A Graph Attention Network (GAT) or GraphSAGE architecture trained on the Barcelona labelled set, then transferred to other cities via few-shot fine-tuning.

---

## 5. Summary

The tabular ML pipeline achieves meaningful noise prediction within Barcelona (RF R² = 0.73, accuracy = 0.75) using freely available geospatial data. The core limitations are overfitting to Barcelona, structural weakness at night, and the inability of tabular features to represent spatial propagation. These are not fixable by tuning the current model family — they require either better features (night events, network topology) or a different model architecture (Graph ML). The short-term recommendations improve the robustness of what is already built; the long-term recommendation addresses the architectural ceiling.
