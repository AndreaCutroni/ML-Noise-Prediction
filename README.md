# ML-Noise-Prediction

## Environment Setup

The project uses a conda environment called **`data-encoding`** with all required geospatial dependencies installed from the `conda-forge` channel.

### 1. Create the environment

Navigate to the project folder in your terminal:

```bash
cd path/to/your/barcelona_project
```

Then create and install all packages at once using the `environment.yml` file:

```bash
conda env create -f environment.yml
```

### 2. Activate the environment

```bash
conda activate data-encoding
```

### 3. Select the kernel in VS Code

1. Open the `analysis.ipynb` notebook in VS Code
2. Click the kernel selector in the top-right corner
3. Select **data-encoding** from the list

---

## Dependencies

All packages are defined in `environment.yml` and installed via `conda-forge`:

| Package | Purpose |
|---|---|
| `geopandas` | Read, manipulate and save geospatial data |
| `osmnx` | Download traffic signals and POIs from OpenStreetMap |
| `jupyter` | Run the notebook |
| `ipykernel` | Connect the conda environment to VS Code |
| `folium` | Interactive map rendering |
| `mapclassify` | Classification schemes for choropleth maps |
| `tqdm` | Display progress bars for loops and data processing |
| `rasterio` | Read and manipulate geospatial raster data |