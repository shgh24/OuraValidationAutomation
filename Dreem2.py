import os
import pandas as pd
from datetime import datetime, timedelta
import shutil
import glob
import mne
import gspread
from google.oauth2 import service_account


scope = ["https://www.googleapis.com/auth/spreadsheets"]
creds = service_account.Credentials.from_service_account_file(
    "api-access-381407-51bd2bb2d008.json", scopes=scope
)
client = gspread.authorize(creds)


# Replace this with your Google Sheet key
# Replace this with your Google Sheet key
with open('/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/analysis/DeZambotti/sheet_key.txt') as f:
    contents = f.readlines()
sheet_key = contents[0]
sheet_name = 'Devices/Session Tracking'

# Read the data from the Google Sheet
sheet = client.open_by_key(sheet_key).worksheet(sheet_name)
# data = sheet.get_all_values()
data = sheet.get_all_records()

# Convert the data to a pandas DataFrame
df_gs = pd.DataFrame(data)


df = pd.read_csv(
    "/Volumes/CSC5/SleepCognitionLab/Tera2b/DREEM_database/DREEMER/DPD_OuraValidation3/OuraValidation3_dataoverview.csv"
)
# data = sheet.get_all_records()

# # Convert the data to a pandas DataFrame
# df = pd.DataFrame(data)

# specify the path to the directory containing the dreem raw files(downloaded from web dashboard)
dir_path = "/Volumes/CSC5/SleepCognitionLab/Tera2b/DREEM_database/DREEMER/DPD_OuraValidation3/Data"
# create a dictionary to map room numbers to session IDs
# room_to_session = {"s01": 1, "s02": 2, "s05": 3, "s06": 4}
folders = next(os.walk(dir_path))[1]
# iterate over all files in the directory
for file in folders:
    # check if the file is a hypnogram file
    # if file.endswith("_hypnogram.txt"):
    # extract the participant ID and session date from the file name
    parts = file.split("_")
    # date_str = parts[2][:10]
    id_str = parts[1]
    # match the recording ID with subject ID
    match_id = df[df["Recording ID"].str.contains(
        id_str)]["Subject ID"].tolist()

    if match_id:
        # os.cp()

        dest_dir = "/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/Dreem_Raw/"
        new_name = match_id

        current_file_name = os.path.join(dir_path, file)
        # "/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/Dreem_Raw/Data_Shohreh/bar.txt"
        for hypno_file in glob.glob(os.path.join(current_file_name, "*.txt")):
            shutil.copy(hypno_file, os.path.join(
                dest_dir, f'{new_name[0]}.txt'))

        # In this section of the script we chopp the dreem data to lights on lights off data and will map the stages to the standatd sleep stages to match it with PSG
        parts_name = new_name[0].split("_")
        match = df_gs[
            (df_gs["Participant ID"].str.replace("_", "") == parts_name[0])
            & (df_gs["Night"] == int(parts_name[1][-1]))
        ]

        lightOff = match.iloc[0]["Session start local time"]
        lightON = match.iloc[0]["Session end local time"]

        header_row = None
        # Open the file and search for the header row
        with open(hypno_file, "r") as f:
            # date_recorded = f.readlines()[3][-9:-1]
            for i, line in enumerate(f):
                if (
                    "Sleep Stage" in line
                    and "Time [hh:mm:ss]" in line
                    and "Event" in line
                    and "Duration[s]" in line
                ):
                    header_row = i
                    break

        # Read the text file into a DataFrame, skipping the header rows
        df_dreem = pd.read_csv(hypno_file, sep="\t", skiprows=header_row)
        # Convert the "Time [hh:mm:ss]" column to a timedeltas object
        timedeltas = pd.to_timedelta(df_dreem["Time [hh:mm:ss]"])

        # Round the timedeltas to the nearest 30 seconds

        rounded_timedeltas = pd.to_timedelta(
            (timedeltas.dt.total_seconds() / 30).round() * 30, unit="s"
        )

        # rounded_times = rounded_timedeltas.apply(
        #     lambda td: pd.Timestamp(0) + td)

        base_date = pd.Timestamp(session_End_date)
        rounded_times = rounded_timedeltas.apply(
            lambda td: base_date - pd.Timedelta(days=1) + td
            if td.components.hours > 20
            else base_date + td
        )
        time = rounded_times

        df_dreem["Time [hh:mm:ss]"] = rounded_times
        # Convert lightOff and lightON to datetime objects
        lightOff = pd.Timestamp(lightOff)
        if lightOff.hour > 20:
            lightOff_day = base_date - pd.Timedelta(days=1)
            lightOff = lightOff.replace(
                year=lightOff_day.year,
                month=lightOff_day.month,
                day=lightOff_day.day,
            )
        else:
            lightOff = lightOff.replace(
                year=base_date.year, month=base_date.month, day=base_date.day
            )
        lightON = pd.Timestamp(lightON).replace(
            year=base_date.year, month=base_date.month, day=base_date.day
        )
        # df_dreem["Time [hh:mm:ss]"] = pd.to_datetime(
        #     df_dreem["Time [hh:mm:ss]"])

        # Slice the df DataFrame based on the Time column
        # Take note that we assumed that dreem first epoch is labeled based on press button sec +it's consequtive 30 sec, since dreem at least needs 30sec of data to get the sleep stage
        # so we cut dreem signal to the >=lights Off to < lights on
        df_sliced = df_dreem.loc[
            (df_dreem["Time [hh:mm:ss]"] >= lightOff)
            & (df_dreem["Time [hh:mm:ss]"] < lightON)
        ]

        # If the start time is later than lightOff, add a row with Sleep Stage = 0
        if df_sliced.iloc[0]["Time [hh:mm:ss]"] > lightOff:
            new_row = {"Time [hh:mm:ss]": lightOff, "Sleep Stage": 0}
            df_sliced = pd.concat(
                [pd.DataFrame([new_row]), df_sliced], ignore_index=True
            )

        # If the end time is earlier than lightON, add a row with Sleep Stage = 0
        if df_sliced.iloc[-1]["Time [hh:mm:ss]"] < lightON - pd.Timedelta(minutes=0.5):
            new_row = {"Time [hh:mm:ss]": lightON, "Sleep Stage": 0}
            df_sliced = pd.concat(
                [df_sliced, pd.DataFrame([new_row])], ignore_index=True
            )

        def dreemMapping(df_sliced, lightOff, lightON):
            dreemdic = {
                "SLEEP-REM": 5,
                "SLEEP-S0": 0,
                "SLEEP-S1": 1,
                "SLEEP-S2": 2,
                "SLEEP-S3": 3,
                "SLEEP-MT": 7,
            }

            dreemdic_MTtoWake = {
                "SLEEP-REM": 5,
                "SLEEP-S0": 0,
                "SLEEP-S1": 1,
                "SLEEP-S2": 2,
                "SLEEP-S3": 3,
                "SLEEP-MT": 0,
            }

            sleeplen = (df_sliced.shape[0]) / 2
            first10percSleep = lightOff + pd.Timedelta(minutes=sleeplen / 10)
            last10percentSleep = lightOff + \
                pd.Timedelta(minutes=sleeplen * 9 / 10)

            # Map the sleep stages to integers using the first dictionary
            df_sliced.loc[
                (df_sliced["Time [hh:mm:ss]"] > first10percSleep)
                & (df_sliced["Time [hh:mm:ss]"] < last10percentSleep),
                "sleep stage",
            ] = df_sliced.loc[
                (df_sliced["Time [hh:mm:ss]"] > first10percSleep)
                & (df_sliced["Time [hh:mm:ss]"] < last10percentSleep),
                "Event",
            ].map(
                dreemdic
            )

            df_sliced.loc[
                (df_sliced["Time [hh:mm:ss]"] < first10percSleep)
                | (df_sliced["Time [hh:mm:ss]"] > last10percentSleep),
                "sleep stage",
            ] = df_sliced.loc[
                (df_sliced["Time [hh:mm:ss]"] < first10percSleep)
                | (df_sliced["Time [hh:mm:ss]"] > last10percentSleep),
                "Event",
            ].map(
                dreemdic_MTtoWake
            )
            return df_sliced

        df_mapped = dreemMapping(df_sliced, lightOff, lightON)
        df_mapped.to_csv(
            dest.replace("sleepstage_Dreem", "sleepstage_Dreem_Mapped").replace(
                "txt", "csv"
            ),
            sep=",",
        )
        df_sliced["sleep stage"].to_csv(
            dest.replace("Dreem_processed", "Dreem_cleaned").replace(
                "txt", "csv"),
            header=False,
            index=False,
        )

    else:
        print(f"No match found for file {file}")


# Clean the dataset
# You can perform any cleaning operation here based on your requirements

print("Chopped datas dataset saved to Dreem_cleaned ")
