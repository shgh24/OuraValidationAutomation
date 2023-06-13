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
df1 = pd.DataFrame(data)
# print(df)
# add subject 3101 to the df structure
sheet_name2 = 'NUS Onsite Dry-Run Data'
# Read the data from the Google Sheet
sheet2 = client.open_by_key(sheet_key).worksheet(sheet_name2)
#data = sheet.get_all_values()
data2 = sheet2.get_all_records()

df2 = pd.DataFrame(data2)


df = pd.concat([df1, df2])

# datadir = '/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/OURA3_Raw/NUS3_NSSA_hypnograms/saved'
# dest_dir = '/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/OURA3_Raw/NUS3_NSSA_hypnograms/v2_processed'
datadir = '/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/OURA3_Raw/NUS3_NSSA_hypnograms_21March-31May/Fisrt_process'
dest_dir = '/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/OURA3_Raw/NUS3_NSSA_hypnograms_21March-31May/v3_processed'
file_names = os.listdir(datadir)


matched_subject_ids = []

count1 = 0
for file_name in [f for f in os.listdir(datadir) if f.endswith(".csv")]:
    count1 = count1+1
    # Matching file names with subject IDs
    parts = file_name.split('_')
    room = int(parts[0].replace('ROOM', ''))
    hand_wrist = parts[1].replace('R', 'Right').replace('L', 'Left')
    session_end_date = parts[3].split('T')[0]

    matched_df = df[(df['Hand / Wrist'] == hand_wrist) &
                    (df['Session end date'] == session_end_date) &
                    (df['Room #'] == room)]

    if not matched_df.empty:
        subject_id = matched_df['Participant ID'].iloc[0]
        Night_no = matched_df['Night'].iloc[0]
        matched_subject_ids.append(subject_id)

        new_name = f'{subject_id}_NIGHT0{Night_no}_{hand_wrist[0]}_sleepstage_nssa.csv'
        # data_n = pd.read_csv(os.path.join(datadir, file_name))
        # data_n['name'] = f'{subject_id}_NIGHT0{Night_no}_{hand_wrist[0]}'

        shutil.copy(os.path.join(datadir, file_name),
                    os.path.join(dest_dir, new_name))

    else:
        matched_subject_ids.append(None)

# Print the matched subject IDs
count2 = 0
for file_name, subject_id in zip(file_names, matched_subject_ids):
    count2 = count2+1
    # NUS3_001_NIGHT01_L_sleepstage_nssa.csv
    print(f"File: {file_name} | Subject ID: {subject_id}")


# name	timestamp	predicted
# NUS3_001_NIGHT01_L	2023-03-02 23:51:00+08:00	WAKE

print(count1, count2)
for file_name in [f for f in os.listdir(dest_dir) if f.endswith(".csv")]:

    data_n = pd.read_csv(os.path.join(dest_dir, file_name))
    # NUS3_053_NIGHT02_R_sleepstage_nssa.csv
    parts = file_name.split('sleepstage')
    data_n['name'] = parts[0][:-1]
    data_n.to_csv(os.path.join(dest_dir, file_name), index=False)
