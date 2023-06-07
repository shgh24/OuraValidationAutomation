

import csv
from datetime import datetime
import csv
from datetime import datetime, timedelta
import os as os
import numpy as np


def save_sleep_period_data(csv_file, files, save_path2):
    save_path = save_path2

    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row if present

        timestamp_data = list(reader)

    unique_days = {}
    for row in timestamp_data:
        timestamp = datetime.fromisoformat(row[1])
        day = timestamp.strftime("%Y-%m-%d")

        if day not in unique_days:
            unique_days[day] = {'first': timestamp, 'last': timestamp}
        else:
            if timestamp < unique_days[day]['first']:
                unique_days[day]['first'] = timestamp
            if timestamp > unique_days[day]['last']:
                unique_days[day]['last'] = timestamp

    # Printing the first and last timestamps for each unique day
    for day, timestamps in unique_days.items():
        print(f"Day: {day}")
        print(f"First Timestamp: {timestamps['first']}")
        print(f"Last Timestamp: {timestamps['last']}")
        print()


csv_file = '/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/OURA3_Raw/NUS3_NSSA_hypnograms/ROOM1_L_528ce9f5-b7c6-4875-9f0a-50c1c01fd27e.csv'
data_dir = '/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/OURA3_Raw/NUS3_NSSA_hypnograms_21March-31May'

save_path = '/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/OURA3_Raw/NUS3_NSSA_hypnograms_21March-31May/Fisrt_process'


for files in [f for f in os.listdir(data_dir) if f.endswith(".csv")]:

    filename = f'{data_dir}/{files}'

    save_sleep_period_data(filename, files, save_path)
    print('done')
