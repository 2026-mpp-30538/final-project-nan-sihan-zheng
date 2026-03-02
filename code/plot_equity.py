import geopandas as gpd
import matplotlib.pyplot as plt

shp_path = "raw data/Race_and_Social_Equity_Composite_Index_Current_68176633384735789/Racial_and_Social_Equity_Index_for_Countywide_2020_Census_Tracts.shp"
gdf = gpd.read_file(shp_path)

print("Columns:", list(gdf.columns))

score_col = "SOCIOECO_1"

# Check score column
gdf[score_col] = gdf[score_col].astype(float)
print("Score range:", gdf[score_col].min(), gdf[score_col].max())

# Projection
try:
    gdf = gdf.to_crs(epsg=3857)
except Exception as e:
    print("CRS transform skipped:", e)

# Plot
fig, ax = plt.subplots(figsize=(9, 9), dpi=200)

gdf.plot(
    column=score_col,
    ax=ax,
    legend=True,
    vmin=0, vmax=1,           
    linewidth=0.2,
    edgecolor="white",
    missing_kwds={"color": "lightgrey", "label": "Missing"}
)

ax.set_title("Seattle Socioeconomic Disadvantage Score (0–1)", fontsize=14)
ax.set_axis_off()

out_path = "Plot/seattle_ses_disadv_heatmap.png"
plt.tight_layout()
plt.savefig(out_path, bbox_inches="tight")
plt.show()

print("Saved to:", out_path)