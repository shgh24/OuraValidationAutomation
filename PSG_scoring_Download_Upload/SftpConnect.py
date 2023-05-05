import pysftp
import os
import glob

# Connect to the SFTP server
sftp = pysftp.Connection('classic.sftp.thesiestagroup.com',
                         username='NUS_CSC', password='kmUeys_CERQ?')

# Change the working directory to the directory you want to get the attributes of
sftp.cwd('/input')

# Get the attributes of all items in the directory
items = sftp.listdir_attr()
# Get Files names in the input folder of the Siesta sftp server
existing_files = [item.filename for item in items if item.st_mode & 0o400]

# get a list of files in the PSG directory
local_Upload_folder_path = '/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/Domino_EDF/epoched'
psg_dir = local_Upload_folder_path
psg_files = os.listdir(psg_dir)
#psg_files = glob.glob(psg_dir+'/*.edf')
print(psg_files)


for file in psg_files:
    if file not in existing_files and file.endswith('.edf'):
        local_path = os.path.join(psg_dir, file)
        remote_path = os.path.join('/input', file)
        print(remote_path)
        sftp.put(local_path, remote_path)

# Close the SFTP connection

print("Finished Uploading :)")


# Download Scored  files from Siesta
#local_Download_folder_path = '/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/Domino_EDF/SiestaScored'
local_Download_folder_path = '/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/Sleep_Staging/SiestaScored'
psg_dir_Download = local_Download_folder_path
psg_files_scored = os.listdir(psg_dir_Download)


# cd to /output folder on siesta sftp server
sftp.cwd('/output')
items_forDownload = sftp.listdir()

# Finf the folder that has 2023 in the folder name (target folder)
for item in items_forDownload:
    if "2023" in item:
        download_foldername = item
        print(download_foldername)

# switch to the directory that scored files by Siesta uploaded
sftp.cwd(download_foldername)
# list all the files inside the folder
items_download = sftp.listdir_attr()
# Get Files names in the source folder in Siesta sftp server
Siesta_Download_files = [
    items_download.filename for items_download in items_download if items_download.st_mode & 0o400]

# Loop through all the files in the Siesta source folder and download the files that does not exist in the destination folder in the server
for file in Siesta_Download_files:
    if file not in psg_files_scored:
        local_path = os.path.join(psg_dir_Download, file)
        remote_path = os.path.join('/output', download_foldername, file)
        print(remote_path)
        sftp.get(remote_path, local_path)


print("Finished Downloading :)")

sftp.close()
