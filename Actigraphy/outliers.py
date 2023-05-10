import pandas as pd


data_path = '/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/analysis/DeZambotti/Acti/Results/May_10_2023/Individual_Bias_N2.csv'

#data_path = '/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/analysis/DeZambotti/Oura3/EBE_individual_N01_R.csv'

df = pd.read_csv(data_path)

df = df.iloc[:, 1:]

# Calculate the mean and standard deviation for each column (except 'subject')
mean_d = df.loc[:, df.columns != 'subject'].mean()
std_d = df.loc[:, df.columns != 'subject'].std()
zscore = (df.loc[:, df.columns != 'subject']-mean_d)/std_d
outliers_bool = zscore.abs() > 2
outliers = pd.DataFrame()
# outliers = []

filename = "/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/analysis/DeZambotti/Acti/Results/May_10_2023/outlier_Individual_Bias_N2.txt"
with open(filename, "a") as f:  # open the file in append mode

    for column in outliers_bool.columns:
        # Get the indices where the outliers are True in the current column
        outlier_indices = outliers_bool.loc[outliers_bool[column]].index
        if len(outlier_indices) > 0:
            # Store the corresponding subject numbers in the outliers DataFrame
            #outliers[column] = df.loc[outlier_indices, 'subject'].values
            x = df.loc[outlier_indices, 'subject'].values
            f.write(f' {x} _ {column}\n')

    # Remove any columns that have no outliers
    outliers = outliers.loc[:, outliers.notnull().any()]

    outliers.to_csv(data_path.replace('Individual_Bias',
                    'Outliers_Individual_Bias'), index=False)

    print('done')
