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
import numpy as np
import glob
import os as os

# Basically 3010n1, 3020n2 and 3030n1 psg terminated before lights on.
# For 3010 and 3020 subject was already awake so we can append wake to end of psg record.
# For 3030 subject was still sleeping so if we are doing any wake time estimation detection, nd to skip this.
outliers = ['3010', '3020']
exlusion = ['3030']
count = 0


staging_file_path = "/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/Sleep_Staging"
Saving_file_path = "/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/analysis/DeZambotti/Dreem/Data"
Dreem_dir = "/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/Dreem_cleaned"
# FB_data="/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/Sleep_Staging/Fitbit/NUS3001_N1.csv"


counts = 0
total_num = 0
dreem_data = glob.glob(os.path.join(
    Dreem_dir, "NUS*.csv"))
for Dreem in dreem_data:
    total_num += 1
    # # Extract the subject number and night from the file name
    # subject1, night = os.path.splitext(os.path.basename(PSG_Scores))[
    #     0].split("_")[0:2]

    # # Find all the files in folder2 that match the subject and night of the current file in folder1
    # dreem_data = glob.glob(os.path.join(
    #     Dreem_dir, "NUS*.csv"))
    # matching_files = [
    #     f for f in dreem_data if subject1 in f and night in f]

    # Read in the data from both files as Pandas dataframes
    subject = Dreem.split('/')
    subject1 = subject[-1][0:7]
    df_Dreem = pd.read_csv(Dreem)
    df_Dreem.replace(2, 1, inplace=True)
    indices_to_remove_dreem = df_Dreem[df_Dreem == 7].dropna(
        how='all').index

    print(
        f"Data lengths difference for {subject1}  has  {len(indices_to_remove_dreem)} out of {len(df_Dreem)} artifacts")
    data_type = df_Dreem.iloc[:, 0].unique()
    # print(
    #     f"Data type for {subject1}_{night}: {data_type}")
    # print(
    #     f"Data lengths difference for {subject1}_{night}: {len(df_PSG)-len(df_Dreem)}")
    if len(indices_to_remove_dreem) >= .2*len(df_Dreem):
        counts += 1

        print(f'{subject1} has more than 20% artifacts')
print(
    f'Total number of {counts} out of {total_num} subjects have more than 20% artifacts')
