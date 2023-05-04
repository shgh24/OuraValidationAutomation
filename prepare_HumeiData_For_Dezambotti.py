import pandas as pd
import numpy as np
import glob
import os as os

# Basically 3010n1, 3020n2 and 3030n1 psg terminated before lights on.
# For 3010 and 3020 subject was already awake so we can append wake to end of psg record.
# For 3030 subject was still sleeping so if we are doing any wake time estimation detection, nd to skip this.

staging_file_path = '/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/Sleep_Staging/Consensus_score/'
Saving_file_path = "/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/analysis/DeZambotti/Humei/Data"
Humei_file = "/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/Zepplife/Humei_cleande_N2.csv"
# FB_data="/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/Sleep_Staging/Fitbit/NUS3001_N1.csv"

Humei_df = pd.read_csv(Humei_file)
count = -1
sm_list_all = []
for index, row in Humei_df.iterrows():

    subject_id = row['Subject']
    n = str(row['Night'])
    # /Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/Sleep_Staging/Consensus_score/NUS3001_N1_030323_sleepstage_consensus.csv

    psg_filename = f'{staging_file_path}{subject_id}_N{n}_*.csv'
    matching_files = glob.glob(psg_filename)

    # subject	TST_diff	SE_diff	SOL_diff	WASO_diff	Light_diff	Deep_diff	REM_diff
    # subject	TIB	TST_ref	TST_device	WASO_ref	WASO_device	Light_ref	Light_device	Deep_ref	Deep_device	REM_ref	REM_device
    sm = pd.DataFrame(columns=['subject', 'TIB',	'TST_ref',	'TST_device',	'WASO_ref',	'WASO_device',
                      'Light_ref', 'Light_device',	'Deep_ref', 'Deep_device',	'REM_ref',	'REM_device'])

    if len(matching_files):
        # count += 1
        psg = pd.read_csv(matching_files[0])

        SOL_ref = 0
        for i, rows in psg.iterrows():
            if rows[0] == 0:
                SOL_ref += 1
            else:
                break

# psg.loc[psg != 0].index[-1]        last_nonzero_index = psg.loc[psg != 0].index[-1]
        X = psg.loc[psg.iloc[:, 0] != 0].index
        Sleepend = X[-1]
        # SOL_ref *= epochLenght/60

        Deep_ref = psg[SOL_ref:].value_counts()[3]/2
        REM_ref = psg[SOL_ref:].value_counts()[5]/2
        Light_ref = (psg[SOL_ref:].value_counts()[1]/2) + \
            (psg[SOL_ref:].value_counts()[2]/2)
        WASO_ref = psg[SOL_ref:].value_counts()[0]/2

        TST_ref = Deep_ref+REM_ref+Light_ref
        # +WASO_ref
        TIB = len(psg)/2

        sm_list = [row['Subject'], TIB, TST_ref, row['TIB'],
                   WASO_ref, row['wakeTime'],
                   Light_ref, row['shallowSleepTime'],
                   Deep_ref, row['deepSleepTime'],
                   REM_ref, row['REMTime']
                   ]

        sm_list_all.append(sm_list)

smN = pd.DataFrame(sm_list_all, columns=['subject', 'TIB',	'TST_ref',	'TST_device',	'WASO_ref',	'WASO_device',
                                         'Light_ref', 'Light_device',	'Deep_ref', 'Deep_device',	'REM_ref',	'REM_device'])
# print(sm_list_all)

smN.to_csv(os.path.join(Saving_file_path,
           'Individual_SleepMeasurement_N2.csv'))
