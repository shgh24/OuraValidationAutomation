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


# These dta points has issues
# Lights off time was 21: 30pm but online recording of PSG only started at 21: 39pm(exact). Data cut according to epoch sizes(21: 39pm exact start) on online recording. Full data extracted on PSG device(offline recording). Epoch data contains all data. Take not in DOMINO light backup, NUS3043_N2_F contains the full data while NUS3043_N2_O does not.

outliers_add = ['NUS3010_N1', 'NUS3020_N2']
outlier_cut = ['NUS3043_N1']


# NUS3010_N1
# NUS3020_N2
# NUS3030_N1
# NUS3101_N2
# NUS3050_N1
# NUS3050_N2
# NUS3040_N1


staging_file_path = "/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/Sleep_Staging"
Saving_file_path = "/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/analysis/DeZambotti/Oura3/Data"
# Oura_sources = glob.glob(os.path.join(
#     staging_file_path, "Oura3", "NUS*_N*_*.csv"))
# Consesnus_Scores = glob.glob(os.path.join(
#     staging_file_path, "Consensus_score", "NUS*_N*_*.csv"))
# set the filename to write to
filename = "/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/analysis/DeZambotti/Oura3/Data/data_lengths.txt"
with open(filename, "a") as f:  # open the file in append mode

    nights = ["N1", "N2"]
    Hands = ["L", "R"]
    for hand in Hands:

        for Night in nights:

            Consesnus_Scores = glob.glob(os.path.join(
                staging_file_path, "Consensus_score", f"NUS*{Night}*.csv"))

            Night = Night.replace("N1", "N01").replace("N2", "N02")
            Oura_sources = glob.glob(os.path.join(
                staging_file_path, "Oura3", f"NUS*{Night}*{hand}*.csv"))

            # data_lengths = {}
            combined_data_AllDays = pd.DataFrame()
            for PSG_Scores in Consesnus_Scores:
                # Extract the subject number and night from the file name
                subject1, night = os.path.splitext(os.path.basename(PSG_Scores))[
                    0].split("_")[0:2]

                night = night.replace("N1", "N01").replace("N2", "N02")

                # Find all the files in folder2 that match the subject and night of the current file in folder1
                matching_files = [
                    f for f in Oura_sources if subject1 in f and night in f]

                if matching_files:

                    for Oura in matching_files:
                        # Read in the data from both files as Pandas dataframes
                        df_PSG = pd.read_csv(PSG_Scores)
                        df_Oura = pd.read_csv(Oura)

                        print(
                            f"Data lengths difference for {subject1}_{night}: {len(df_PSG)-len(df_Oura)}")
                        f.write(
                            f"Data lengths difference for {subject1}_{night}:  {len(df_PSG)-len(df_Oura)}\n")

                        # Sanity check
                        # Check if the data lengths are the same
                        if len(df_PSG) >= len(df_Oura):
                            df_PSG = df_PSG[0:len(df_Oura)]
                        else:
                            df_Oura = df_Oura[0:len(df_PSG)]

                        # Replace 2 with 1 in df_PSG
                        df_PSG.replace(2, 1, inplace=True)

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
                            f"Data lengths difference after cleaning for {subject1}_{night}: {len(df_PSG)-len(df_Oura)}")
            #             print(
            #                 f"Data lengths difference for {subject1}_{night}: {data_difference}")
            # # write the current line to the file with a newline character

                        combined_data = pd.DataFrame(
                            data=[subject1]*len(df_PSG), columns=['subject'])

                        #epochs = np.arange(len(df_PSG))+1
                        combined_data['epoch'] = np.arange(len(df_PSG))+1
                        combined_data['reference'] = df_PSG
                        combined_data['device'] = df_Oura

                        # combined_data_AllDays = pd.concat(combined_data_AllDays,combined_data)
                        combined_data_AllDays = pd.concat(
                            [combined_data_AllDays, combined_data], ignore_index=True)

            # combined_data_AllDays.to_csv(os.path.join(Saving_file_path,
            #                                           f"combined_data_{Night}_{hand}.csv"), index=False)
