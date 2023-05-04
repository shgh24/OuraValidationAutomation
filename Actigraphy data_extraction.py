import pandas as pd
import numpy as np
import csv
import glob as glob

file = '/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/Actigraph/CSV/NUS3001/NUS3001_gt3x_epochs.csv'


dir_path = "/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/Actigraph/CSV"

# folders = next(os.walk(dir_path))[1]
folders = glob.glob(dir_path+'/NUS*/NUS*.csv')
# 2023-03-09T23-30-56_19cfb704-83e3-40af-92d2-75fa740027d2
# iterate over all folders in the directory
for folder in folders:

    # extract the recording ID
    parts = folder.split("_")
    id_str = parts[0]

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
    sleep_periods_indices = [0] + sleep_periods_indices + [len(lines)]
    # Split the list of lines into separate lists for each "Sleep Period"
    sleep_periods = []
    for i in range(len(sleep_periods_indices) - 1):
        start_index = sleep_periods_indices[i]
        end_index = sleep_periods_indices[i + 1]
        sleep_period = lines[start_index:end_index]
        sleep_periods.append(sleep_period)

    if match_id:
        dest_dir = "/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/Dreem_Raw/"

        current_folder = os.path.join(dir_path, folder)
        for hypno_file in glob.glob(os.path.join(current_folder, "*.txt")):
            # Scldreem_s01_2023-03-09T23-30-56[+0800]_hypnogram.txt
            parts = folder.split("_")
            file_date = parts[0]
            new_name = f'{match_id[0]}_{file_date}.txt'

            shutil.copy(hypno_file, os.path.join(dest_dir, new_name))
