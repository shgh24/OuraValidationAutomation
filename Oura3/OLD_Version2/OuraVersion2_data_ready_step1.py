"""
The script designed to extract and organize scored sleep staging data from the Oura validation 3 study.
the script reads the staging data from a CSV file, which contains scores for the data collected in each sleep room across multiple nights. The CSV file serves as the input source for the script's data processing.
the script categorize the sleep data into different nights, subjects, and wrist indicators. This categorization ensures that the resulting output files adhere to a consistent and standardized format, similar to the first batch of data provided by Oura Ring.
(Oura Ring provided the 2nd and 3rd batch of data in the new format and that's why the script named OuraVersion2 and this scripts will generate new files in the format of first batch file as below:
A sample File from the first batch: "NUS3_003_NIGHT02_L_sleepstage_nssa.csv." In this file, we see data for a single night (Night 2) for user NUS3_003, captured from the left wrist. 
Each file contains data for one user only, not a mixture of different users' data based on the room number. )


Usage:
    python RAWdata_preparation_DeZambotti.py <NUS*.csv>

Dependencies:
    - pandas
    - numpy
    - os 
    -glob
"""
import csv
from datetime import datetime, timedelta
import os as os


def save_sleep_period_data(csv_file, files, save_path2):
    save_path = save_path2

    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row if present

        timestamp_data = list(reader)

    unique_days = set()
    for row in timestamp_data:
        timestamp = datetime.fromisoformat(row[0])
        day = timestamp.strftime("%Y-%m-%d")
        unique_days.add(day)

    for day in unique_days:
        sleep_start = datetime.fromisoformat(
            day).replace(hour=19, minute=0, second=0)
        sleep_end = (datetime.fromisoformat(day) + timedelta(days=1)
                     ).replace(hour=11, minute=0, second=0)

        sleep_period_data = []
        for row in timestamp_data:
            timestamp = datetime.fromisoformat(row[0]).replace(
                tzinfo=None)  # Convert to offset-naive datetime
            if sleep_start <= timestamp < sleep_end:
                sleep_period_data.append(row)

        if sleep_period_data:
            save_to_csv(day, sleep_period_data, files, save_path)


def save_to_csv(day, data, files, save_path):
    room_hand = files[0:7]
    start_rcrd = data[0][0]
    end_rcrd = data[-1][0]
    filename = f"{save_path}/{room_hand}_{start_rcrd}_{end_rcrd}_sleep_period_data.csv"
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp"])  # Header row
        writer.writerows(data)


# Usage example


csv_file = '/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/OURA3_Raw/NUS3_NSSA_hypnograms/ROOM1_L_528ce9f5-b7c6-4875-9f0a-50c1c01fd27e.csv'
# file_name = f'{path_save}/'

data_dir = '/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/OURA3_Raw/NUS3_NSSA_hypnograms'
save_path = '/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/OURA3_Raw/NUS3_NSSA_hypnograms/saved'

for files in [f for f in os.listdir(data_dir) if f.endswith(".csv")]:

    filename = f'{data_dir}/{files}'

    save_sleep_period_data(filename, files, save_path)
    print('done')
