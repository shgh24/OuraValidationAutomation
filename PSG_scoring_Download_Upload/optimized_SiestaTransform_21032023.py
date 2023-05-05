import pandas as pd
import os
import glob


if __name__ == '__main__':
    source_path = '/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/Sleep_Staging/SiestaScored'
    #dest_path ='/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/Sleep_Staging/SiestaScored_Clean'
    tsv_files = glob.glob(os.path.join(source_path, '*hqc.txt'))

    for file in tsv_files:
        df = pd.read_csv(file, sep='\t')
        df.columns = ["epoch", "stage_repeats"]

        df.loc[len(df)] = df.loc[len(df)-1]
        df['stage_repeats'].replace({4: 3, 9: 0}, inplace=True)
        #csv_file = file.replace("__1_.hqc.txt", ".csv")
        csv_file = file.replace("_epoched__1_.hqc.txt", "_sleepstage_siesta.csv").replace(
            "SiestaScored", "SiestaScored_Clean")

        df[['stage_repeats']].to_csv(csv_file, index=False, header=False)
