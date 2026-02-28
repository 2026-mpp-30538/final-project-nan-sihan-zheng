import geopandas as gpd
import pandas as pd
import os
from shapely import wkt

os.getcwd()
PATH_RAW = '/Users/zackzzz/python_II_ps/final-project-nan-sihan-zheng/data/raw-data'

call = pd.read_csv(os.path.join(PATH_RAW,'call.csv'))
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

call_filter = call_care[
    ~(
        call['Initial Call Type'].str.contains('TEST') |
        call['Final Call Type'].str.contains('TEST') 
    )
].copy()

call_filter.shape