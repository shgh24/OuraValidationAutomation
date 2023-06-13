import os
import pandas as pd
import shutil
import glob

df = pd.read_csv(
    "/Volumes/CSC5/SleepCognitionLab/Tera2b/DREEM_database/DREEMER/DPD_OuraValidation3/OuraValidation3_dataoverview.csv"
)

# specify the path to the directory containing the dreem raw files(downloaded from web dashboard)
dir_path = "/Volumes/CSC5/SleepCognitionLab/Tera2b/DREEM_database/DREEMER/DPD_OuraValidation3/Data"

folders = next(os.walk(dir_path))[1]
# 2023-03-09T23-30-56_19cfb704-83e3-40af-92d2-75fa740027d2
# iterate over all folders in the directory
for folder in folders:
    
    # extract the recording ID
    parts = folder.split("_")
    id_str = parts[1]

    # match the recording ID with subject ID
    match_id = df[df["Recording ID"].str.contains(
        id_str)]["Subject ID"].tolist()
    
    if match_id: 
        dest_dir = "/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/Dreem_Raw/"
        
        current_folder = os.path.join(dir_path, folder)       
        for hypno_file in glob.glob(os.path.join(current_folder, "*.txt")):
            # Scldreem_s01_2023-03-09T23-30-56[+0800]_hypnogram.txt
            parts = folder.split("_")
            file_date=parts[0]
            new_name = f'{match_id[0]}_{file_date}.txt'

            shutil.copy(hypno_file, os.path.join(dest_dir, new_name))

      