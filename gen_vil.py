# Generate the 7 Viladecans notebooks from the Milan templates.
import copy
import json
import os

MIL_DIR = os.path.join('deployment', 'Milan', 'notebooks')
VIL_DIR = os.path.join('deployment', 'Viladecans', 'notebooks')
os.makedirs(VIL_DIR, exist_ok=True)

# Ordered, case-sensitive replacements (most specific first)
REPLACEMENTS = [
    ('MIL_noise_streets.gpkg', 'VIL_noise_streets.gpkg'),
    ('mil_osm_landuse.gpkg', 'vil_osm_landuse.gpkg'),
    ('mil_noise_class_ml_dataset.csv', 'vil_noise_class_ml_dataset.csv'),
    ('mil_noise_class_ml_subsample.csv', 'vil_noise_class_ml_subsample.csv'),
    ('milan.graphml', 'viladecans.graphml'),
    ('Milan, Italy', 'Viladecans, Spain'),
    ('EPSG:32632', 'EPSG:25831'),
    ('32632', '25831'),
    ('deployment/Milan/', 'deployment/Viladecans/'),
    ('Milan', 'Viladecans'),
    ('milan', 'viladecans'),
    ('MIL_', 'VIL_'),
    ('01_MIL', '01_VIL'),
    ('02_MIL', '02_VIL'),
]


def transform_text(text):
    for old, new in REPLACEMENTS:
        text = text.replace(old, new)
    return text


def load_nb(name):
    with open(os.path.join(MIL_DIR, name), encoding='utf-8') as f:
        return json.load(f)


def strip_and_replace(nb):
    for cell in nb['cells']:
        cell['source'] = [transform_text(line) for line in cell['source']]
        if cell['cell_type'] == 'code':
            cell['outputs'] = []
            cell['execution_count'] = None
        cell.pop('id', None)
    return nb


def set_cell(nb, idx, cell_type, source):
    """Replace cell idx with new source (applied AFTER strip_and_replace)."""
    cell = {'cell_type': cell_type, 'metadata': {}, 'source': source.splitlines(keepends=True)}
    if cell_type == 'code':
        cell['outputs'] = []
        cell['execution_count'] = None
    nb['cells'][idx] = cell


def save_nb(nb, name):
    path = os.path.join(VIL_DIR, name)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)
    # validate round-trip
    with open(path, encoding='utf-8') as f:
        json.load(f)
    print('Wrote', path, f"({len(nb['cells'])} cells)")


# ---------------------------------------------------------------------------
# 1. VIL_Noise.ipynb — built fresh (metadata copied from MIL_Noise)
# ---------------------------------------------------------------------------
mil_noise = load_nb('MIL_Noise.ipynb')
nb = {'cells': [], 'metadata': mil_noise['metadata'],
      'nbformat': mil_noise['nbformat'], 'nbformat_minor': mil_noise['nbformat_minor']}


def add(cell_type, source):
    cell = {'cell_type': cell_type, 'metadata': {}, 'source': source.splitlines(keepends=True)}
    if cell_type == 'code':
        cell['outputs'] = []
        cell['execution_count'] = None
    nb['cells'].append(cell)


add('markdown', """# Viladecans - Contaminació Acústica (Strategic Noise Map)

Downloads the "Contaminació Acústica (Dades)" dataset from the Viladecans open data
platform (Portal Viladecans 360, ArcGIS Online hosted layer). The data comes from the
strategic noise map of the Baix Llobregat II agglomeration (Gavà, Viladecans and
Sant Boi de Llobregat), representing the acoustic situation in 2017 (valid for the
2017-2022 period) per street segment and per period:

| Field | Meaning |
|---|---|
| TOTDIA | Total noise level, day period (7h-21h), dB(A) |
| TOTVES | Total noise level, evening period (21h-23h), dB(A) |
| TOTNIT | Total noise level, night period (23h-7h), dB(A) |
| TOTDEN | Total noise level, Lden index (24h), dB(A) |
| TVL* / TFL* / TAL* / INL* / OCL* | Per-source levels: road / rail / air / industry / leisure |
| VLDIA / VLVES / VLNIT | Legal limit values (acoustic capacity map) |
| POBTOT | Population assigned to the segment |

The notebook enriches the segments with clean `db_day` / `db_evening` / `db_night`
columns (from the TOT* totals), exports the enriched GeoJSON to
`../layers/viladecans_noise_enriched.geojson`, and explores the data.

Note: a 2022-2027 strategic noise map exists but is currently published only as a
web viewer; this dataset is the latest downloadable per-segment data.""")

add('code', """import os
import time
import requests
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt""")

add('markdown', '## Task 1 - Fetch the data (paginated ArcGIS REST query)')

add('code', """URL = ('https://services1.arcgis.com/ZP1Iw2MU5AMTAddh/arcgis/rest/services/'
       'Contaminaci%C3%B3_Ac%C3%BAstica_(Dades)/FeatureServer/0/query')
PAGE_SIZE = 1000

_layers_dir = os.path.join(os.path.dirname(os.path.abspath(os.getcwd())), 'layers')
ENRICHED_PATH = os.path.join(_layers_dir, 'viladecans_noise_enriched.geojson')

if os.path.exists(ENRICHED_PATH):
    print('Enriched GeoJSON already exists - loading from cache:')
    print(' ', ENRICHED_PATH)
    acoustic = gpd.read_file(ENRICHED_PATH)
else:
    all_features = []
    offset = 0
    while True:
        params = {
            'where': '1=1',
            'outFields': '*',
            'f': 'geojson',
            'resultOffset': offset,
            'resultRecordCount': PAGE_SIZE,
        }
        for attempt in range(3):
            try:
                r = requests.get(URL, params=params, timeout=120)
                r.raise_for_status()
                data = r.json()
                break
            except Exception as e:
                print(f'  attempt {attempt + 1} failed ({e}), retrying in 5 s...')
                time.sleep(5)
        else:
            raise RuntimeError('Failed to fetch page after 3 attempts')

        feats = data.get('features', [])
        if not feats:
            break
        all_features.extend(feats)
        print(f'Fetched {len(feats):5d} features (total {len(all_features)})')
        offset += len(feats)

    print(f'Total features downloaded: {len(all_features)}')
    acoustic = gpd.GeoDataFrame.from_features(all_features, crs='EPSG:4326')

print('CRS:', acoustic.crs)
print('Shape:', acoustic.shape)
print('Columns:', acoustic.columns.tolist())""")

add('code', """print(acoustic[['TOTDIA', 'TOTVES', 'TOTNIT']].describe())
acoustic.head()""")

add('markdown', """## Task 2 - Enrich with clean noise columns

The ML pipeline uses one dB value per period. We take the total noise levels
(`TOT*`) — for most segments identical to the road-traffic levels (`TVL*`), since
rail / air / industry contributions are zero on the local street network.""")

add('code', """noise_value_cols = ['TOTDIA', 'TOTVES', 'TOTNIT', 'TOTDEN',
                    'TVLDIA', 'TVLVES', 'TVLNIT',
                    'VLDIA', 'VLVES', 'VLNIT', 'POBTOT']
for c in noise_value_cols:
    acoustic[c] = pd.to_numeric(acoustic[c], errors='coerce')

acoustic['db_day'] = acoustic['TOTDIA']
acoustic['db_evening'] = acoustic['TOTVES']
acoustic['db_night'] = acoustic['TOTNIT']

assert acoustic['db_day'].notna().all(), 'Missing day noise values found'
assert acoustic['db_evening'].notna().all(), 'Missing evening noise values found'
assert acoustic['db_night'].notna().all(), 'Missing night noise values found'

acoustic[['IDTRAM', 'db_day', 'db_evening', 'db_night']].head(10)""")

add('markdown', '## Task 3 - Export the enriched GeoJSON')

add('code', """if not os.path.exists(ENRICHED_PATH):
    acoustic.to_file(ENRICHED_PATH, driver='GeoJSON')
    print('Exported:', ENRICHED_PATH)
else:
    print('Already on disk:', ENRICHED_PATH)""")

add('markdown', '## Explore - reproject to metric CRS (EPSG:25831) for mapping')

add('code', """acoustic_m = acoustic.to_crs('EPSG:25831')
print('Reprojected CRS:', acoustic_m.crs)
total_len = acoustic_m.geometry.length.sum() / 1000
print(f'Total mapped street length: {total_len:.1f} km')""")

add('markdown', '## Noise maps per period')

add('code', """fig, axes = plt.subplots(1, 3, figsize=(24, 9))
vmin = acoustic_m[['db_day', 'db_evening', 'db_night']].min().min()
vmax = acoustic_m[['db_day', 'db_evening', 'db_night']].max().max()
for ax, col, title in zip(axes,
                          ['db_day', 'db_evening', 'db_night'],
                          ['Day (7h-21h)', 'Evening (21h-23h)', 'Night (23h-7h)']):
    acoustic_m.plot(column=col, cmap='coolwarm', linewidth=1.2, legend=True,
                    vmin=vmin, vmax=vmax, ax=ax)
    ax.set_title(f'Total noise - {title} dB(A)')
    ax.set_axis_off()
plt.tight_layout()
plt.show()""")

add('markdown', '## Noise level distribution per period')

add('code', """fig, ax = plt.subplots(figsize=(12, 6))
for col, color in zip(['db_day', 'db_evening', 'db_night'],
                      ['tab:red', 'tab:orange', 'tab:blue']):
    acoustic_m[col].plot(kind='hist', bins=range(25, 85, 2), alpha=0.45,
                         label=col, color=color, ax=ax)
ax.set_xlabel('dB(A)')
ax.set_title('Noise level distribution per period')
ax.legend()
plt.show()""")

add('markdown', '## Summary statistics')

add('code', """w = acoustic_m.geometry.length
for col in ['db_day', 'db_evening', 'db_night']:
    print(f'{col}: mean {acoustic_m[col].mean():.1f} dB(A), '
          f'length-weighted mean {(acoustic_m[col] * w).sum() / w.sum():.1f} dB(A), '
          f'min {acoustic_m[col].min():.0f}, max {acoustic_m[col].max():.0f}')
print(f"\\nTotal assigned population (POBTOT): {int(acoustic_m['POBTOT'].sum())}")
print('Population on segments with db_day >= 65: '
      f"{int(acoustic_m.loc[acoustic_m['db_day'] >= 65, 'POBTOT'].sum())}")""")

save_nb(nb, 'VIL_Noise.ipynb')

# ---------------------------------------------------------------------------
# 2. VIL_OSM_roads_noise_class.ipynb — Milan template + patched noise cells
# ---------------------------------------------------------------------------
nb = strip_and_replace(load_nb('MIL_OSM_roads_noise_class.ipynb'))

set_cell(nb, 0, 'markdown', """# OSM roads — Viladecans

Loads the enriched strategic-noise-map segments (real modeled dB values per street
axis, day/evening/night), downloads the OSM drive network for Viladecans, assigns
each OSM street segment the noise values of the nearest noise-map segment (via the
segment midpoint), classifies the dB values into the 5 noise classes used by the ML
pipeline, computes distance-to-road-category features and exports
`../layers/VIL_noise_streets.gpkg` and `data/osm_roads_noise_class.csv`.""")

set_cell(nb, 2, 'markdown', '## Import and analyse the strategic noise map segments')

set_cell(nb, 3, 'code', """_layers_dir = os.path.join(os.path.dirname(os.path.abspath(os.getcwd())), 'layers')
noise_lines = gpd.read_file(os.path.join(_layers_dir, 'viladecans_noise_enriched.geojson'))
noise_lines = noise_lines.to_crs('EPSG:25831')
print('CRS:', noise_lines.crs)
print('Shape:', noise_lines.shape)
noise_lines[['db_day', 'db_evening', 'db_night']].describe()""")

set_cell(nb, 4, 'code', """ax = noise_lines.plot(column='db_day', cmap='coolwarm', linewidth=1.2,
                      legend=True, figsize=(12, 12))
ax.set_title('Viladecans strategic noise map — total noise, day period dB(A)')
ax.set_axis_off()
plt.show()""")

set_cell(nb, 18, 'markdown', """## Assign noise values to each street segment

Each OSM segment inherits `db_day`, `db_evening` and `db_night` from the nearest
noise-map street axis (matched via the OSM segment midpoint with `sjoin_nearest`).
The match distance is recorded — OSM centerlines and the municipal street axes
should nearly coincide, so most distances are expected below ~30 m.""")

set_cell(nb, 19, 'code', """# Midpoint -> nearest noise-map segment join
noise_roads = roads_filtered.reset_index(drop=True).copy()
midpoints = noise_roads[['segment_id']].copy()
midpoints = gpd.GeoDataFrame(midpoints,
                             geometry=noise_roads.geometry.interpolate(0.5, normalized=True),
                             crs=noise_roads.crs)

noise_cols = ['db_day', 'db_evening', 'db_night']
joined = gpd.sjoin_nearest(midpoints, noise_lines[noise_cols + ['geometry']],
                           how='left', distance_col='distance')
# Equidistant ties can match twice - keep the first match
joined = joined[~joined.index.duplicated(keep='first')]

for c in noise_cols:
    noise_roads[c] = joined[c]
noise_roads['distance'] = joined['distance']

noise_roads = noise_roads[noise_roads['db_day'].notna()].copy()
print(f'Segments with noise values: {len(noise_roads)} / {len(midpoints)}')
print('Match distance stats (m):')
print(noise_roads['distance'].describe())
print(f"Segments matched farther than 50 m: {(noise_roads['distance'] > 50).sum()}")
noise_roads[noise_cols + ['distance']].describe()""")

set_cell(nb, 22, 'code', """# The Viladecans strategic noise map provides all three periods directly:
# day (7-21h), evening (21-23h) and night (23-7h)
noise_roads['noise_day'] = noise_roads['db_day'].apply(classify_noise)
noise_roads['noise_evening'] = noise_roads['db_evening'].apply(classify_noise)
noise_roads['noise_night'] = noise_roads['db_night'].apply(classify_noise)

noise_roads.head()""")

set_cell(nb, 37, 'markdown', """## Export Viladecans noise streets layer

VIL_noise_streets.gpkg (layer `noise_streets`) in `deployment/Viladecans/layers/` — all
filtered street segments with segment_id, highway, name, length, dB values and noise
classes. This is the street layer consumed by the momepy / points / landuse notebooks.""")

set_cell(nb, 38, 'code', """export_cols = ['segment_id', 'highway', 'name', 'length',
               'db_day', 'db_evening', 'db_night',
               'noise_day', 'noise_evening', 'noise_night', 'distance', 'geometry']
export_gdf = noise_roads[[c for c in export_cols if c in noise_roads.columns]].copy()
export_gdf['name'] = export_gdf['name'].astype(str)
export_gdf['noise_day'] = export_gdf['noise_day'].astype(int)

out_gpkg = os.path.join(_layers_dir, 'VIL_noise_streets.gpkg')
export_gdf.to_file(out_gpkg, layer='noise_streets', driver='GPKG')
print('Exported:', out_gpkg)
print('Segments:', len(export_gdf))""")

save_nb(nb, 'VIL_OSM_roads_noise_class.ipynb')

# ---------------------------------------------------------------------------
# 3-5. momepy / points / landuse — pure text transforms
# ---------------------------------------------------------------------------
for src, dst in [('MIL_momepy.ipynb', 'VIL_momepy.ipynb'),
                 ('MIL_OSM_points.ipynb', 'VIL_OSM_points.ipynb'),
                 ('MIL_OSM_landuse.ipynb', 'VIL_OSM_landuse.ipynb')]:
    save_nb(strip_and_replace(load_nb(src)), dst)

# ---------------------------------------------------------------------------
# 6. 01_VIL_create_dataset_class.ipynb — transform + subsample tweak
# ---------------------------------------------------------------------------
nb = strip_and_replace(load_nb('01_MIL_create_dataset_class.ipynb'))
patched = 0
for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        src = ''.join(cell['source'])
        if src.startswith('sample_size = 5000'):
            src = src.replace('sample_size = 5000',
                              '# Viladecans is small: cap the subsample at the dataset size\n'
                              'sample_size = min(5000, len(ml_dataset))', 1)
            cell['source'] = src.splitlines(keepends=True)
            patched += 1
assert patched == 1, f'subsample cell patched {patched} times'
save_nb(nb, '01_VIL_create_dataset_class.ipynb')

# ---------------------------------------------------------------------------
# 7. 02_VIL_EDA_class.ipynb — pure text transform
# ---------------------------------------------------------------------------
save_nb(strip_and_replace(load_nb('02_MIL_EDA_class.ipynb')), '02_VIL_EDA_class.ipynb')

# ---------------------------------------------------------------------------
# Final scan for leftover Milan-specific tokens
# ---------------------------------------------------------------------------
print('\n--- leftover-token scan ---')
bad = ['Milan', 'milan', 'MIL_', '32632', 'Italy', 'CLASSE_ACU', 'db_diurno', 'db_notturno']
clean = True
for fname in sorted(os.listdir(VIL_DIR)):
    if not fname.endswith('.ipynb'):
        continue
    d = json.load(open(os.path.join(VIL_DIR, fname), encoding='utf-8'))
    for i, cell in enumerate(d['cells']):
        src = ''.join(cell['source'])
        for tok in bad:
            if tok in src:
                print(f'  {fname} cell {i}: contains "{tok}"')
                clean = False
print('CLEAN' if clean else 'TOKENS FOUND - fix needed')
