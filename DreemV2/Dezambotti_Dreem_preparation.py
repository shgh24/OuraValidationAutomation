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


nights = ["N1"]
len_diff = pd.DataFrame(columns=['subject', 'PSGlen_Dreemlen'])

for Night in nights:

    Consesnus_Scores = glob.glob(os.path.join(
        staging_file_path, "Consensus_score", f"NUS*{Night}*.csv"))

    # Oura_sources = glob.glob(os.path.join(
    #     staging_file_path, "Oura3", f"NUS*{Night}*.csv"))

    # data_lengths = {}
    combined_data_AllDays = pd.DataFrame()
    for PSG_Scores in Consesnus_Scores:
        # Extract the subject number and night from the file name
        subject1, night = os.path.splitext(os.path.basename(PSG_Scores))[
            0].split("_")[0:2]

        # Find all the files in folder2 that match the subject and night of the current file in folder1
        dreem_data = glob.glob(os.path.join(
            Dreem_dir, "NUS*.csv"))
        matching_files = [
            f for f in dreem_data if subject1 in f and night in f]

        if matching_files:

            for Dreem in matching_files:
                # Read in the data from both files as Pandas dataframes
                df_PSG = pd.read_csv(PSG_Scores)
                df_Dreem = pd.read_csv(Dreem)
                df_Dreem.replace(2, 1, inplace=True)
                indices_to_remove_dreem = df_Dreem[df_Dreem == 7].dropna(
                    how='all').index

                # print(
                #     f"Data lengths difference for {subject1}_{night}: {len(df_PSG)-len(df_FB)}")
                data_type = df_Dreem.iloc[:, 0].unique()
                # print(
                #     f"Data type for {subject1}_{night}: {data_type}")
                print(
                    f"Data lengths difference for {subject1}_{night}: {len(df_PSG)-len(df_Dreem)}")
                # len_diff = len_diff.append({'PSGlen_Dreemlen': len(
                #     df_PSG)-len(df_Dreem), 'subject': subject1}, ignore_index=True)
                if len(indices_to_remove_dreem) <= .2*len(df_Dreem) and abs(len(df_PSG)-len(df_Dreem)) <= 3:
                    # Sanity check
                    # Check if the data lengths are the same
                    if len(df_PSG) >= len(df_Dreem):
                        df_PSG = df_PSG[0:len(df_Dreem)]
                    else:
                        df_Dreem = df_Dreem[0:len(df_PSG)]

                    df_PSG.replace(2, 1, inplace=True)

                    # Find the indices of rows with 7 in df_PSG
                    indices_to_remove = df_PSG[df_PSG == 7].dropna(
                        how='all').index

                    # Drop the rows with 7 in df_PSG
                    df_PSG.drop(indices_to_remove, inplace=True)

                    # Drop the respective rows in df_Oura
                    df_Dreem.drop(indices_to_remove, inplace=True)
                    df_PSG.reset_index(drop=True, inplace=True)
                    df_Dreem.reset_index(drop=True, inplace=True)

                    indices_to_remove_dreem2 = df_Dreem[df_Dreem == 7].dropna(
                        how='all').index
                    df_Dreem.drop(indices_to_remove_dreem2, inplace=True)

                    # Drop the respective rows in df_Oura
                    df_PSG.drop(indices_to_remove_dreem2, inplace=True)

                    # Reset index for both dataframes
                    df_PSG.reset_index(drop=True, inplace=True)
                    df_Dreem.reset_index(drop=True, inplace=True)

                    print(
                        f"Data lengths difference for {subject1}_{night}: {len(df_PSG)-len(df_Dreem)}")
                    # len_diff['subject'] = subject1
                    # len_diff = len_diff.append({'PSGlen_Dreemlen': len(
                    #     df_PSG)-len(df_Dreem), 'subject': subject1}, ignore_index=True)

                    combined_data = pd.DataFrame(
                        data=[subject1]*len(df_PSG), columns=['subject'])

                    # epochs = np.arange(len(df_PSG))+1
                    combined_data['epoch'] = np.arange(len(df_PSG))+1
                    combined_data['reference'] = df_PSG
                    combined_data['device'] = df_Dreem

                    # combined_data_AllDays = pd.concat(combined_data_AllDays,combined_data)
                    combined_data_AllDays = pd.concat(
                        [combined_data_AllDays, combined_data], ignore_index=True)
                # else:
                #     if len(indices_to_remove_dreem) <= .2*len(df_Dreem):
                #         count += 1
                #         print(
                #             f"Data lengths difference for {subject1}_{night} has more than 20% of outliers ")

    combined_data_AllDays.to_csv(os.path.join(Saving_file_path,
                                              f"combined_data_{Night}.csv"), index=False)
# l en_diff.to_csv(os.path.join(Saving_file_path,
#                              f'DataLength.csv'), index=False)
