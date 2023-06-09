import pandas as pd
import numpy as np
import glob
import os as os

# Get the Oura subjects in each night and Hand
Saving_file_path = '/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/analysis/DeZambotti/Oura3/Data/May_10_2023'
Saving_file_path = '/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/analysis/DeZambotti/Oura3/Data/EBE/Common_epochs/Common_Subj_N1_Nodreem'
# "/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/analysis/DeZambotti/Oura3/Data/combined_data_N01_L_2023_05_10.csv"
fi = glob.glob(Saving_file_path+'/**.csv')
# Subjects = pd.DataFrame()
for files in fi:
    Subjects = pd.DataFrame()

    data = pd.read_csv(files)

    Subjects['subj'] = data["subject"].unique()
    Subjects.to_csv(files.replace('combined_data',
                    'SubjectID').replace('', ''), index=False)
