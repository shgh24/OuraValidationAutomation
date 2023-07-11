from datetime import datetime
import os as os
import numpy as np
import mne
import os
import glob
import pandas as pd
import gspread
from google.oauth2 import service_account
from datetime import datetime, timedelta
import shutil
import pytz


# Load credentials and connect to Google Sheets API
scope = ['https://www.googleapis.com/auth/spreadsheets']
creds = service_account.Credentials.from_service_account_file(
    '/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/analysis/DeZambotti/GoogleSheet_api_key/api-access-381407-51bd2bb2d008.json', scopes=scope)
client = gspread.authorize(creds)


# Replace this with your Google Sheet key
with open('/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/analysis/DeZambotti/GoogleSheet_api_key/sheet_key.txt') as f:
    contents = f.readlines()
sheet_key = contents[0]
sheet_name = 'Devices/Session Tracking'
# Read the data from the Google Sheet
sheet = client.open_by_key(sheet_key).worksheet(sheet_name)

data = sheet.get_all_records()

# Convert the data to a pandas DataFrame

df1 = pd.DataFrame(data)

# add subject 3101 to the df structure
sheet_name2 = 'NUS Onsite Dry-Run Data'
# Read the data from the Google Sheet
sheet2 = client.open_by_key(sheet_key).worksheet(sheet_name2)
data2 = sheet2.get_all_records()

df2 = pd.DataFrame(data2)


df = pd.concat([df1, df2])


data_dir = '/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/OURA3_Raw'
filelist = glob.glob(data_dir+'/NUS*_nssa.csv')

# Now you can test your for loop using the `data` DataFrame


for files in filelist:

    df_Oura = pd.read_csv(files, sep=',')
    # print(df_Oura.columns)

    #OuraTime = pd.Timestamp(df_Oura["timestamp"])

    participant = df_Oura["name"][0]
    match = df[(df['Night'] == int(participant[-3]))
               & (df['Participant ID'] == participant[:-10])]

    lightOff = match.iloc[0]['Session start local time']
    lightON = match.iloc[0]['Session end local time']

    lightOff = pd.Timestamp(lightOff)
    base_date = pd.Timestamp(match.iloc[0]['Session end date'])
    if lightOff.hour > 19:
        lightOff_day = base_date - pd.Timedelta(days=1)
        lightOff = lightOff.replace(year=lightOff_day.year,
                                    month=lightOff_day.month, day=lightOff_day.day).tz_localize(pytz.UTC)
    else:
        lightOff = lightOff.replace(year=base_date.year,
                                    month=base_date.month, day=base_date.day).tz_localize(pytz.UTC)
    lightON = pd.Timestamp(lightON).replace(
        year=base_date.year, month=base_date.month, day=base_date.day).tz_localize(pytz.UTC)
    s = df_Oura['timestamp']
    s_cut = s.str[:-6]
    df_Oura['timestamp'] = s_cut
    #df_Oura = pd.DataFrame({'timestamp': s_cut})

    # Convert timestamp column to Timestamp objects
    df_Oura['timestamp'] = pd.to_datetime(df_Oura['timestamp'], utc=True)

    # Slice the DataFrame based on lightOff and lightOn
    df_sliced = df_Oura.loc[(df_Oura['timestamp'] >= lightOff)
                            & (df_Oura['timestamp'] < lightON), ['timestamp', 'predicted']]

    # Check if the first row of df_sliced is after lightOff
    if (df_sliced.iloc[0][["timestamp"]] > lightOff).item():
        # Calculate the number of zero value rows to add
        time_diff = df_sliced.iloc[0]["timestamp"] - lightOff

        num_rows = time_diff.total_seconds() / 60-.5

        # Create a DataFrame with zero value rows
        zero_df_LOFF = pd.DataFrame({"timestamp": pd.date_range(
            lightOff+pd.Timedelta(minutes=.5), periods=num_rows*2, freq="30S"), "predicted": 'NaN'})

        # Concatenate the zero_df with df_sliced
        df_sliced = pd.concat([zero_df_LOFF, df_sliced], ignore_index=True)

    # If the end time is earlier than lightON, add a row with Sleep Stage = 0
    # if (df_sliced.iloc[-1][["timestamp"]] < lightON-pd.Timedelta(minutes=.5)).item():
    if (df_sliced.iloc[-1][["timestamp"]] < lightON).item():
        time_diff_LONN = lightON-df_sliced.iloc[-1]["timestamp"]
        num_rows_LONN = time_diff_LONN.total_seconds() / 60 - .5

        # Create a DataFrame with zero value rows
        zero_df_LON = pd.DataFrame({"timestamp": pd.date_range(
            df_sliced.iloc[-1]["timestamp"]+pd.Timedelta(minutes=.5), periods=num_rows_LONN*2, freq="30S"), "predicted": 'NaN'})
        df_sliced = pd.concat([df_sliced, zero_df_LON], ignore_index=True)
    # Mapp Oura

    OuraMapping = {
        'REM': 5,
        'WAKE': 0,
        'LIGHT': 1,
        'DEEP': 3,
        'NaN': 7

    }

    df_sliced['predicted'] = df_sliced['predicted'].map(OuraMapping)
    # /Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/Sleep_Staging/Oura3
    df_sliced['predicted'].to_csv(files.replace(
        '_nssa.csv', '_nssa_clean.csv').replace('S3_', 'S3').replace('NIGHT', 'N').replace('data_raw/OURA3_Raw', 'analysis/DeZambotti/Oura3/Data/EBE/Common_epochs/RAW_Data'), index=False, header=False)


################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################
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


# Basically 3010n1, 3020n2 and 3030n1 psg terminated before lights on.
# For 3010 and 3020 subject was already awake so we can append wake to end of psg record.
# For 3030 subject was still sleeping so if we are doing any wake time estimation detection, nd to skip this.
# For NUS3101_N2 Signal flatline at 0748 ish. Lights on at 0800. Flatline during peri-sleep task. Wake at 0739.


# These dta points has issues
# Lights off time was 21: 30pm but online recording of PSG only started at 21: 39pm(exact).
# Data cut according to epoch sizes(21: 39pm exact start) on online recording. Full data extracted on PSG device(offline recording).
# Epoch data contains all data. Take not in DOMINO light backup, NUS3043_N2_F contains the full data while NUS3043_N2_O does not.


outliers_cut_end = ['NUS3010_N1', 'NUS3020_N2']
outlier_cut_start = []

# Subject NUS3001 has participated in study twice because the first time recording was spoiled (NUS3101 is the new recording ID in his second attempt)
# Subject 3035 dropped out after first time recording N1
outlier = ['NUS3001_N1', 'NUS3035_N1', 'NUS3001_N2']
# outlier = ['NUS3021_N1', 'NUS3007_N1', 'NUS3001_N2']

today = datetime.now().strftime("%Y_%m_%d")

# NUS3010_N1
# NUS3020_N2
# NUS3030_N1
# NUS3101_N2
# NUS3050_N1
# NUS3050_N2
# NUS3040_N1


staging_file_path = "/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/Sleep_Staging"
staging_file_path_oura = "/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/analysis/DeZambotti/Oura3/Data/EBE/Common_epochs/RAW_Data"
Saving_file_path = "/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/analysis/DeZambotti/Oura3/Data/EBE/Common_epochs"
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
                staging_file_path_oura, f"NUS*{Night}*{hand}*.csv"))

            # data_lengths = {}
            combined_data_AllDays = pd.DataFrame()
            for PSG_Scores in Consesnus_Scores:
                # Extract the subject number and night from the file name
                subject1, night_psg = os.path.splitext(os.path.basename(PSG_Scores))[
                    0].split("_")[0:2]

                night = night_psg.replace("N1", "N01").replace("N2", "N02")

                # Find all the files in folder2 that match the subject and night of the current file in folder1
                matching_files = [
                    f for f in Oura_sources if subject1 in f and night in f]

                if matching_files:

                    for Oura in matching_files:
                        # Read in the data from both files as Pandas dataframes
                        df_PSG = pd.read_csv(PSG_Scores)
                        df_Oura = pd.read_csv(Oura)
                        subject_id = f'{subject1}_{night_psg}'

                        # print(
                        #     f"Data lengths difference for {subject1}_{night}: {len(df_PSG)-len(df_Oura)}")
                        # f.write(
                        #     f"Data lengths difference for {subject1}_{night}:  {len(df_PSG)-len(df_Oura)}\n")

                        # Sanity check
                        # Check if the data lengths are the same
                        if subject_id not in outlier:
                            if len(df_PSG) >= len(df_Oura):
                                df_PSG = df_PSG[0:len(df_Oura)]

                            elif len(df_PSG) < len(df_Oura) and subject_id in outlier_cut_start:
                                start_ind = len(df_Oura)-len(df_PSG)
                                df_Oura = df_Oura[start_ind:]
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

                            indices_to_remove = df_Oura[df_Oura == 7].dropna(
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

            combined_data_AllDays.to_csv(os.path.join(Saving_file_path,
                                                      f"combined_data_{Night}_{hand}_{today}.csv"), index=False)
