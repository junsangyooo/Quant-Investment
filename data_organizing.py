import pandas as pd
import os

csv_directory = 'path/to/your/csv/files'

def convert_csv_to_df():
    df = pd.read_csv(os.path.join(csv_directory, 'APPL.csv'))
    
