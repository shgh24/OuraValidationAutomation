import mne
import os
import pandas as pd
import gspread
from google.oauth2 import service_account
from datetime import datetime, timedelta
import shutil


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

# specify the path to the directory containing the dreem raw files(downloaded from web dashboard)
dir_path = '/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/Dreem_Raw'
# create a dictionary to map room numbers to session IDs
room_to_session = {'s01': 1, 's02': 2, 's05': 3,  's06': 4}

# iterate over all files in the directory
for file in os.listdir(dir_path):
    # check if the file is a hypnogram file
    if file.endswith('_hypnogram.txt'):
        # extract the participant ID and session date from the file name
        parts = file.split('_')
        date_str = parts[2][:10]
        time_str = parts[2][11:19]

        # part_date = parts[2].split('T')
        session_id = room_to_session[parts[1]]

        dt = datetime.strptime(f"{date_str}T{time_str}", "%Y-%m-%dT%H-%M-%S")

       # if the time is before 8 a.m., subtract one day from the date
        if dt.hour > 20:
            dt = dt + timedelta(days=1)

        # format the new date and time as strings
        session_End_date = dt.strftime("%Y-%m-%d")

        #session_end_date_time = dt.strftime("%Y-%m-%d %H:%M:%S")

        # find the matching row in the DataFrame based on the session date and ID

        match = df[(df['Session end date'] == session_End_date)
                   & (df['Room #'] == session_id)]
        if len(match) == 2 and match.loc[:, 'Participant ID'].nunique() == 1:
            # print the participant ID for the matching row
            participant_id = match.iloc[0]['Participant ID']
            # Source file path
            source = os.path.join(dir_path, file)
            # destination file path
            file_name = f"{participant_id.replace('_', '')}_N{int(match.iloc[0]['Night']):d}_sleepstage_Dreem.txt"
            dest = os.path.join(dir_path.replace(
                'Dreem_Raw', 'Dreem_processed'), file_name)

            #shutil.copy2(source, dest)

            # In this section of the script we chopp the dreem data to lights on lights off data and will map the stages to the standatd sleep stages to match it with PSG

            lightOff = match.iloc[0]['Session start local time']
            lightON = match.iloc[0]['Session end local time']

            header_row = None
            # Open the file and search for the header row
            with open(source, "r") as f:
                #date_recorded = f.readlines()[3][-9:-1]
                for i, line in enumerate(f):
                    if "Sleep Stage" in line and "Time [hh:mm:ss]" in line and "Event" in line and "Duration[s]" in line:
                        header_row = i
                        break

            # Read the text file into a DataFrame, skipping the header rows
            df_dreem = pd.read_csv(source, sep="\t", skiprows=header_row)
            # Convert the "Time [hh:mm:ss]" column to a timedeltas object
            timedeltas = pd.to_timedelta(df_dreem["Time [hh:mm:ss]"])

            # Round the timedeltas to the nearest 30 seconds

            rounded_timedeltas = pd.to_timedelta(
                (timedeltas.dt.total_seconds() / 30).round() * 30, unit='s')

            # rounded_times = rounded_timedeltas.apply(
            #     lambda td: pd.Timestamp(0) + td)

            base_date = pd.Timestamp(session_End_date)
            rounded_times = rounded_timedeltas.apply(
                lambda td: base_date - pd.Timedelta(days=1) + td if td.components.hours > 20 else base_date + td)
            time = rounded_times

            df_dreem["Time [hh:mm:ss]"] = rounded_times
            # Convert lightOff and lightON to datetime objects
            lightOff = pd.Timestamp(lightOff)
            if lightOff.hour > 20:
                lightOff_day = base_date - pd.Timedelta(days=1)
                lightOff = lightOff.replace(year=lightOff_day.year,
                                            month=lightOff_day.month, day=lightOff_day.day)
            else:
                lightOff = lightOff.replace(year=base_date.year,
                                            month=base_date.month, day=base_date.day)
            lightON = pd.Timestamp(lightON).replace(
                year=base_date.year, month=base_date.month, day=base_date.day)
            # df_dreem["Time [hh:mm:ss]"] = pd.to_datetime(
            #     df_dreem["Time [hh:mm:ss]"])

            # Slice the df DataFrame based on the Time column
            # Take note that we assumed that dreem first epoch is labeled based on press button sec +it's consequtive 30 sec, since dreem at least needs 30sec of data to get the sleep stage
            # so we cut dreem signal to the >=lights Off to < lights on
            df_sliced = df_dreem.loc[(df_dreem["Time [hh:mm:ss]"] >= lightOff) &
                                     (df_dreem["Time [hh:mm:ss]"] < lightON)]

            # If the start time is later than lightOff, add a row with Sleep Stage = 0
            if df_sliced.iloc[0]["Time [hh:mm:ss]"] > lightOff:
                new_row = {"Time [hh:mm:ss]": lightOff, "Sleep Stage": 0}
                df_sliced = pd.concat(
                    [pd.DataFrame([new_row]), df_sliced], ignore_index=True)

            # If the end time is earlier than lightON, add a row with Sleep Stage = 0
            if df_sliced.iloc[-1]["Time [hh:mm:ss]"] < lightON-pd.Timedelta(minutes=.5):
                new_row = {"Time [hh:mm:ss]": lightON, "Sleep Stage": 0}
                df_sliced = pd.concat(
                    [df_sliced, pd.DataFrame([new_row])], ignore_index=True)

            def dreemMapping(df_sliced, lightOff, lightON):
                dreemdic = {
                    'SLEEP-REM': 5,
                    'SLEEP-S0': 0,
                    'SLEEP-S1': 1,
                    'SLEEP-S2': 2,
                    'SLEEP-S3': 3,
                    'SLEEP-MT': 7
                }

                dreemdic_MTtoWake = {
                    'SLEEP-REM': 5,
                    'SLEEP-S0': 0,
                    'SLEEP-S1': 1,
                    'SLEEP-S2': 2,
                    'SLEEP-S3': 3,
                    'SLEEP-MT': 0
                }

                sleeplen = (df_sliced.shape[0])/2
                first10percSleep = lightOff+pd.Timedelta(minutes=sleeplen/10)
                last10percentSleep = lightOff + \
                    pd.Timedelta(minutes=sleeplen*9/10)

                # Map the sleep stages to integers using the first dictionary
                df_sliced.loc[(df_sliced["Time [hh:mm:ss]"] > first10percSleep) &
                              (df_sliced["Time [hh:mm:ss]"] < last10percentSleep), "sleep stage"] = \
                    df_sliced.loc[(df_sliced["Time [hh:mm:ss]"] > first10percSleep) &
                                  (df_sliced["Time [hh:mm:ss]"] < last10percentSleep), "Event"].map(dreemdic)

                df_sliced.loc[(df_sliced["Time [hh:mm:ss]"] < first10percSleep) |
                              (df_sliced["Time [hh:mm:ss]"] > last10percentSleep), "sleep stage"] = \
                    df_sliced.loc[(df_sliced["Time [hh:mm:ss]"] < first10percSleep) |
                                  (df_sliced["Time [hh:mm:ss]"] > last10percentSleep), "Event"].map(dreemdic_MTtoWake)
                return df_sliced

            df_mapped = dreemMapping(df_sliced, lightOff, lightON)
            df_mapped.to_csv(dest.replace(
                'sleepstage_Dreem', 'sleepstage_Dreem_Mapped').replace('txt', 'csv'), sep=',')
            df_sliced['sleep stage'].to_csv(dest.replace(
                'Dreem_processed', 'Dreem_cleaned').replace('txt', 'csv'), header=False, index=False)

        else:
            print(f"No match found for file {file}")


# Clean the dataset
# You can perform any cleaning operation here based on your requirements

print("Chopped datas dataset saved to Dreem_cleaned ")
