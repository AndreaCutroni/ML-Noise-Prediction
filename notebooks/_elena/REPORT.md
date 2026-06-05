## Data Sources

### Base Geometry
OSM road geometry was used as the reference geometry for the analysis.

### Noise Data
Noise levels were taken from Barcelona Open Data and assigned to OSM road segments using the closest available match.

## Feature Set

1   road_category          11711 non-null  int64  
2   dist_to_trunk          11711 non-null  float64
3   dist_to_primary        11711 non-null  float64
4   dist_to_secondary      11711 non-null  float64
5   dist_to_tertiary       11711 non-null  float64
6   dist_to_residential    11711 non-null  float64
7   dist_to_living_street  11711 non-null  float64
8   signals                11711 non-null  float64
9   transport              11711 non-null  float64
10  pois                   11711 non-null  float64
11  width                  11711 non-null  float64
12  height                 11711 non-null  float64
13  betw_centrality        11711 non-null  float64
14  clos_centrality        11711 non-null  float64
15  green_100              11711 non-null  float64
16  straightness           11711 non-null  float64
17  closeness400           11711 non-null  float64

### Road Category
`road_category` was tested with both one-hot encoding and label encoding. The current workflow keeps the label-encoded version.

### Distance to Road Categories
The following distance-to-category variables were included:
1. `dist_to_trunk`
2. `dist_to_primary`
3. `dist_to_secondary`
4. `dist_to_tertiary`
5. `dist_to_residential`
6. `dist_to_living_street`

### Width
Road width was estimated as total building-to-building width using roads and buildings through `momepy`.

### Centrality
The network-based features include:
1. Edge-based betweenness centrality
2. Global closeness, aggregated from nodes to edges
3. Local closeness, aggregated from nodes to edges
4. Straightness, aggregated from nodes to edges

### Points and Mobility
1. POIs were filtered to keep engagement-related POIs.
2. Traffic-related POIs and transport variables were treated as related candidates.
3. Signals were kept without additional filtering.

Point counts were computed using a 50 m buffer and a road length window of 100 m.

### Green Percentage
From land-use data, only green percentage was kept, defined as the share of a 50 m buffer covered by green land use. Commercial and industrial land-use candidates were not retained because commercial activity was already partly represented by POIs.

### Slope and Height
Slope and height were derived from LiDAR data. These features were later dropped to improve reproducibility.

## Regression Baseline
Regression was tested first, with the goal of predicting noise in dB. In practice, the assigned road values were not truly continuous, but discretized in 5 dB steps. This limited the suitability of a regression formulation.

The observed performance was:
1. Linear Regression: about 0.38
2. XGBoost Regression: about 0.56, with signs of overfitting
3. Neural network regression: not competitive

Some outliers were identified as tunnels and removed from the dataset.

## Classification Setup
The task was then reformulated as 5-class classification:
1. `<40 dB`
2. `40-50 dB`
3. `50-60 dB`
4. `60-70 dB`
5. `>70 dB`

In this setting, Linear Regression reached about 0.57, Random Forest about 0.60, and XGBoost about 0.71. XGBoost was the strongest model, with class 3 being the easiest to predict, followed by class 0.

## Ablation Study
The ablation study was designed to answer four questions:
1. Is `road_category` informative on its own, or are the distance-to-category variables more useful?
2. Do engineered features improve the baseline?
3. Can engineered interaction features replace their raw inputs?
4. Which original features or feature groups can be removed without hurting performance?

Results of the ablation study was that drpping height and road category improved results, as well as adding distance to main roads (trunk, primary, secondary) and distance to local road (tertiary, residential, living street). Additionally, replacing width adn betwenness centrality with their combination further improved the result.