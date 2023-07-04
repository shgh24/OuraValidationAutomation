import pandas as pd
import numpy as np
import os
import glob as glob


HPB_raw_path = '/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/HPB/CSC_sleep_intervals.xlsx'

# reading the HPB file
data = pd.read_excel(HPB_raw_path, sheet_name="N1")
stages = pd.unique(data["sleepstagecategory"])
data["stage"] = data["sleepstagecategory"].map({
    'LIGHT':
    1,
    'DEEP':
    3,
    'SAWAKE':
    0,
    'REM':
    5,
    'RESTLESS':
    7,
    'ASLEEP':
    1,
    'CAWAKE': 0})


df_clean = pd.DataFrame(columns=["name",
                                 "timestamp",
                                 "predicted"])

IDS = pd.unique(data["NUSID"])

for id in IDS:

    df_temp = data[(data["NUSID"] == id)]
    result = df_temp.loc[df_temp.index.repeat(df_temp.intervaldurationmins*2)]

    # df_clean["name"] =

    print('done')
