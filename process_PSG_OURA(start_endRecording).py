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
    'api-access-381407-51bd2bb2d008.json', scopes=scope)
client = gspread.authorize(creds)


# Replace this with your Google Sheet key
sheet_key = '1fS9kNDh1DlJiyphvD_ZbpSERU282xsUPJmjx4iUtm4I'
sheet_name = 'Devices/Session Tracking'

# Read the data from the Google Sheet
sheet = client.open_by_key(sheet_key).worksheet(sheet_name)
#data = sheet.get_all_values()
data = sheet.get_all_records()

# Convert the data to a pandas DataFrame
df = pd.DataFrame(data)
# print(df)

data_dir = '/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/OURA3_Raw'
psg_dir = '/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/Sleep_Staging/Consensus_score'
saving_path = '/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/Sleep_Staging/PSG_Cut2OuraTiming'
filelist = glob.glob(data_dir+'/NUS*_nssa.csv')
# filelist = glob.glob(data_dir+'/NUS3_008_NIGHT02_R_sleepstage_nssa*')

# Debugin
# dataframes = []
# for file in filelist:
#     df = pd.read_csv(file)
#     dataframes.append(df)

# # Concatenate the DataFrames into a single DataFrame
# data = pd.concat(dataframes, axis=0, ignore_index=True)

# Now you can test your for loop using the `data` DataFrame
# for i, row in data.iterrows():

for files in filelist:

    df_Oura = pd.read_csv(files, sep=',')

    # print(df_Oura.columns)

    #OuraTime = pd.Timestamp(df_Oura["timestamp"])

    participant = df_Oura["name"][0]
    match = df[(df['Night'] == int(participant[-3]))
               & (df['Participant ID'] == participant[:-10])]
    subject = participant[:-10].replace('_', '')
    # NUS3001_N1_030323_sleepstage_consensus.csv
    psg_fileName = glob.glob(
        psg_dir + f'/{subject }_N{participant[-3]}_*.csv')
    df_psg = pd.read_csv(psg_fileName[0], sep=',')

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

########################################################################

    # Slice the DataFrame based on lightOff and lightOn
    Diff_start = int(
        (df_Oura.iloc[0]["timestamp"] - lightOff).total_seconds()/30)
    Diff_end = int(
        ((lightON-df_Oura.iloc[-1]["timestamp"]).total_seconds()+30)/30)

    df_sliced = df_psg
    if Diff_start >= 0:
        df_sliced = df_sliced.iloc[Diff_start:]

    if Diff_end >= 0:
        df_sliced = df_sliced.iloc[:-Diff_end]

    # Check if the first row of df_sliced is after lightOff
    if (df_Oura.iloc[0]["timestamp"] < lightOff):
        # Calculate the number of zero value rows to add
        time_diff = lightOff-df_Oura.iloc[0]["timestamp"]

        num_rows = time_diff.total_seconds() / 60-.5

        # Create a DataFrame with zero value rows
        zero_df_LOFF = pd.DataFrame({"timestamp": pd.date_range(
            df_Oura.iloc[0]["timestamp"] + pd.Timedelta(minutes=.5), periods=num_rows*2, freq="30S"), "predicted": 0})

        # Concatenate the zero_df with df_sliced
        df_sliced = pd.concat(
            [zero_df_LOFF["predicted"], df_sliced.iloc[:, 0]], ignore_index=True)

    # If the end time is earlier than lightON, add a row with Sleep Stage = 0
    # if (df_sliced.iloc[-1][["timestamp"]] < lightON-pd.Timedelta(minutes=.5)).item():
    if (df_Oura.iloc[-1][["timestamp"]] > lightON).item():
        time_diff_LONN = df_Oura.iloc[-1]["timestamp"]-lightON
        num_rows_LONN = time_diff_LONN.total_seconds() / 60 - .5

        # Create a DataFrame with zero value rows
        zero_df_LON = pd.DataFrame({"timestamp": pd.date_range(
            df_Oura.iloc[-1]["timestamp"]+pd.Timedelta(minutes=.5), periods=num_rows_LONN*2, freq="30S"), "predicted": 0})
        df_sliced = pd.concat(
            [df_sliced.iloc[:, 0], zero_df_LON['predicted']], ignore_index=True)
    # Mapp Oura

    OuraMapping = {
        'REM': 5,
        'WAKE': 0,
        'LIGHT': 1,
        'DEEP': 3

    }
    df_Oura.loc[:, 'staging'] = df_Oura['predicted'].map(OuraMapping)
    # df_Oura.loc["predicted"] = df_Oura.loc["predicted"].map(OuraMapping)
    print(f'{subject} difference length of Oura-psg is {len(df_Oura)-len(df_sliced)}')

    # /Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/Sleep_Staging/Oura3
    # df_sliced.iloc[:, 0].to_csv(files.replace(
    #     '_nssa.csv', '_nssa_clean.csv').replace('S3_', 'S3').replace('NIGHT', 'N').replace('OURA3_Raw', 'Sleep_Staging/saving_path'), index=False, header=False)
