import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import altair as alt

script_dir = Path(__file__).parent
clean_call = script_dir / '../data/derived-data/call_clean.csv'
call_clean = pd.read_csv(clean_call)

call_type_col = "Final Call Type"  

dist_df = (
    call_clean
    .dropna(subset=[call_type_col])
    .groupby(call_type_col, as_index=False)
    .size()
    .rename(columns={"size": "count"})
    .sort_values("count", ascending=False)
)

dist_df["percent"] = dist_df["count"] / dist_df["count"].sum()

top_n = 15
dist_plot = dist_df.head(top_n)

chart_type = (
    alt.Chart(dist_plot)
    .mark_bar()
    .encode(
        x=alt.X("count:Q", title="Number of Calls"),
        y=alt.Y(f"{call_type_col}:N", sort="-x", title="Call Type"),
        tooltip=[
            call_type_col,
            "count",
            alt.Tooltip("percent:Q", format=".2%")
        ]
    ).properties(
        width=800,
        height=500,
        title="Composition by Call Type - Distribution of Emergency Calls"
    )
)

output_path = script_dir / '../data/derived-data/'
chart_type.save(output_path / "bar_call_type.png", scale_factor=2)