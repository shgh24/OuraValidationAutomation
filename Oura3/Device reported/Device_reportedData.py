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

    participant = df_Oura["name"][0]
    match = df[(df['Night'] == int(participant[-3]))
               & (df['Participant ID'] == participant[:-10])]

    # Mapp Oura

    OuraMapping = {
        'REM': 5,
        'WAKE': 0,
        'LIGHT': 1,
        'DEEP': 3

    }

    df_Oura['predicted'] = df_Oura['predicted'].map(OuraMapping)

    # /Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/Sleep_Staging/Oura3
    df_Oura['predicted'].to_csv(files.replace(
        '_nssa.csv', '_nssa_clean.csv').replace('S3_', 'S3').replace('NIGHT', 'N').replace('OURA3_Raw', 'Sleep_Staging/Oura3/DeviceOnly'), index=False, header=False)


################################################################


outliers_cut_end = ['NUS3010_N1', 'NUS3020_N2']
outlier_cut_start = []

# Subject NUS3001 has participated in study twice because the first time recording was spoiled (NUS3101 is the new recording ID in his second attempt)
# Subject 3035 dropped out after first time recording N1
outlier = ['NUS3001_N1', 'NUS3035_N1', 'NUS3001_N2']
# outlier = ['NUS3021_N1', 'NUS3007_N1', 'NUS3001_N2']

today = datetime.now().strftime("%Y_%m_%d")


staging_file_path = "/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/Sleep_Staging"
Saving_file_path = "/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/analysis/DeZambotti/Oura3/Data/DeviceOnly"

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
                staging_file_path, "Oura3/DeviceOnly", f"NUS*{Night}*{hand}*.csv"))

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

                        # Sanity check
                        # Check if the data lengths are the same
                        if subject_id not in outlier:

                            # # write the current line to the file with a newline character

                            combined_data = pd.DataFrame(
                                data=[subject1]*len(df_Oura), columns=['subject'])

                            #epochs = np.arange(len(df_PSG))+1
                            combined_data['epoch'] = np.arange(len(df_Oura))+1
                            combined_data['reference'] = df_Oura
                            combined_data['device'] = df_Oura

                            # combined_data_AllDays = pd.concat(combined_data_AllDays,combined_data)
                            combined_data_AllDays = pd.concat(
                                [combined_data_AllDays, combined_data], ignore_index=True)

            combined_data_AllDays.to_csv(os.path.join(Saving_file_path,
                                                      f"combined_data_{Night}_{hand}_{today}.csv"), index=False)
