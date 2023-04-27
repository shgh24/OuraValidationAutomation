import pandas as pd

data_path = '/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/analysis/DeZambotti/Oura3/EBE_individual_N01_R.csv'

df = pd.read_csv(data_path)

df = df.iloc[:, 1:]

# Calculate the mean and standard deviation for each column (except 'subject')
mean_d = df.loc[:, df.columns != 'subject'].mean()
std_d = df.loc[:, df.columns != 'subject'].std()
zscore = (df.loc[:, df.columns != 'subject']-mean_d)/std_d
outliers_bool = zscore.abs() > 3


for column in outliers_bool.columns:
    # Get the indices where the outliers are True in the current column
    outlier_indices = outliers_bool.loc[outliers_bool[column]].index

    # Store the corresponding subject numbers in the outliers DataFrame
    outliers[column] = df.loc[outlier_indices, 'subject'].values

# Remove any columns that have no outliers
outliers = outliers.loc[:, outliers.notnull().any()]

outliers.to_csv(data_path.replace('EBE', 'Outliers_EBE'), index=False)

print('done')
