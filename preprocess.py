import pandas as pd
import os
import numpy as np

# Directories
current_directory = os.getcwd()
raw_data_dir = os.path.join(current_directory, 'stock_data')
processed_dir = os.path.join(current_directory, 'processed_data')

if not os.path.exists(processed_dir):
    os.makedirs(processed_dir)

def compute_features(df):
    """
    Given a stock DataFrame with columns [Date, Open, High, Low, Close, Adj Close, Volume],
    compute useful ML features and return processed DataFrame.
    """

    df = df.copy()
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date').reset_index(drop=True)

    # --- Core financial features ---

    # Daily returns based on Adj Close
    df['Return'] = df['Adj Close'].pct_change()

    # Moving averages (trend indicators)
    df['MA5'] = df['Adj Close'].rolling(window=5).mean()
    df['MA20'] = df['Adj Close'].rolling(window=20).mean()
    df['MA50'] = df['Adj Close'].rolling(window=50).mean()

    # Exponential moving average
    df['EMA12'] = df['Adj Close'].ewm(span=12, adjust=False).mean()
    df['EMA26'] = df['Adj Close'].ewm(span=26, adjust=False).mean()

    # MACD (trend momentum indicator)
    df['MACD'] = df['EMA12'] - df['EMA26']

    # Bollinger Bands (volatility)
    df['BB_Middle'] = df['MA20']
    df['BB_Upper'] = df['MA20'] + (2 * df['Adj Close'].rolling(window=20).std())
    df['BB_Lower'] = df['MA20'] - (2 * df['Adj Close'].rolling(window=20).std())

    # Rolling volatility (20-day)
    df['Volatility20'] = df['Return'].rolling(window=20).std()

    # RSI (Relative Strength Index, 14-day)
    delta = df['Adj Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    RS = gain / (loss + 1e-9)
    df['RSI14'] = 100 - (100 / (1 + RS))

    # Drop rows with NaN (from rolling calculations)
    df = df.dropna().reset_index(drop=True)

    return df

def preprocess_all():
    """
    Iterate through all CSV files in stock_data/, compute features,
    and save to processed_data/ with same filename.
    """
    for filename in os.listdir(raw_data_dir):
        if filename.endswith('.csv'):
            filepath = os.path.join(raw_data_dir, filename)
            try:
                df = pd.read_csv(filepath)
                processed_df = compute_features(df)
                save_path = os.path.join(processed_dir, filename)
                processed_df.to_csv(save_path, index=False)
                print(f"Processed and saved: {filename}")
            except Exception as e:
                print(f"Failed to process {filename}: {e}")

if __name__ == "__main__":
    preprocess_all()
