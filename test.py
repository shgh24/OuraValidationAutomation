import pandas as pd
data_path = '/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/analysis/DeZambotti/Oura3/EBE_individual_N01_R.csv'

df = pd.read_csv(data_path)

df = df.iloc[:, 1:]

outliers = pd.DataFrame(columns=df.columns)
for column in df:
    if column != 'subject':
        count = 0
        mean_d = df[column].mean()
        std_d = df[column].std()

        for p in df[column]:
            count += 1
            z_score = (p - mean_d) / std_d
            if abs(z_score) > 3:
                suj_n = df.loc[count - 1, 'subject']
                str_p = f'{suj_n} with {z_score} is outlier in {column}'
                print(str_p)

                outliers.loc[count, column] = [
                    df.loc[count - 1, 'subject']]

outliers.iloc[:, 1:].to_csv(data_path.replace(
    'EBE', 'Outliers_EBE'), index=False)

print('done')
