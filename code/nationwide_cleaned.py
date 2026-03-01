import pandas as pd

# Load data
POINTS_DATA_PATH = "raw data/Map-Data-as-of-Sep16-25.csv"  

df = pd.read_csv(POINTS_DATA_PATH)

# Drop missing values in "Call Category"
df["Call Categories"] = df["Call Categories"].dropna()

# Split "Call Category" into lists
df["Call Categories"] = df["Call Categories"].str.split(",")

# Explode to long format DataFrame
df_long = df.explode("Call Categories")

# Strip whitespace from "Call Category"
df_long["Call Categories"] = df_long["Call Categories"].str.strip()

# Summarize
category_counts = (
    df_long.groupby("Call Categories")
           .size()
           .reset_index(name="Number of Programs")
           .sort_values("Number of Programs", ascending=False)
)

print(category_counts)

df_long.to_csv("nationwide_long.csv", index=False)
