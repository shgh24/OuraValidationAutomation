
import os as os
import glob
import numpy as np
import pandas as pd
import os

file = '/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/analysis/DeZambotti/Subjects_For_FinalAnalysis.xlsx'
# '/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/analysis/DeZambotti/Subjects_For\ FinalAnalysis.xlsx'
subj_N1_All = pd.read_excel(file, sheet_name='N1_All')
subj_N1_NoDreem = pd.read_excel(file, sheet_name='N1_NoDreem')
subj_N2_All = pd.read_excel(file, sheet_name='N2')
print('done')

devices = ['FB', 'Dreem', 'Oura3', 'Acti']
devices = ['Acti']
# Saving_file_path = f'/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/analysis/DeZambotti/{devi}/Common_Subj_N1'
#
for devi in devices:
    # Get the Oura subjects in each night and Hand
    data_dir = f'/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/analysis/DeZambotti/{devi}/Data/June_13_2023'

    # /Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/analysis/DeZambotti/Dreem/Common_Subj_N1
    # "/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/analysis/DeZambotti/Oura3/Data/combined_data_N01_L_2023_05_10.csv"
    fi = glob.glob(data_dir + '/combined*N1*.csv')
    # Subjects = pd.DataFrame()
    for files in fi:
        Subjects = pd.DataFrame()

        data = pd.read_csv(files)
        df1 = data
        # df2 = subj_N1_All
        df2 = subj_N1_NoDreem

        new_df = df1[df1['subject'].isin(df2['ID'])]

        new_df.to_csv(files.replace('Data/June_13_2023',
                      'Common_Subj_N1_Nodreem'), index=False)

        # new_df.to_csv(files.replace('Data/June_13_2023',
        #               'Common_Subj_N1'), index=False)


print('done')
