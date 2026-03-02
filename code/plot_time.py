import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from pathlib import Path
import altair as alt

script_dir = Path(__file__).parent
clean_call = script_dir / '../data/derived-data/call_clean.csv'
call_clean = pd.read_csv(clean_call)

heatmap_df = (
    call_clean
    .groupby(["dayofweek", "hour"], as_index=False)
    .size()
    .rename(columns={"size": "call_count"})
)

weekday_order = [
    "Monday", "Tuesday", "Wednesday",
    "Thursday", "Friday", "Saturday", "Sunday"]

chart_time = (
    alt.Chart(heatmap_df)
    .mark_rect()
    .encode(
        x=alt.X("hour:O", title="Hour of Day", axis=alt.Axis(labelAngle=0)),
        y=alt.Y("dayofweek:O", sort=weekday_order, title="Day of Week"),
        color=alt.Color("call_count:Q", scale=alt.Scale(scheme="blues"), title="Number of Calls"),
        tooltip=["dayofweek", "hour", "call_count"]
    ).properties(
        width=600,
        height=300,
        title="Behavioral / CARE Calls by Day and Hour"
    )
)


output_path = script_dir / '../data/derived-data/'
chart_time.save(output_path / "heatmap_day_hour.png", scale_factor=2)