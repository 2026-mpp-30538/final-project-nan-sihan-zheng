import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from pathlib import Path

script_dir = Path(__file__).parent
clean_call = script_dir / '../data/derived-data/call_clean.csv'
raw_neigh = script_dir / '../data/raw-data/Neighborhood_geo/Neighborhood_Map_Atlas_Districts.shp'

call_clean = pd.read_csv(clean_call)
call_group = (call_clean
              .groupby('neighborhood')
              .size()
              .reset_index(name='n_calls')
              )

neigh_gdf = gpd.read_file(raw_neigh)

plot_df = neigh_gdf.merge(call_group,how='left',
                          left_on='L_HOOD',
                          right_on='neighborhood').fillna(0)


fig, ax = plt.subplots(figsize=(8, 6))

plot_df.plot(
    column='n_calls',
    cmap='Reds',
    linewidth=0.5,
    edgecolor='gray',
    legend=True,
    ax=ax
)

ax.set_title("Number of Calls by Neighborhood", fontsize=14)
ax.axis('off')

plt.savefig(
    script_dir / '../data/derived-data/calls_Seattle.png',
    dpi=300,
    bbox_inches="tight"
)

plt.show()

