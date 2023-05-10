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
#data = sheet.get_all_values()
data = sheet.get_all_records()

# Convert the data to a pandas DataFrame
df = pd.DataFrame(data)
# print(df)

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
            lightOff+pd.Timedelta(minutes=.5), periods=num_rows*2, freq="30S"), "predicted": 'WAKE'})

        # Concatenate the zero_df with df_sliced
        df_sliced = pd.concat([zero_df_LOFF, df_sliced], ignore_index=True)

    # If the end time is earlier than lightON, add a row with Sleep Stage = 0
    # if (df_sliced.iloc[-1][["timestamp"]] < lightON-pd.Timedelta(minutes=.5)).item():
    if (df_sliced.iloc[-1][["timestamp"]] < lightON).item():
        time_diff_LONN = lightON-df_sliced.iloc[-1]["timestamp"]
        num_rows_LONN = time_diff_LONN.total_seconds() / 60 - .5

        # Create a DataFrame with zero value rows
        zero_df_LON = pd.DataFrame({"timestamp": pd.date_range(
            df_sliced.iloc[-1]["timestamp"]+pd.Timedelta(minutes=.5), periods=num_rows_LONN*2, freq="30S"), "predicted": 'WAKE'})
        df_sliced = pd.concat([df_sliced, zero_df_LON], ignore_index=True)
    # Mapp Oura

    OuraMapping = {
        'REM': 5,
        'WAKE': 0,
        'LIGHT': 1,
        'DEEP': 3

    }

    df_sliced['predicted'] = df_sliced['predicted'].map(OuraMapping)
    # /Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/Sleep_Staging/Oura3
    df_sliced['predicted'].to_csv(files.replace(
        '_nssa.csv', '_nssa_clean.csv').replace('S3_', 'S3').replace('NIGHT', 'N').replace('OURA3_Raw', 'Sleep_Staging/Oura3'), index=False, header=False)
