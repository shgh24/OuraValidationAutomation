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


# df=pd.read_csv('')

data_dir = '/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/OURA3_Raw/NUS3_NSSA_hypnograms_21March-31May'
save_path = '/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/OURA3_Raw/NUS3_NSSA_hypnograms_21March-31May/test2'
list_f = os.listdir(data_dir)

for room_no in range(4):
    room_str = f'ROOM{room_no+1}'
    print(room_str)

    filter_object = filter(lambda a: room_str in a, list_f)

    for i in (list(filter(lambda a: room_str in a, list_f))):
        data = pd.read_csv(os.path.join(data_dir, i))

        hand = i.replace('_L', '_Left').replace(
            '_R', '_Right').split('_')[1][:-4]
        # filter all data by room numbers in the oura master file:
        df_room = df[(df['Room #'] == (
            room_no+1)) & (df['Hand / Wrist'] == hand)]
        df_room = df_room.reset_index()

        counter = 0

        for days in df_room['Session end date']:
            counter += 1
            # print(days)

            sleep_start = (datetime.fromisoformat(
                days) - timedelta(days=1)).replace(hour=19, minute=0, second=0)
            sleep_end = (datetime.fromisoformat(days)
                         ).replace(hour=11, minute=0, second=0)

            sleep_period_data = []

            sleep_period_data = pd.DataFrame()
            data['timestamp'] = pd.to_datetime(
                data['timestamp'], format='%Y-%m-%dT%H:%M:%S%z', errors='coerce')
            # data['timestamp'] = data['timestamp'].apply(
            #     lambda x: datetime.fromisoformat(x.replace('+08:00', '')).replace(tzinfo=None))
            from pytz import timezone
            # Replace 'Asia/Shanghai' with the actual timezone
            tz = timezone('Asia/Shanghai')

            # Convert sleep_start and sleep_end to timezone-aware datetime objects
            sleep_start = tz.localize(sleep_start)
            sleep_end = tz.localize(sleep_end)

            df_sliced = data.loc[(data['timestamp'] >= sleep_start)
                                 & (data['timestamp'] < sleep_end), ['timestamp', 'predicted']]

            if not df_sliced.empty:

                # save_to_csv(day, sleep_period_data, files, save_path)

                subject_id = df_room['Participant ID'][counter-1]
                Night_no = df_room['Night'][counter-1]
                df_sliced['name'] = f'{subject_id}_NIGHT0{Night_no}_{i[6]}'
                new_name = f'{subject_id}_NIGHT0{Night_no}_{i[6]}_sleepstage_nssa.csv'

                df_sliced.to_csv(os.path.join(
                    save_path, new_name), index=False)
                # matched_subject_ids.append(subject_id)

                # print('Not empty')


# print('done processing')
