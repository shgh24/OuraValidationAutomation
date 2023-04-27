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
sheet_key = "1fS9kNDh1DlJiyphvD_ZbpSERU282xsUPJmjx4iUtm4I"
sheet_name = "Devices/Session Tracking"

# Read the data from the Google Sheet
sheet = client.open_by_key(sheet_key).worksheet(sheet_name)
# data = sheet.get_all_values()
data = sheet.get_all_records()

# Convert the data to a pandas DataFrame
df = pd.DataFrame(data)

folders = "/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/Dreem_Raw/"
dir_path = '/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/Dreem_Raw'
# dest = os.path.join(folders.replace(
#     'Dreem_Raw', 'Dreem_processed'))
# dest="/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/Sleep_Staging/Dreem"

# for files in glob.glob(f'{folders}*txt'):
txt_files = [file for file in os.listdir(folders) if file.endswith('.txt')]

for files in txt_files:
    # extract the recording ID
    # NUS3001_N1.txt
    parts = files.split("_")
    id_str = parts[0].replace('3', '3_')

    date_str = parts[2][:10]
    time_str = parts[2][11:19]

    # match the recording ID with subject ID
    match_id = df[df["Participant ID"].str.contains(
        id_str) & (df['Night'] == int(parts[1][1]))]

    if not match_id.empty:
        dest = os.path.join(dir_path.replace(
            'Dreem_Raw', 'Dreem_processed'), files)

        lightOff = match_id.iloc[0]["Session start local time"]
        lightON = match_id.iloc[0]["Session end local time"]

        dt = datetime.strptime(f"{date_str}T{time_str}", "%Y-%m-%dT%H-%M-%S")
        # if the time is before 8 a.m., subtract one day from the date
        if dt.hour > 18:
            dt = dt + timedelta(days=1)

        # format the new date and time as strings
        session_End_date = dt.strftime("%Y-%m-%d")

        header_row = None
        # Open the file and search for the header row
        source = os.path.join(folders, files)
        with open(source, "r") as f:
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
        df_dreem = pd.read_csv(source, sep="\t", skiprows=header_row)
        # Convert the "Time [hh:mm:ss]" column to a timedeltas object
        timedeltas = pd.to_timedelta(df_dreem["Time [hh:mm:ss]"])

        # Round the timedeltas to the nearest 30 seconds

        rounded_timedeltas = pd.to_timedelta(
            (timedeltas.dt.total_seconds() / 30).round() * 30, unit="s"
        )

        # session_End_date = match_id.iloc[0]["Session end date"]
        base_date = pd.Timestamp(session_End_date)
        rounded_times = rounded_timedeltas.apply(
            lambda td: base_date - pd.Timedelta(days=1) + td
            if td.components.hours > 18
            else base_date + td
        )
        time = rounded_times

        df_dreem["Time [hh:mm:ss]"] = rounded_times
        # Convert lightOff and lightON to datetime objects
        lightOff = pd.Timestamp(lightOff)
        if lightOff.hour > 18:
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

        if (df_sliced.iloc[0]["Time [hh:mm:ss]"] > lightOff):
            # Calculate the number of zero value rows to add
            time_diff = df_sliced.iloc[0]["timestamp"] - lightOff

            num_rows = time_diff.total_seconds() / 60-.5

        # Create a DataFrame with zero value rows
            zero_df_LOFF = pd.DataFrame({'timestamp': pd.date_range(
                lightOff+pd.Timedelta(minutes=.5), periods=num_rows*2, freq="30S"), "predicted": 'SLEEP-S0'})

        # Concatenate the zero_df with df_sliced
            df_sliced = pd.concat([zero_df_LOFF, df_sliced], ignore_index=True)

    # If the end time is earlier than lightON, add a row with Sleep Stage = 0
    # if (df_sliced.iloc[-1][["timestamp"]] < lightON-pd.Timedelta(minutes=.5)).item():
    if (df_sliced.iloc[-1]["Time [hh:mm:ss]"] < lightON):
        time_diff_LONN = lightON-df_sliced.iloc[-1]["Time [hh:mm:ss]"]
        num_rows_LONN = time_diff_LONN.total_seconds() / 60 - .5

        # Create a DataFrame with zero value rows
        zero_df_LON = pd.DataFrame({"Time [hh:mm:ss]": pd.date_range(
            df_sliced.iloc[-1]["Time [hh:mm:ss]"]+pd.Timedelta(minutes=.5), periods=num_rows_LONN*2, freq="30S"), "predicted": 'SLEEP-S0'})
        df_sliced = pd.concat([df_sliced, zero_df_LON], ignore_index=True)

        # If the start time is later than lightOff, add a row with Sleep Stage = 0
        # if df_sliced.iloc[0]["Time [hh:mm:ss]"] > lightOff:
        #     new_row = {"Time [hh:mm:ss]": lightOff, "Sleep Stage": 0}
        #     df_sliced = pd.concat(
        #         [pd.DataFrame([new_row]), df_sliced], ignore_index=True
        #     )

        # # If the end time is earlier than lightON, add a row with Sleep Stage = 0
        # if df_sliced.iloc[-1]["Time [hh:mm:ss]"] < lightON - pd.Timedelta(minutes=0.5):
        #     new_row = {"Time [hh:mm:ss]": lightON, "Sleep Stage": 0}
        #     df_sliced = pd.concat(
        #         [df_sliced, pd.DataFrame([new_row])], ignore_index=True
        #     )

        def dreemMapping(df_sliced, lightOff, lightON):
            dreemdic = {
                "SLEEP-REM": 5,
                "SLEEP-S0": 0,
                "SLEEP-S1": 1,
                "SLEEP-S2": 2,
                "SLEEP-S3": 3,
                "SLEEP-MT": 7,
            }

            # Map the sleep stages to integers using the first dictionary
            df_sliced["sleep stage"] = df_sliced["Event"].map(
                dreemdic
            )

            return df_sliced

        df_mapped = dreemMapping(df_sliced, lightOff, lightON)
        df_mapped[["Time [hh:mm:ss]", "Event", "sleep stage"]].to_csv(
            dest.replace(
                ".txt", "_sleepstage_Dreem_Mapped.csv"
            ),
            sep=",",
        )
        df_sliced['sleep stage'].to_csv(dest.replace(
            'Dreem_processed', 'Dreem_cleaned').replace('txt', 'csv'), header=False, index=False)

    else:
        print(f"No match found for file {files}")


# Clean the dataset
# You can perform any cleaning operation here based on your requirements

print("Chopped datas dataset saved to Dreem_cleaned ")
