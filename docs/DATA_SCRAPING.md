# Noise dataset

The original dataset is "2017 tramer mapa estrategic soroll bcn". 

This dataset was preprocessed in QGis removing the closed poyllines and keeping only the open polylines, which approximately overlap with the osm_roads.

The coordinate system is the standard for Barcelona: EPSG:25831 - ETRS89 / UTM zone 31N.

TRAM = TRAMO (street segment ID)

The first 3 columns were considered:
- TOTAL_D: dB during the day
- TOTAL_E: dB during the evening
- TOTAL_N: dB during the night

The length of the segment could be meaningful becuase it represents the distance betwenn two crosses.

Transforming noise into logaritmic scale decrease correlation rather than increasing it.

# Open Street Map

Open street map data were downloaded from Internet. In the data processing phase, they are either loaded from file or with the command: ox.features_from_place("Barcelona, Spain", tags={"some_key": "some_value"}).

The geometry is always projected to EPSG:25831 - ETRS89 / UTM zone 31N for being compared with noise dataset.

## Roads

### Road category

We preprocessed the road dataset to exclude the follwoing categoreis:
- "path", "track" and "service", as they do not overlap any noise segment. 
- "pedestrian", "footway" and "cycleway", as they are mainly parallel to major roads. 
- "steps" and links as non relevant.
- "motorway" and "busway" because very little represented.

Following the priority: 'trunk', 'primary', 'secondary', 'tertiary', 'residential', 'living_street'.
We checked if there is any road of that category in a 5 m buffer from noise segment, and in positive case, assign it. Categories are labeled encoded with an integer from 1 to 6.

### Maxspeed, width, lanes, oneway

OSM data for max speed, width and lanes is very sparse (mostly NaN). 

## Building height / number of floors

We documented the building-height workflow with three different approaches.
OSM building heights were too sparse to cover Barcelona consistently. Cadastral floor counts were much more precise, but converting floors to meters was unstable because floor-to-floor height varies across buildings. For that reason, we compared two LiDAR Digital Surface Model TIFFs (`Catalunya-1mtif1777965317095.tif` and `Catalunya-1mtif1777965631099.tif`) as height sources and kept these data as the most complete city-wide solution.

## Points of Interest

POIs were classified with overlapping flags instead of one hard label, so a single point can be daytime and continuous at the same time. We used these groups:

- `daytime` / `nighttime`: when the place is most active
- `continuous` / `discontinuous`: whether the use is steady or event-like
- `transport_related`: mobility nodes such as stops, stations, parking, bike and rental facilities
- `support_infrastructure`: utility and city-support uses such as recycling, lockers, bins, toilets, ATMs
- `noise_sensitive`: uses where noise is more problematic, such as schools, hospitals, libraries, and care facilities
- `recreation_green`: parks, sports, leisure, and green-related uses

This separation keeps the POI features interpretable and lets us count multiple roles for the same point.


## Trees

We first tested OSM trees, but coverage was too sparse and mostly represented street-tree records. We then switched to two Barcelona Open Data layers: street trees and park trees, which are much more complete at city scale.

Tree points were counted separately inside 10 m and 20 m buffers around each noise street segment, and then summed into total tree counts per buffer distance.



# Momepy

Momepy was used for calculating width. It is not the carrage width, but the building to building distance. 
Openess was also calculated. 

# Networkx

### Betwenness centrality (edge + node)

It measures how often a street (edge) or intersection (node) lies on the shortest paths between all othe rplaces in the network. A street with high betweenness centrality carries a lot of potnetial flow. It is often a major traffic corridor.

### Closeness centrality (node)

It measures how close a node is to all other nodes in the network (in terms of travel distance).
High closeness = central, well‑connected area.

### Straightness centrality (node)

It measures hw direct routes are from a node to all others.
- If the network is grid‑like and straight, straightness is high.
- If the network is curvy, fragmented, medieval, straightness is low.

# Dataset merge and subsample

## Merge notebook

The merge notebook collects all processed feature tables and combines them into one machine-learning dataset.

- Base table: OSM roads with the street_id key and noise targets.
- Merge key: all feature tables are normalized to street_id (for example, TRAM is renamed when needed).
- Merge strategy: iterative left joins so every base street segment is preserved.
- Cleanup: duplicate columns are removed, missing values are filled with 0, and noise ranges are converted to numeric lower-bound values.
- Output: a single merged CSV used for model training.

## Subsample notebook

The subsample notebook creates a half-size version of the final ML table while keeping the overall noise distribution balanced.

1. It starts from the merged dataset and checks that the three targets exist: noise_day, noise_evening, noise_night.
2. It builds one row-level noise_score as the mean of the three targets, so sampling is based on overall exposure instead of three separate axes.
3. It creates quantile buckets from noise_score using qcut (target: 8 buckets). Quantile buckets keep group sizes similar and avoid over-representing common ranges.
4. It samples 50% of rows inside each bucket with a fixed random seed, so the result is reproducible and balanced across quieter and louder streets.
5. It removes temporary helper columns (noise_score and bucket label), keeps row order stable (sorted by fid when present), and exports the halved CSV.

This gives a smaller dataset with comparable noise-profile coverage, which is useful for faster experiments without strongly distorting the target distribution.

# TODO

Calculate closeness centrality, betweeness centrality ndoes, straightness centrality
Consider adding distance from major road and distance to city center.
Consider adding building height to momepy for calculating canyon height and h/w ratio.