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
# add_wake = ['3010_N1', '3020_N2']
# exlusion = ['3022_N2']


# Recording ID
# NUS3010_N1
# NUS3020_N2
# NUS3030_N1
# NUS3101_N2  1072  1030
# NUS3050_N1  939   940
# NUS3050_N2  1076  1078
# NUS3040_N1  935   936


# staging_file_path = "/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/Sleep_Staging"
Saving_file_path = "/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/analysis/DeZambotti/Acti/Data/June_20_2023"
# FB_data="/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/Sleep_Staging/Fitbit/NUS3001_N1.csv"
acti = '/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/Sleep_Staging/Actigraphy/epoched/'
# 'NUS3001_2-3-2023_N1_Actigraphy.csv'
psg = '/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/Sleep_Staging/Consensus_score/'
# NUS3001_N1_030323_sleepstage_consensus.csv'

nights = ["N1", "N2"]


outliers_cut_end = ['NUS3010_N1', 'NUS3020_N2']
outlier_cut_start = ['NUS3043_N1', 'NUS3021_N1']


for Night in nights:

    # /Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/analysis/DeZambotti/Oura3/Data/SubjectID_N01_L_2023_05_10.csv
    Night_oura = Night.replace('N', 'N0')
    subj_list = pd.read_csv(
        f'/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/analysis/DeZambotti/Oura3/Data/SubjectID_{Night_oura}_L_2023_06_13.csv')
    # Consesnus_Scores = glob.glob(os.path.join(
    #     staging_file_path, "Consensus_score", f"NUS*{Night}*.csv"))

    combined_data_AllDays = pd.DataFrame()
    for index, row in subj_list.iterrows():
        # Extract the subject number and night from the file name
        # subject1, night = os.path.splitext(os.path.basename(PSG_Scores))[
        #     0].split("_")[0:2]

        # Find all the files in folder2 that match the subject and night of the current file in folder1
        subj = row['subj']
        acti_file = f'{acti}{subj}*{Night}_Actigraphy.csv'
        Acti_data = glob.glob(acti_file)
        psg_file = f'{psg}{subj}_{Night}*sleepstage_consensus.csv'
        PSG_data = glob.glob(psg_file)
        # matching_files = [
        #     f for f in FB_data if subject1 in f and night in f]

        if len(Acti_data) > 0:

            # for FB in matching_files:
            # Read in the data from both files as Pandas dataframes
            df_PSG = pd.read_csv(PSG_data[0])
            df_Oura = pd.read_csv(Acti_data[0])

            print(
                f"Data lengths difference for {subj}_{Night}: {len(df_PSG)-len(df_Oura)}")
            # data_type = df_FB['0'].unique()
            # print(
            #     f"Data type for {subject1}_{night}: {data_type}")

            subject_night = f"{subj}_{Night}"
            if len(df_PSG) >= len(df_Oura):
                if subject_night in outlier_cut_start:
                    start_ind1 = len(df_PSG)-len(df_Oura)
                    df_PSG = df_PSG[start_ind1:]
                else:
                    df_PSG = df_PSG[0:len(df_Oura)]

            elif len(df_PSG) < len(df_Oura) and subject_night in outlier_cut_start:
                print(
                    f"PSG DATA SHORTER {subj}_{Night}: {len(df_PSG)-len(df_Oura)}")
                start_ind = len(df_Oura)-len(df_PSG)
                df_Oura = df_Oura[start_ind:]
            else:
                df_Oura = df_Oura[0:len(df_PSG)]
                print(
                    f"ACTI  DATA SHORTER {subj}_{Night}: {len(df_PSG)-len(df_Oura)}")

            df_PSG.replace(2, 1, inplace=True)
            df_PSG.replace(3, 1, inplace=True)
            df_PSG.replace(5, 1, inplace=True)
            # df_PSG.replace(3, 1, inplace=True)

            # Find the indices of rows with 7 in df_PSG
            indices_to_remove = df_PSG[df_PSG == 7].dropna(
                how='all').index

            # Drop the rows with 7 in df_PSG
            df_PSG.drop(indices_to_remove, inplace=True)

            # Drop the respective rows in df_Oura
            df_Oura.drop(indices_to_remove, inplace=True)

            # Reset index for both dataframes
            df_PSG.reset_index(drop=True, inplace=True)
            df_Oura.reset_index(drop=True, inplace=True)

            print(
                f"AFTER DATA cut and impute Data lengths difference for {subj}_{Night}: {len(df_PSG)-len(df_Oura)}")

            combined_data = pd.DataFrame(
                data=[subj]*len(df_PSG), columns=['subject'])

            #epochs = np.arange(len(df_PSG))+1
            combined_data['epoch'] = np.arange(len(df_PSG))+1
            combined_data['reference'] = df_PSG
            combined_data['device'] = df_Oura

            # combined_data_AllDays = pd.concat(combined_data_AllDays,combined_data)
            combined_data_AllDays = pd.concat(
                [combined_data_AllDays, combined_data], ignore_index=True)

        else:
            print(f'{subj}_ {Night} No Acti data ')

    combined_data_AllDays.to_csv(os.path.join(Saving_file_path,
                                              f"combined_data_{Night}.csv"), index=False)
print('done')
