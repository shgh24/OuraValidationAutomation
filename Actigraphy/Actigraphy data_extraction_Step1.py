import pandas as pd
import numpy as np
import csv
import glob as glob

# file = '/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/Actigraph/CSV/NUS3001/NUS3001_gt3x_epochs.csv'


dir_path = "/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/Actigraph/CSV"
saving_path = '/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/Sleep_Staging/Actigraphy/Raw'

# folders = next(os.walk(dir_path))[1]
folders = glob.glob(dir_path+'/NUS*/NUS*.csv')
# 2023-03-09T23-30-56_19cfb704-83e3-40af-92d2-75fa740027d2
# iterate over all folders in the directory
for folder in folders:

    # extract the recording ID
    parts = folder.split("/")
    id_str = parts[-1][0:7]

    # match the recording ID with subject ID
    # match_id = df[df["Recording ID"].str.contains(
    #     id_str)]["Subject ID"].tolist()

    header_row = None
    # Open the file and search for the header row
    source = folder
    with open(source, "r") as f:

        for i, line in enumerate(f):
            if (
                "Sleep Period" in line

            ):
                header_row = i
                break

    # Read the text file into a DataFrame, skipping the header rows
    # df_dreem = pd.read_csv(source, sep="\t", skiprows=header_row)


# Open the file and read its contents

    with open(source, "r") as f:
        reader = csv.reader(f)
        lines = [line for line in reader]

    # Find line numbers where "Sleep Period" appears
    sleep_periods_indices = [i for i, line in enumerate(
        lines) if "Sleep Period" in line]

    # Add the first and last line numbers to the list
    sleep_periods_indices = sleep_periods_indices
    sleep_periods_indices = sleep_periods_indices + [len(lines)]
    # sleep_periods_indices = [0] + sleep_periods_indices + [len(lines)]
    # Split the list of lines into separate lists for each "Sleep Period"
    # sleep_periods = []

    for i in range(len(sleep_periods_indices) - 1):

        start_index = sleep_periods_indices[i]+1
        end_index = sleep_periods_indices[i+1]-1
        sleep_period = lines[start_index:end_index]
        date_recorded = sleep_period[1][0].replace('/', '-')
        file_name = f'{saving_path }/{id_str}_{date_recorded}_N{i+1}_Actigraphy.csv'
        df_sleep = pd.DataFrame(sleep_period)
        # df_sleep.to_csv(file_name, index=False, header=False)
        epoch = df_sleep.iloc[1:, -1]
        epoch.replace({'W': 0, 'S': 1}, inplace=True)

        newdf = epoch.loc[epoch.index.repeat(2)].reset_index(drop=True)

        newdf.to_csv(file_name.replace('Raw', 'epoched'),
                     index=False, header=False)

    print('Fin')
