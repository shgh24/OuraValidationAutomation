"""
This Python script performs a data cleaning  of the scored sleep staging data forOura validation 3 study. The script reads in the staging data from a CSV file, cleans and prepare the raw data for De Zambotti package.

Usage:
    python RAWdata_preparation_DeZambotti.py <NUS*.csv>

Dependencies:
    - pandas
    - numpy
    - os 
    -glob
"""


import pandas as pd
import glob
import os as os
import numpy as np

# Basically 3010n1, 3020n2 and 3030n1 psg terminated before lights on.
# For 3010 and 3020 subject was already awake so we can append wake to end of psg record.
# For 3030 subject was still sleeping so if we are doing any wake time estimation detection, nd to skip this.


staging_file_path = "/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/Sleep_Staging"
Saving_file_path = "/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/analysis/DeZambotti/FB/Data/DeviceOnly"
# FB_data="/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/Sleep_Staging/Fitbit/NUS3001_N1.csv"


nights = ["N1"]

for Night in nights:

    FB_data = glob.glob(os.path.join(
        staging_file_path, "Fitbit", "DeviceOnly", "NUS*.csv"))
    combined_data_AllDays = pd.DataFrame()
    for FB_Scores in FB_data:
        # Extract the subject number and night from the file name
        subject1, night = os.path.splitext(os.path.basename(FB_Scores))[
            0].split("_")[0:2]

        df_FB = pd.read_csv(FB_Scores)

        combined_data = pd.DataFrame(
            data=[subject1]*len(df_FB), columns=['subject'])

        combined_data['epoch'] = np.arange(len(df_FB))+1
        combined_data['reference'] = df_FB
        combined_data['device'] = df_FB

        combined_data_AllDays = pd.concat(
            [combined_data_AllDays, combined_data], ignore_index=True)

    combined_data_AllDays.to_csv(os.path.join(Saving_file_path,
                                              f"combined_data_{Night}.csv"), index=False)
