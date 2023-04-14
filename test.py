import pandas as pd
import numpy as np
import mne
# file = "/Users/shohreh/Downloads/Scldreem_s05_2023-03-14T00-23-48.edf"
# data = mne.io.read_raw_edf(file)
# raw_data = data.get_data()
# # you can get the metadata included in the file and a list of all channels:
# info = data.info
# channels = data.ch_names


df_Oura = pd.DataFrame({
    'timestamp': ['2023-03-03 23:50:00+08:00', '2023-03-04 00:00:00+08:00', '2023-03-04 00:10:00+08:00'],
    'data': [1, 2, 3]
})

lightOff = pd.Timestamp('2023-03-04 00:00:00')
lightOn = pd.Timestamp('2023-03-04 00:05:00')

# Convert timestamp column to Timestamp objects
df_Oura['timestamp'] = pd.to_datetime(df_Oura['timestamp'], utc=True)

# Slice the dataframe
df_sliced = df_Oura.loc[(df_Oura['timestamp'] >= lightOff)
                        & (df_Oura['timestamp'] < lightOn)]

print(df_sliced)
