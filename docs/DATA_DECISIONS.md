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

# Open Street Map

Open street map data were downloaded from Internet. In the data processing phase, they are either loaded from file or with the command: ox.features_from_place("Barcelona, Spain", tags={"some_key": "some_value"}).

The geometry is always projected to EPSG:25831 - ETRS89 / UTM zone 31N for being compared with noise dataset.

## Roads

### Road category

We assign to the noise vector the class of the closest osm road as road category.
We preprocessed the road dataset to exclude the follwoing categoreis:
- "path", "track" and "service", as they do not overlap any noise segment. 
- "pedestrian", "footway" and "cycleway", as they are mainly parallel to major roads. 
- "steps" and links as non relevant.

### Maxspeed and width

Since most of these are NaN for OSM roads, we do not consdier the features. 
Another reason to exclude them is that they would have high correlation with road category (class). 
