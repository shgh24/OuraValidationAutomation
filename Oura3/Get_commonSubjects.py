
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

# devices = ['FB', 'Dreem', 'Oura3', 'Acti']
devices = ['Oura3', 'FB', 'Acti']
devices = ['Oura3']
#
for devi in devices:
    # Get the Oura subjects in each night and Hand
    #
    data_dir = f'/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/analysis/DeZambotti/{devi}/Common_Subj_N1_Nodreem'
    # /Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/analysis/DeZambotti/Oura3/Data/DeviceOnly/Common_Subj_N1_Nodreem

    fi = glob.glob(data_dir + '/combined*N1*.csv')

    for files in fi:
        Subjects = pd.DataFrame()

        data = pd.read_csv(files)
        df1 = data

        df2 = subj_N1_NoDreem

        new_df = df1[df1['subject'].isin(df2['ID'])]

        new_df.to_csv(files.replace('/Common_Subj_N1_Nodreem',
                                    '/Data/DeviceOnly/Common_Subj_N1_Nodreem'), index=False)


print('done')
