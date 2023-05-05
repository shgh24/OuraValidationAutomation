import numpy as np
import pandas as pd
import os
import glob
# spurce_path=C:\Users\SCL\Desktop\TestUsleep
# tsv_files=glob.glob("C:\Users\SCL\Desktop\TestUsleep\*.tsv")
tsv_files = glob.glob(
    '/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/Domino_EDF/epoched/*.tsv')

# Read the TSV file into a DataFrame
for files in tsv_files:
    df = pd.read_csv(files, sep='\t')

    # Create an empty list to hold the new values
    new_col = []

    # Loop through each row in the DataFrame
    for index, row in df.iterrows():
        # Calculate the number of times to repeat the stage value
        repeat_count = int(row['duration_sec'] / 30)

        # Append the stage value to the new_col list the appropriate number of times
        new_col += [row['stage']] * repeat_count

    # Create a new DataFrame with the new_col list as the only column
    new_df = pd.DataFrame(new_col, columns=['stage_repeats'])

    # new_df.replace(to_replace=['Wake','N1','N2','N3','REM'], value=[0,1,2,3,5])
    mapping = {'N1': 1, 'N2': 2, 'N3': 3, 'REM': 5, 'Wake': 0}

    # new_df.replace({'stage_repeats': mapping})

    new_df.stage_repeats = [mapping[item] for item in new_df.stage_repeats]

    # Write the new DataFrame to a CSV file
    new_df.to_csv(files.replace(
        "_epoched_(1).tsv", "_sleepstage_Usleep.csv").replace('n1', 'N1').replace("n2", "N2"), index=False, header=False)
