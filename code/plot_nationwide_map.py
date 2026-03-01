import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from shapely.affinity import scale, translate

BASEMAP_GEOJSON_PATH = "raw data/us-states.json"
POINTS_DATA_PATH     = "raw data/Map-Data-as-of-Sep16-25.csv"
OUTPUT_PNG_PATH      = "national_programs_map.png"

LAT_COL   = "Latitude"
LON_COL   = "Longitude"
CALL_COL  = "Call Volume"

CALL_THRESHOLD = 3000

TITLE = "Nationwide Community Responder Programs"

# align all data to a common CRS
FORCE_BASEMAP_CRS_IF_MISSING = "EPSG:4326"
POINTS_INPUT_CRS = "EPSG:4326"
PLOT_CRS = "EPSG:3857"

# load basemap
basemap = gpd.read_file(BASEMAP_GEOJSON_PATH)
if basemap.crs is None:
    basemap = basemap.set_crs(FORCE_BASEMAP_CRS_IF_MISSING)

# load points data
df = pd.read_csv(POINTS_DATA_PATH)

# Clean and convert to numeric, drop rows with invalid lat/lon data
df[LAT_COL] = pd.to_numeric(df[LAT_COL], errors="coerce")
df[LON_COL] = pd.to_numeric(df[LON_COL], errors="coerce")
df[CALL_COL] = pd.to_numeric(df[CALL_COL], errors="coerce")

df = df.dropna(subset=[LAT_COL, LON_COL]).copy()

# create GeoDataFrame
points = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(df[LON_COL], df[LAT_COL]),
    crs="EPSG:4326"
)

# project points to match basemap CRS
points_proj = points.to_crs(basemap.crs)

# split into high/low call volume
high = points_proj[points_proj[CALL_COL] > CALL_THRESHOLD].copy()
low  = points_proj[points_proj[CALL_COL] <= CALL_THRESHOLD].copy()
unknown = df[df[CALL_COL].isna()].copy()  # not includeed in plot

# exclude Hawaii and Puerto Rico
basemap = basemap[~basemap["name"].isin(["Hawaii", "Puerto Rico"])].copy()

# project BOTH basemap and points to plotting CRS first
basemap_3857 = basemap.to_crs(PLOT_CRS)
points_3857 = points.to_crs(PLOT_CRS)

# Separate Alaska polygon
alaska_poly = basemap_3857[basemap_3857["name"] == "Alaska"].copy()
lower48_poly = basemap_3857[basemap_3857["name"] != "Alaska"].copy()

# Separate Alaska points
points_4326 = points.to_crs("EPSG:4326")
alaska_idx = points_4326[
    (points_4326.geometry.x < -130) & (points_4326.geometry.y > 50)
].index

alaska_points = points_3857.loc[alaska_idx].copy()
lower48_points = points_3857.drop(alaska_idx).copy()

# scale down Alaska polygon + points
SCALE_FACTOR = 0.35

# use the SAME origin for scaling polygon + points (polygon centroid)
ak_origin = alaska_poly.geometry.unary_union.centroid

alaska_poly["geometry"] = alaska_poly["geometry"].apply(
    lambda geom: scale(geom, xfact=SCALE_FACTOR, yfact=SCALE_FACTOR, origin=ak_origin)
)
alaska_points["geometry"] = alaska_points["geometry"].apply(
    lambda geom: scale(geom, xfact=SCALE_FACTOR, yfact=SCALE_FACTOR, origin=ak_origin)
)

# translate Alaska to lower-left of lower48
minx, miny, maxx, maxy = lower48_poly.total_bounds
ak_minx, ak_miny, ak_maxx, ak_maxy = alaska_poly.total_bounds

x_offset = minx - ak_minx - 6e5
y_offset = miny - ak_miny - 6e5

alaska_poly["geometry"] = alaska_poly["geometry"].apply(
    lambda geom: translate(geom, xoff=x_offset, yoff=y_offset)
)
alaska_points["geometry"] = alaska_points["geometry"].apply(
    lambda geom: translate(geom, xoff=x_offset, yoff=y_offset)
)

# combine back
basemap_final = gpd.GeoDataFrame(
    pd.concat([lower48_poly, alaska_poly], ignore_index=True),
    crs=PLOT_CRS
)

points_final = gpd.GeoDataFrame(
    pd.concat([lower48_points, alaska_points], ignore_index=True),
    crs=PLOT_CRS
)

# now split by call volume on points_final
high_final = points_final[points_final[CALL_COL] > CALL_THRESHOLD].copy()
low_final  = points_final[(points_final[CALL_COL].notna()) & (points_final[CALL_COL] <= CALL_THRESHOLD)].copy()
unknown_final = points_final[points_final[CALL_COL].isna()].copy()

# plotting
fig, ax = plt.subplots(figsize=(14, 8))

basemap_final.plot(ax=ax, color="#1f3a93", edgecolor="white", linewidth=0.8)

low_final.plot(
    ax=ax,
    marker="o",
    facecolor="white",
    edgecolor="black",
    linewidth=0.8,
    markersize=60,
    alpha=0.95
)

high_final.plot(
    ax=ax,
    marker="D",
    facecolor="#f1c40f",
    edgecolor="black",
    linewidth=0.8,
    markersize=70,
    alpha=0.95
)

ax.set_title(TITLE, fontsize=16, pad=14)
ax.set_axis_off()

legend_elements = [
    Line2D([0], [0], marker='D', color='w',
           label=f"More than {CALL_THRESHOLD:,} calls/year",
           markerfacecolor="#f1c40f", markeredgecolor="black", markersize=10),
    Line2D([0], [0], marker='o', color='w',
           label=f"{CALL_THRESHOLD:,} calls/year or less",
           markerfacecolor="white", markeredgecolor="black", markersize=10),
]
ax.legend(handles=legend_elements, loc="upper right", frameon=True)

total_programs = len(points_final)
ax.text(
    0.5, 0.02, f"{total_programs} Programs",
    transform=ax.transAxes, ha="center", va="bottom",
    fontsize=14, color="black"
)

minx, miny, maxx, maxy = lower48_poly.total_bounds
ax.set_xlim(minx - 5e5, maxx + 5e5)
ax.set_ylim(miny - 5e5, maxy + 5e5)

plt.tight_layout()
plt.savefig(OUTPUT_PNG_PATH, dpi=300, bbox_inches="tight")
print(f"Saved map to: {OUTPUT_PNG_PATH}")
plt.show()