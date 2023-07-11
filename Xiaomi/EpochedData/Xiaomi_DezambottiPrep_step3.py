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
# exlusion = ['3030']


staging_file_path = "/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/Sleep_Staging"
staging_file_path_xiaomi = "/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/Zepplife"
Saving_file_path = "/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/analysis/DeZambotti/Xiaomi/Data/withXiaomi"
# HPB_data="/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/Sleep_Staging/Fitbit/NUS3001_N1.csv"


nights = ["N1"]


for Night in nights:

    Consesnus_Scores = glob.glob(os.path.join(
        staging_file_path, "Consensus_score", f"NUS*{Night}*.csv"))

    # Oura_sources = glob.glob(os.path.join(
    #     staging_file_path, "Oura3", f"NUS*{Night}*.csv"))

    # data_lengths = {}
    combined_data_AllDays = pd.DataFrame()
    for PSG_Scores in Consesnus_Scores:
        # Extract the subject number and night from the file name
        subject2, night = os.path.splitext(os.path.basename(PSG_Scores))[
            0].split("_")[0:2]
        subject1 = subject2.replace("NUS3", "NUS3_")

        # Find all the files in folder2 that match the subject and night of the current file in folder1
        HPB_data = glob.glob(os.path.join(
            staging_file_path_xiaomi, "PSG_Loff_Lonn", f"NUS*{Night}*.csv"))
        matching_files = [
            f for f in HPB_data if subject1 in f and night in f]

        if matching_files:

            for HPB in matching_files:
                # Read in the data from both files as Pandas dataframes
                df_PSG = pd.read_csv(PSG_Scores)
                df_HPB = pd.read_csv(HPB)

                if len(df_PSG) >= len(df_HPB):
                    df_PSG = df_PSG[0:len(df_HPB)]
                else:
                    df_HPB = df_HPB[0:len(df_PSG)]

                df_PSG.replace(2, 1, inplace=True)

                # Find the indices of rows with 7 in df_PSG
                indices_to_remove = df_PSG[df_PSG == 7].dropna(
                    how='all').index

                # Drop the rows with 7 in df_PSG
                df_PSG.drop(indices_to_remove, inplace=True)

                # Drop the respective rows in df_Oura
                df_HPB.drop(indices_to_remove, inplace=True)

                # Reset index for both dataframes
                df_PSG.reset_index(drop=True, inplace=True)
                df_HPB.reset_index(drop=True, inplace=True)

                print(
                    f"Data lengths difference for {subject1}_{night}: {len(df_PSG)-len(df_HPB)}")

                combined_data = pd.DataFrame(
                    data=[subject2]*len(df_PSG), columns=['subject'])

                #epochs = np.arange(len(df_PSG))+1
                combined_data['epoch'] = np.arange(len(df_PSG))+1
                combined_data['reference'] = df_PSG
                combined_data['device'] = df_HPB

                # combined_data_AllDays = pd.concat(combined_data_AllDays,combined_data)

                combined_data_AllDays = pd.concat(
                    [combined_data_AllDays, combined_data], ignore_index=True)

    combined_data_AllDays.to_csv(os.path.join(Saving_file_path,
                                              f"combined_data_{Night}.csv"), index=False)
