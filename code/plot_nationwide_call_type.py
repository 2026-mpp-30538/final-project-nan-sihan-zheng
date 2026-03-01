import pandas as pd
import altair as alt

# Load data
df = pd.read_csv("derived data/nationwide_long.csv")
CALL_CATEGORY_COL = "Call Categories"

# Aggregate counts
category_counts = (
    df.groupby(CALL_CATEGORY_COL)
      .size()
      .reset_index(name="Number of Programs")
      .sort_values("Number of Programs", ascending=False)
)

# Altair chart
chart = (
    alt.Chart(category_counts)
    .mark_bar()
    .encode(
        x=alt.X(
            "Number of Programs:Q",
            title="Number of Programs"
        ),
        y=alt.Y(
            f"{CALL_CATEGORY_COL}:N",
            sort="-x",
            title=None
        ),
        color=alt.Color(
               f"{CALL_CATEGORY_COL}:N",
               scale=alt.Scale(
                   domain=category_counts[CALL_CATEGORY_COL].tolist(),
                   range=["#2E4A9E", "#5B6B9A", "#7A7A70", "#A59659", "#C9AE45", "#F2C21A"]
               ),
               legend=None
        )
    )
    .properties(
        width=700,
        height=400,
        title="Call Categories"
    )
)

chart.save("national_call_categories.png", scale_factor=2)