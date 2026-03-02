import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from pathlib import Path
import matplotlib.patheffects as pe

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


fig, ax = plt.subplots(figsize=(9, 9))

plot_df.plot(
    column='n_calls',
    cmap='Reds',
    scheme='quantiles',
    k=5,
    linewidth=0.4,
    edgecolor='white',
    legend=True,
    legend_kwds={
        'title': "CARE Calls (Quantiles)",
        'fmt': "{:.0f}"
        },
    ax=ax
)

plot_df['label_point'] = plot_df.geometry.representative_point()
top_n = plot_df.nlargest(5, 'n_calls')

for _, row in top_n.iterrows():
    ax.text(
        row['label_point'].x,
        row['label_point'].y,
        f"{row['L_HOOD']}\n{int(row['n_calls'])}",
        ha='center',
        va='center',
        fontsize=6,
        color='white',
        weight='bold',
        path_effects=[
            pe.Stroke(linewidth=1, foreground='grey'),
            pe.Normal()]
    )

ax.set_title("Number of CARE Calls by Large Neighborhood in Seattle", fontsize=14)
ax.axis('off')

plt.savefig(
    script_dir / '../data/derived-data/calls_Seattle_enhanced.png',
    dpi=300,
    bbox_inches='tight'
)

plt.show()

plt.savefig(
    script_dir / '../data/derived-data/calls_Seattle.png',
    dpi=300,
    bbox_inches="tight"
)

plt.show()

