import pandas as pd
import os

current_directory = os.getcwd()
csv_directory = os.path.join(current_directory, 'stock_data')
def convert_csv_to_df():
    df = pd.read_csv(os.path.join(csv_directory, 'AAPL.csv'))
    #df.set_index('Date', inplace=True)
    last_row = df.tail(1)
    last_date = last_row['Date'].values[0]
    print(last_date)

convert_csv_to_df()