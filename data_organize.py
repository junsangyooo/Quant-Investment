import pandas as pd
import os

current_directory = os.getcwd()
csv_directory = os.path.join(current_directory, 'stock_data')
def convert_csv_to_df():
    df = pd.read_csv(os.path.join(csv_directory, 'CRM.csv'))
    print(df.tail(5))
convert_csv_to_df()