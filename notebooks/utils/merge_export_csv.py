#!/usr/bin/env python
# coding: utf-8

# # Merge and Export Machine Learning Dataset
# This notebook gathers all the pre-calculated features from the other scripts (OSM POIs, Land Use percentages, and Terrain Slope) and merges them into one single comprehensive `.csv` table that will be fed to the Machine Learning models.

# ## Note: Data Requirements
# Currently, the other notebooks do not save their resulting pandas DataFrames to disk. For this notebook to effectively gather and merge them, we must first run the feature generation loops directly here, OR you must add an export block to the other notebooks (e.g. `dataset.to_csv("my_features.csv", index=False)`).
# 
# In this script, we'll write the logic that assumes those feature dataframes have either been saved to disk or can be reconstructed.

# In[1]:


import pandas as pd
import os

print("Libraries imported.")


# ### Load the datasets
# **Assumption:** The datasets have been saved to a `../../data/processed/` folder from the previous notebooks. If not, go back to `UsosSol_percentages.ipynb`, `OSM_points.ipynb` and `Street_Slope copy.ipynb` and add `dataset.to_csv('../../data/processed/[name].csv', index=False)` at the very bottom of each.

# In[ ]:


# Define file paths (UNCOMMENT AND ADJUST ONCE YOU HAVE EXPORTED THE DATA)

path_landuse = "../../data/processed/landuse_features.csv"
path_osm_landuse = "../../data/processed/osm_landuse_features.csv"
path_osm = "../../data/processed/osm_features.csv"
path_slope = "../../data/processed/slope_features.csv"
path_bldg_height = "../../data/processed/osm_building_heights.csv"
path_lidar_height = "../../data/processed/lidar_building_heights.csv"
path_catastral_floors = "../../data/processed/catastral_building_floors.csv"

df_landuse = pd.read_csv(path_landuse)
df_osm_landuse = pd.read_csv(path_osm_landuse)
df_osm = pd.read_csv(path_osm)
df_slope = pd.read_csv(path_slope)
df_bldg_height = pd.read_csv(path_bldg_height)
df_lidar_height = pd.read_csv(path_lidar_height)
df_catastral_floors = pd.read_csv(path_catastral_floors)


print("Data loaded successfully.")
print("Data loaded successfully.")


# ### Merge Datasets
# We merge on the overarching street unique id (`TRAM`). Because we expect every street segment to be present in our base `noise` predictions, we will do a `LEFT` merge starting with the dataframe that contains the dependent noise variables.

# In[ ]:


# Start with a base dataframe that has our targets (Assume df_landuse has the targets as constructed previously)
ml_dataset = df_landuse.copy()

# Ensure no duplicate target columns from other dataframes
cols_to_drop = ['noise_day', 'noise_evening', 'noise_night']

# Merge OSM Land Use
_df_osm_landuse_clean = df_osm_landuse.drop(columns=[c for c in cols_to_drop if c in df_osm_landuse.columns])
if 'fid' not in _df_osm_landuse_clean.columns and 'fid' in ml_dataset.columns:
    _df_osm_landuse_clean['street_id'] = _df_osm_landuse_clean['street_id'].astype(str)
    ml_dataset = ml_dataset.merge(_df_osm_landuse_clean, on=['street_id'], how='left')
else:
    _df_osm_landuse_clean['street_id'] = _df_osm_landuse_clean['street_id'].astype(str)
    ml_dataset = ml_dataset.merge(_df_osm_landuse_clean, on=['fid', 'street_id'], how='left')

# Merge OSM points
_df_osm_clean = df_osm.drop(columns=[c for c in cols_to_drop if c in df_osm.columns])
ml_dataset['street_id'] = ml_dataset['street_id'].astype(str)
if 'fid' not in _df_osm_clean.columns and 'fid' in ml_dataset.columns:
    _df_osm_clean['street_id'] = _df_osm_clean['street_id'].astype(str)
    ml_dataset = ml_dataset.merge(_df_osm_clean, on=['street_id'], how='left')
else:
    _df_osm_clean['street_id'] = _df_osm_clean['street_id'].astype(str)
    ml_dataset = ml_dataset.merge(_df_osm_clean, on=['fid', 'street_id'], how='left')

# Merge Slopes
_df_slope_clean = df_slope.drop(columns=[c for c in cols_to_drop if c in df_slope.columns])
if 'fid' not in _df_slope_clean.columns and 'fid' in ml_dataset.columns:
    _df_slope_clean['street_id'] = _df_slope_clean['street_id'].astype(str)
    ml_dataset = ml_dataset.merge(_df_slope_clean, on=['street_id'], how='left')
else:
    _df_slope_clean['street_id'] = _df_slope_clean['street_id'].astype(str)
    ml_dataset = ml_dataset.merge(_df_slope_clean, on=['fid', 'street_id'], how='left')

# Merge Building Heights
_df_bldg_height = df_bldg_height.drop(columns=[c for c in cols_to_drop if c in df_bldg_height.columns])
if 'fid' not in _df_bldg_height.columns and 'fid' in ml_dataset.columns:
    _df_bldg_height['street_id'] = _df_bldg_height['street_id'].astype(str)
    ml_dataset = ml_dataset.merge(_df_bldg_height, on=['street_id'], how='left')
else:
    _df_bldg_height['street_id'] = _df_bldg_height['street_id'].astype(str)
    ml_dataset = ml_dataset.merge(_df_bldg_height, on=['fid', 'street_id'], how='left')

# Merge LiDAR Building Heights
_df_lidar_height = df_lidar_height.drop(columns=[c for c in cols_to_drop if c in df_lidar_height.columns])
if 'fid' not in _df_lidar_height.columns and 'fid' in ml_dataset.columns:
    _df_lidar_height['street_id'] = _df_lidar_height['street_id'].astype(str)
    ml_dataset = ml_dataset.merge(_df_lidar_height, on=['street_id'], how='left')
else:
    _df_lidar_height['street_id'] = _df_lidar_height['street_id'].astype(str)
    ml_dataset = ml_dataset.merge(_df_lidar_height, on=['fid', 'street_id'], how='left')

# Merge Catastral Building Floors
_df_catastral_floors = df_catastral_floors.drop(columns=[c for c in cols_to_drop if c in df_catastral_floors.columns])
if 'fid' not in _df_catastral_floors.columns and 'fid' in ml_dataset.columns:
    _df_catastral_floors['street_id'] = _df_catastral_floors['street_id'].astype(str)
    ml_dataset = ml_dataset.merge(_df_catastral_floors, on=['street_id'], how='left')
else:
    _df_catastral_floors['street_id'] = _df_catastral_floors['street_id'].astype(str)
    ml_dataset = ml_dataset.merge(_df_catastral_floors, on=['fid', 'street_id'], how='left')

# Fill any new NAs generated across the merges (caused by lack of points/features around specific street ids)
ml_dataset = ml_dataset.fillna(0)

print(ml_dataset.head(5))
print(f"Final dataset shape: {ml_dataset.shape}")


# ### Export to CSV
# Finally, we dump out the master table into a standard format readable by `scikit-learn` in the next phase!

# In[4]:


# UNCOMMENT TO EXPORT

output_dir = "../../data/machine_learning/"
os.makedirs(output_dir, exist_ok=True)

final_path = os.path.join(output_dir, "bcn_noise_ml_dataset.csv")
ml_dataset.to_csv(final_path, index=False)

print(f"Dataset successfully exported to: {final_path}")

