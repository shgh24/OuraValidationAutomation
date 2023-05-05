import mne
import os
import pandas as pd
import gspread
from google.oauth2 import service_account
from datetime import datetime, timedelta
import shutil
import glob
from datetime import datetime
import pytz
from pytz import timezone
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
df = pd.DataFrame(data)

# specify the path to the directory containing the dreem raw files(downloaded from web dashboard)
dir_path = '/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/Zepplife/ExtractedFiles'
dir_path_folders = os.listdir(dir_path)

# Humei_finaldata = pd.DataFrame()
Humei_cleaned_list = []
Humei_cleaned_list_LOn_LOff = []

for path in glob.glob(f'{dir_path}/*/SLEEP*'):
    Humei_cleaned = pd.DataFrame()
    # print(path)
    file_path = glob.glob(f'{path}/*.csv')
    humei_data = pd.read_csv(file_path[0], usecols=[
                             i for i in range(7)])
    # X = df.loc['Session end date']
    # Y = df.loc['Room #']
    roomNo = int(path[-1])
    # wakeUp_time = humei_data['stop']
    dt_stop = humei_data['stop'].apply(
        lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S%z'))

    dt_SG_stop = dt_stop.apply(lambda x: x.astimezone(
        timezone('Asia/Shanghai')).strftime('%Y-%m-%dT%H:%M:%S%z'))

    dt_start = humei_data['start'].apply(
        lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S%z'))

    dt_SG_start = dt_start.apply(lambda x: x.astimezone(
        timezone('Asia/Shanghai')).strftime('%Y-%m-%dT%H:%M:%S%z'))

    humei_data['stop'] = dt_SG_stop
    humei_data['start'] = dt_SG_start
    # humei_data['stop'] = dt_SG_stop.apply(lambda x: x.split('T')[0])
    humei_data['stop_date'] = dt_SG_stop.apply(lambda x: x.split('T')[0])

    df['Session end date'] = pd.to_datetime(
        df['Session end date'], format='%Y-%m-%d')

    for index, row in humei_data.iterrows():
        match = df[(df['Room #'] == roomNo)
                   & (row['stop_date'] == df['Session end date'])]
        # print(match)

        if not match.empty:
            Humei_cleaned = row
            Humei_cleaned.loc['Subject'] = match["Participant ID"].iloc[0].replace(
                '_', '')
            Humei_cleaned.loc['Night'] = int(match["Night"].iloc[0])
            Humei_cleaned_list.append(Humei_cleaned)

            # get the lIghts on and Lights of the PSG and check if Humei data recorded between Lights On and Lights Off
            lightOff = match.iloc[0]['Session start local time']
            lightON = match.iloc[0]['Session end local time']

            lightOff = pd.Timestamp(lightOff)
            base_date = pd.Timestamp(match.iloc[0]['Session end date'])
            if lightOff.hour > 19:
                lightOff_day = base_date - pd.Timedelta(days=1)
                lightOff = lightOff.replace(year=lightOff_day.year,
                                            month=lightOff_day.month, day=lightOff_day.day).tz_localize(pytz.timezone('Asia/Shanghai'))
            else:
                lightOff = lightOff.replace(year=base_date.year,
                                            month=base_date.month, day=base_date.day).tz_localize(pytz.timezone('Asia/Shanghai'))
            lightON = pd.Timestamp(lightON).replace(
                year=base_date.year, month=base_date.month, day=base_date.day).tz_localize(pytz.timezone('Asia/Shanghai'))

            TIB = pd.Timestamp(
                row['stop'])-pd.Timestamp(row['start'])
            TIB_s = pd.Series({'TIB': TIB.total_seconds()/60})
            # Humei_cleaned = pd.concat([Humei_cleaned, TIB_s], axis=1)
            Humei_cleaned = pd.concat([TIB_s, Humei_cleaned])

            if (pd.Timestamp(row['start']) >= lightOff and pd.Timestamp(row['stop']) <= lightON):

                Humei_cleaned_list_LOn_LOff.append(Humei_cleaned)


df_Humei_LON_LOff = pd.DataFrame(Humei_cleaned_list_LOn_LOff)
df_Humei_LON_LOff = df_Humei_LON_LOff.reset_index(drop=True)

df_Humei_LON_LOff = df_Humei_LON_LOff[(df_Humei_LON_LOff['REMTime'] != 0) & (
    df_Humei_LON_LOff['shallowSleepTime'] != 0) & (df_Humei_LON_LOff['deepSleepTime'] != 0)]

cols = list(df_Humei_LON_LOff)
cols = cols[-2:] + cols[0:-2]
df_Humei_LON_LOff = df_Humei_LON_LOff[cols]
df_Humei_LON_LOff.to_csv(os.path.join(
    dir_path, 'Humei_Data_LihtsOn_lightsOff_v1.csv'), index=False)


# the whole dataset that does not exclude any recorded data
df_humei = pd.DataFrame(Humei_cleaned_list)
df_humei = df_humei.reset_index(drop=True)
df_humei = df_humei[(df_humei['REMTime'] != 0) & (
    df_humei['shallowSleepTime'] != 0) & (df_humei['deepSleepTime'] != 0)]
cols = list(df_humei)
cols = cols[-2:] + cols[0:-2]
df_humei = df_humei[cols]
df_humei.to_csv(os.path.join(
    dir_path, 'Humei_Data_Allincluded_v1.csv'), index=False)

# cleaning Humei data before processing it
# we keep the data points that recoding ON and off happens inside the Lights On and Off


print('done with data')
