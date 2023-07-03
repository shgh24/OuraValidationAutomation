import pandas as pd
import os
import glob as glob


HPB_raw_path = '/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/HPB/CSC_sleep_intervals.xlsx'

# reading the HPB file
data = pd.read_excel(HPB_raw_path)

print('done')
