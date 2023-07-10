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


HPB_raw_path = '/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/Zepplife/Zepp_Life_processed.csv'
HPB_saving_processed = '/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/Zepplife/PSG_Loff_Lonn'
HPB_saving_RAW = '/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/Zepplife/subjectbysubject_RAW'

# reading the HPB file
data = pd.read_csv(HPB_raw_path)
stages = pd.unique(data["Stage"])
# [Light sleep', 'REM', 'Awake', 'Deep Sleep', 'Deep sleep', 'Light Sleep']

data["Stage"] = data["Stage"].map({
    'Light sleep':
    1,
    'Deep sleep':
    3,
    'Awake':
    0,
    'REM':
    5,
    'Deep Sleep':
    3,
    'Light Sleep':
    1})


df_clean = pd.DataFrame(columns=["name",
                                 "timestamp",
                                 "predicted"])

IDS = pd.unique(data["NUS_ID"])

# exclude = ["NUS3056"]

# IDS = IDS[IDS != "NUS3056"]

for id in IDS:

    df_temp = data[(data["NUS_ID"] == id)]
    df_temp = df_temp.loc[df_temp.index.repeat(df_temp.Duration*2)]

    participant = id[0:-3]
    Night = id[-1]
    match = df[(df['Night'] == int(Night))
               & (df['Participant ID'] == participant)]

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

    # s = df_temp["intervalstartdatetime"]
    # s_cut = s.str[:-5]
    # df_temp["intervalstartdatetime"] = s_cut
    # df_temp['timestamp'] = pd.to_datetime(
    #     df_temp['start_stage'], utc=True)
    df_temp['timestamp'] = pd.to_datetime(
        df_temp['start_stage'], utc=True, dayfirst=True)

    # df_Oura['timestamp'] = pd.to_datetime(df_Oura['timestamp'], utc=True)

    # TT = pd.DataFrame({"timestamp": pd.date_range(
    #     df_temp.iloc[0]["timestamp"]+pd.Timedelta(minutes=.5), periods=len(df_temp["timestamp"]), freq="30S")})

    df_temp["timestamp"] = pd.date_range(
        df_temp.iloc[0]["timestamp"]+pd.Timedelta(minutes=.5), periods=len(df_temp["timestamp"]), freq="30S")

    df_sliced = df_temp.loc[(df_temp['timestamp'] >= lightOff)
                            & (df_temp['timestamp'] < lightON), ['timestamp', 'Stage']]
    df_sliced['predicted'] = df_sliced['Stage']

    # Check if the first row of df_sliced is after lightOff
    if (df_sliced.iloc[0][["timestamp"]] > lightOff).item():
        # Calculate the number of zero value rows to add
        time_diff = df_sliced.iloc[0]["timestamp"] - lightOff

        num_rows = time_diff.total_seconds() / 60-.5

        # Create a DataFrame with zero value rows
        zero_df_LOFF = pd.DataFrame({"timestamp": pd.date_range(
            lightOff+pd.Timedelta(minutes=.5), periods=num_rows*2, freq="30S"), "predicted": '0'})

        # Concatenate the zero_df with df_sliced
        df_sliced = pd.concat([zero_df_LOFF, df_sliced], ignore_index=True)

    # If the end time is earlier than lightON, add a row with Sleep Stage = 0
    # if (df_sliced.iloc[-1][["timestamp"]] < lightON-pd.Timedelta(minutes=.5)).item():
    if (df_sliced.iloc[-1][["timestamp"]] < lightON).item():
        time_diff_LONN = lightON-df_sliced.iloc[-1]["timestamp"]
        num_rows_LONN = time_diff_LONN.total_seconds() / 60 - .5

        # Create a DataFrame with zero value rows
        zero_df_LON = pd.DataFrame({"timestamp": pd.date_range(
            df_sliced.iloc[-1]["timestamp"]+pd.Timedelta(minutes=.5), periods=num_rows_LONN*2, freq="30S"), "predicted": '0'})
        df_sliced = pd.concat([df_sliced, zero_df_LON], ignore_index=True)

        file_name = f'{id}.csv'
        # NUS3001_N01_L_sleepstage_nssa_clean.csv
        # /Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/Sleep_Staging/Oura3
        df_sliced['predicted'].to_csv(os.path.join(
            HPB_saving_processed, file_name), index=False, header=False)
        df_temp.to_csv(os.path.join(
            HPB_saving_RAW, file_name), index=False, header=False)

    # Mapp Oura
    # df_clean["name"] =

    print('done')
