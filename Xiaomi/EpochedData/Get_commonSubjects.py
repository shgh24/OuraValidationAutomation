
import os as os
import glob
import numpy as np
import pandas as pd
import os

file = '/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/analysis/DeZambotti/Subjects_For_FinalAnalysis.xlsx'


subj_HPB_Nodreem = pd.read_excel(file, sheet_name='Xiaomi_Nodreem')
print('done')

# devices = ['FB', 'Dreem', 'Oura3', 'Acti']
devices = ['Oura3', 'FB', 'Acti', 'Xiaomi']

for devi in devices:
    # Get the Oura subjects in each night and Hand

    # data_dir = f'/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/analysis/DeZambotti/{devi}/Data'
    data_dir = f'/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/analysis/DeZambotti/{devi}/Data/withXiaomi'
    # /Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/analysis/DeZambotti/HPB/Data
    fi = glob.glob(data_dir + '/combined*N1*.csv')
    # Subjects = pd.DataFrame()
    for files in fi:
        Subjects = pd.DataFrame()

        data = pd.read_csv(files)
        df1 = data
        # df2 = subj_N1_All
        df2 = subj_HPB_Nodreem

        new_df = df1[df1['subject'].isin(df2['ID'])]

        new_df.to_csv(files.replace('/withXiaomi',
                                    '/withXiaomi/Common_Subj_N1_Nodreem'), index=False)


print('done')
