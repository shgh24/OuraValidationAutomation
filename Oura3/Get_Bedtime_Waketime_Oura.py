import mne
import os
import glob
import pandas as pd
import gspread
from google.oauth2 import service_account
from datetime import datetime, timedelta
import shutil
import pytz
import numpy as np


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
filelist = glob.glob(data_dir+'/NUS*NIGHT01_L*_nssa.csv')
Saving_file_path = "/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/analysis/DeZambotti/Oura3/Data/SOL_OURA"

# staging_file_path = "/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/Sleep_Staging"
# Now you can test your for loop using the `data` DataFrame
staging_file_path = '/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/Sleep_Staging/Consensus_score'
combined_data_AllDays = pd.DataFrame()
combined_data_AllDays_diff = pd.DataFrame()

for files in filelist:

    df_Oura = pd.read_csv(files, sep=',')

    participant = df_Oura["name"][0]
    match = df[(df['Night'] == int(participant[-3]))
               & (df['Participant ID'] == participant[:-10])]

    subj = df_Oura['name'][0][0:8].replace('_', '')
    night = df_Oura['name'][0][-3]

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

    OuraMapping = {
        'REM': 5,
        'WAKE': 0,
        'LIGHT': 1,
        'DEEP': 3

    }

    df_Oura['predicted'] = df_Oura['predicted'].map(OuraMapping)

    A = df_Oura['timestamp'][0]
    B = lightOff

    hour = int(A.strftime('%H'))
    minutes = int(A.strftime('%M'))
    seconds = int(A.strftime('%S'))
    hour_in_seconds_A1 = int(hour) * 60 + int(minutes) + int(seconds)/60

    if hour > 18:
        hr = -24*60

        hour_in_seconds_A1 = hour_in_seconds_A1+hr

    hour = int(B.strftime('%H'))
    minutes = int(B.strftime('%M'))
    seconds = int(B.strftime('%S'))
    hour_in_seconds_B1 = int(hour) * 60 + int(minutes) + int(seconds)/60

    if hour > 18:
        hr = -24*60

        hour_in_seconds_B1 = hour_in_seconds_B1+hr

    diff = hour_in_seconds_A1-hour_in_seconds_B1
    print(
        f"Bedtime start difference Based on Seconds  {subj}  NIGHT {night}    {diff} minutes            OURA {A }  and  PSG {B}")

    # Calculate the time difference and include the sign
    time_diff = A - B
    diff_seconds1 = time_diff.total_seconds()

    # difference of Lights ON and Oura start of recording
    BedtimeStart_difference = diff_seconds1

    print(
        f"Bedtime start difference  {subj}  NIGHT {night}    {diff_seconds1/60} minutes            OURA {A }  and  PSG {B}")

    # A2 = df_Oura['timestamp'][len(df_Oura)-1]
    A = df_Oura['timestamp'].iloc[-1]
    B = lightON

    hour = int(A.strftime('%H'))
    minutes = int(A.strftime('%M'))
    seconds = int(A.strftime('%S'))
    hour_in_seconds_A2 = int(hour) * 60 + int(minutes) + int(seconds)/60

    if hour > 18:
        hr = -24*60

        hour_in_seconds_A2 = hour_in_seconds_A2+hr

    hour = int(B.strftime('%H'))
    minutes = int(B.strftime('%M'))
    seconds = int(B.strftime('%S'))
    hour_in_seconds_B2 = int(hour) * 60 + int(minutes) + int(seconds)/60

    if hour > 18:
        hr = -24*60

        hour_in_seconds_B2 = hour_in_seconds_B2+hr

    diff = hour_in_seconds_A2-hour_in_seconds_B2

    # Calculate the time difference and include the sign
    time_diff2 = A - B
    diff_seconds2 = time_diff2.total_seconds()

    BedtimeEnd_difference = diff_seconds2
    print(
        f"Bedtime end difference    {subj}  NIGHT {night}    {BedtimeEnd_difference} minutes            OURA {A }  and  PSG {B}")

    # SOL_Oura = df_Oura[df_Oura['predicted'] != 'WAKE']['timestamp'][0]
    SOL_Oura = df_Oura.loc[df_Oura['predicted']
                           != 'WAKE', 'timestamp'].values[0]

    PSG_Score = f"{staging_file_path}/{subj}_N{night}*.csv"
    # NUS3001_N1_030323_sleepstage_consensus.csv
    psg_file = glob.glob(PSG_Score)

    df_PSG = pd.read_csv(psg_file[0])

    if os.path.exists(psg_file[0]) and os.path.getsize(psg_file[0]) > 0:
        start_ep_diff = BedtimeStart_difference/30
        end_ep_diff = BedtimeEnd_difference/30

        combined_data_diff = pd.DataFrame({
            'subj': [subj],
            'start_bias': [start_ep_diff/2],
            'end_bias': [end_ep_diff/2],
            'start_Oura': [hour_in_seconds_A1],
            'start_PSG': [hour_in_seconds_B1],
            'end_Oura': [hour_in_seconds_A2],
            'end_PSG': [hour_in_seconds_B2]
        })

        combined_data_AllDays_diff = combined_data_AllDays_diff.append(
            combined_data_diff, ignore_index=True
        )

        if end_ep_diff < 0:

            df_PSG = df_PSG[:len(df_PSG)+int(end_ep_diff)+1]
        else:

            zeros_df1 = pd.DataFrame({'0': [0] * (int(abs(end_ep_diff))+1)})
            df_PSG = pd.concat([df_PSG, zeros_df1], ignore_index=True)

        if start_ep_diff > 0:
            df_PSG = df_PSG[int(start_ep_diff)-1:]
        else:

            zeros_df2 = pd.DataFrame({'0': [0] * (int(abs(start_ep_diff))+1)})
            df_PSG = pd.concat([zeros_df2, df_PSG], ignore_index=True)

        df_PSG.replace(2, 1, inplace=True)

        df_PSG.reset_index(drop=True, inplace=True)
        df_Oura.reset_index(drop=True, inplace=True)

        # print(
        #     f"Data lengths difference after cleaning for {subj}  NIGHT {night}: {len(df_PSG)-len(df_Oura)}")

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

        # print(
        #     f"Data lengths difference after cleaning for {subj}  NIGHT {night}: {len(df_PSG)-len(df_Oura)}")

        if (subj == 'NUS3010') or (subj == 'NUS3031'):
            zeros_df = pd.DataFrame(
                {'0': [0] * (int(abs(len(df_PSG)-len(df_Oura))))})
            df_PSG = pd.concat([zeros_df, df_PSG], ignore_index=True)

        if len(df_PSG)-len(df_Oura) < 0:
            df_Oura = df_Oura[:-1]

        # print(
        #     f"Data lengths difference after cleaning for {subj}  NIGHT {night}: {len(df_PSG)-len(df_Oura)}")

        combined_data = pd.DataFrame(
            data=[subj]*len(df_PSG), columns=['subject'])

        #epochs = np.arange(len(df_PSG))+1
        combined_data['epoch'] = np.arange(len(df_PSG))+1
        combined_data['reference'] = df_PSG['0']
        combined_data['device'] = df_Oura['predicted']

        # combined_data_AllDays = pd.concat(combined_data_AllDays,combined_data)
        combined_data_AllDays = pd.concat(
            [combined_data_AllDays, combined_data], ignore_index=True)

# combined_data_AllDays.to_csv(os.path.join(Saving_file_path,
#                                           f"combined_data_N{night}_L.csv"), index=False)

# print(combined_data_AllDays_diff)

combined_data_AllDays_diff.to_csv(os.path.join(Saving_file_path,
                                               f"BedtimeDiff_data_N{night}_L.csv"), index=False)
