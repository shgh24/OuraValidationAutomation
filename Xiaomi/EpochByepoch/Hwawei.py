import pandas as pd
import os
import glob as glob
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


df_subj_list = pd.concat([df1, df2])


data_dir = '/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/Zepplife/Zepp_Life.xlsx'

sheet_names = ['SR1', 'SR2', 'SR3', 'SR4']
df_combined = pd.DataFrame(columns=['Date', 'ID', 'Stage'])


for sheet_name in sheet_names:
    df = pd.read_excel(data_dir, sheet_name=sheet_name)

    # Reshape the DataFrame
    df_new = pd.DataFrame(columns=['Date', 'ID', 'Stage'])
    num_columns = len(df.columns)
    num_rows = len(df)

    for i in range(0, num_columns, 3):
        data_slice = df.iloc[:, i:i+3]
        data_slice.columns = ['Date', 'ID', 'Stage']
        df_new = pd.concat([df_new, data_slice])

    # Reset the index
    df_new.reset_index(drop=True, inplace=True)
    data = df_new.dropna(how='all')
    data.reset_index(drop=True, inplace=True)

    ind = data[data['ID'].notna() & data['ID'].str.contains('NUS')].index
    data['NUS_ID'] = ''

    for i in range(len(ind)-1):
        start_idx = ind[i]
        end_idx = ind[i+1]
        nus_id = data.loc[start_idx, 'ID']
        data.loc[start_idx:end_idx-1, 'NUS_ID'] = nus_id

        match_id = df_subj_list[df_subj_list["Participant ID"].str.contains(
            nus_id[0:-3]) & (df_subj_list['Night'] == int(nus_id[-1]))]
        end_date = match_id['Session end date'].iloc[0]

    # Fill the last segment
    nus_id = data.loc[ind[-1], 'ID']
    data.loc[ind[-1]:, 'NUS_ID'] = nus_id

    # Append the processed data to the combined DataFrame
    df_combined = pd.concat([df_combined, data])

# Reset the index of the combined DataFrame
df_combined.reset_index(drop=True, inplace=True)

df_combined = df_combined.dropna(subset=['Stage'])
df_combined.reset_index(drop=True, inplace=True)


df_combined = df_combined.rename(
    columns={"Date": "start_stage", "ID": "end_stage"})

df_combined.to_csv(data_dir.replace(
    'Zepp_Life.xlsx', 'Zepp_Life_processed.csv'))

# Print the final combined DataFrame
print(df_combined)


print('done')


################################################################

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

df_subj_list = pd.concat([df1, df2])

data_dir = '/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/Zepplife/Zepp_Life.xlsx'

sheet_names = ['SR1', 'SR2', 'SR3', 'SR4']
df_combined = pd.DataFrame(
    columns=['Date', 'ID', 'Stage', 'Start Date', 'End Date'])

for sheet_name in sheet_names:
    df = pd.read_excel(data_dir, sheet_name=sheet_name)

    # Reshape the DataFrame
    df_new = pd.DataFrame(columns=['Date', 'ID', 'Stage'])
    num_columns = len(df.columns)
    num_rows = len(df)

    for i in range(0, num_columns, 3):
        data_slice = df.iloc[:, i:i+3]
        data_slice.columns = ['Date', 'ID', 'Stage']
        df_new = pd.concat([df_new, data_slice])

    # Reset the index
    df_new.reset_index(drop=True, inplace=True)
    data = df_new.dropna(how='all')
    data.reset_index(drop=True, inplace=True)

    ind = data[data['ID'].notna() & data['ID'].str.contains('NUS')].index
    data['NUS_ID'] = ''

    for i in range(len(ind)-1):
        start_idx = ind[i]
        end_idx = ind[i+1]
        nus_id = data.loc[start_idx, 'ID']
        data.loc[start_idx:end_idx-1, 'NUS_ID'] = nus_id

        match_id = df_subj_list[df_subj_list["Participant ID"].str.contains(
            nus_id[0:-3]) & (df_subj_list['Night'] == int(nus_id[-1]))]
Apologies for the incomplete response. Here's the continuation of the code snippet:

```python
        end_date = match_id['Session end date'].iloc[0]
        start_date = end_date - \
            pd.DateOffset(days=len(data[start_idx:end_idx-1]))

        data.loc[start_idx:end_idx-1, 'Start Date'] = start_date
        data.loc[start_idx:end_idx-1, 'End Date'] = end_date

    # Fill the last segment
    nus_id = data.loc[ind[-1], 'ID']
    data.loc[ind[-1]:, 'NUS_ID'] = nus_id

    match_id = df_subj_list[df_subj_list["Participant ID"].str.contains(
        nus_id[0:-3]) & (df_subj_list['Night'] == int(nus_id[-1]))]
    end_date = match_id['Session end date'].iloc[0]
    start_date = end_date - pd.DateOffset(days=len(data[ind[-1]:]))

    data.loc[ind[-1]:, 'Start Date'] = start_date
    data.loc[ind[-1]:, 'End Date'] = end_date

    # Append the processed data to the combined DataFrame
    df_combined = pd.concat([df_combined, data])

# Reset the index of the combined DataFrame
df_combined.reset_index(drop=True, inplace=True)

df_combined = df_combined.dropna(subset=['Stage'])
df_combined.reset_index(drop=True, inplace=True)

df_combined = df_combined.rename(
    columns={"Date": "start_stage", "ID": "end_stage"})

df_combined.to_csv(data_dir.replace(
    'Zepp_Life.xlsx', 'Zepp_Life_processed.csv'))

# Print the final combined DataFrame
print(df_combined)

print('done')
