import geopandas as gpd
import pandas as pd
import os
from shapely import wkt
from pathlib import Path

script_dir = Path(__file__).parent
raw_call = script_dir / '../data/raw-data/Call_Data_20260227.csv'

call = pd.read_csv(raw_call)
call.head(5)
call.shape

### Quick Sanity Check
dup_mask = call['CAD Event Number'].duplicated(keep=False)
dup_events = call.loc[dup_mask].sort_values('CAD Event Number')
dup_events.head(10)

### If CAD Event Response Category is 'SPD/CARE Co-Response', 
### Call Sign Dsipatch ID will be recorded twice or third time by different programs

call['is_care'] = (
    call['Call Sign Dispatch ID']
    .str.contains('CARE', case=False, na=False)
)

call_sorted = (call.sort_values(
    by=['CAD Event Number', 'is_care'],
    ascending=[True, False]  
    )
)

call_care = call_sorted.drop_duplicates(
    subset='CAD Event Number',
    keep='first'
)

assert call_care['CAD Event Number'].duplicated().sum() == 0, 'There is duplicated CAD number'

### Filter call type
initial_call_type = call_care['Initial Call Type'].unique()
final_call_type = call_care['Final Call Type'].unique()

call_clean = call_care[
    ~(
        call['Initial Call Type'].str.contains('TEST') |
        call['Final Call Type'].str.contains('TEST') 
    )
].copy()

# Parse datetime + add time features (for heatmap)
TIME_COL = 'CAD Event Original Time Queued'
call_clean[TIME_COL] = pd.to_datetime(call_clean[TIME_COL], errors="coerce")
call_clean = call_clean.dropna(subset=[TIME_COL]).copy()
call_clean = call_clean.rename(columns={TIME_COL: "datetime"})
call_clean["hour"] = call_clean["datetime"].dt.hour
call_clean["dayofweek"] = call_clean["datetime"].dt.day_name()
call_clean["date"] = call_clean["datetime"].dt.date

# Clean lat/lon + build GeoDataFrame (for maps)
redacted_lat = (call["Dispatch Latitude"] == "REDACTED").sum()
redacted_lon = (call["Dispatch Longitude"] == "REDACTED").sum()
print("Latitude redacted count:", redacted_lat)
print("Longitude redacted count:", redacted_lon)

call_clean.shape