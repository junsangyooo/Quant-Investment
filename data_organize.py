import pandas as pd
import os

current_directory = os.getcwd()
csv_directory = os.path.join(current_directory, 'historical_data')
def convert_csv_to_df():
    df = pd.read_csv(os.path.join(csv_directory, 'AAPL.csv'))
    df.set_index('Date', inplace=True)
    print(df)

convert_csv_to_df()