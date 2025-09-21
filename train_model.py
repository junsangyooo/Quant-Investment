import pandas as pd
import os
import argparse
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

current_directory = os.getcwd()
processed_dir = os.path.join(current_directory, 'processed_data')

def add_target(df, period, threshold):
    """
    Adds binary target column: 1 if price rises >= threshold within 'period' days.
    """
    df = df.copy()
    future_price = df['Adj Close'].shift(-period)
    df['Target'] = ((future_price / df['Adj Close'] - 1) >= threshold).astype(int)
    df = df.dropna().reset_index(drop=True)
    return df

def load_all_stocks(period, threshold):
    X_list, y_list, tickers = [], [], []
    for filename in os.listdir(processed_dir):
        if filename.endswith('.csv'):
            filepath = os.path.join(processed_dir, filename)
            try:
                df = pd.read_csv(filepath)
                df = add_target(df, period, threshold)

                drop_cols = ['Date','Open','High','Low','Close','Adj Close','Target']
                feature_cols = [c for c in df.columns if c not in drop_cols]

                X_list.append(df[feature_cols])
                y_list.append(df['Target'])
                tickers.extend([filename.replace('.csv','')] * len(df))
            except Exception as e:
                print(f"Skipping {filename}: {e}")

    X = pd.concat(X_list, ignore_index=True)
    y = pd.concat(y_list, ignore_index=True)
    tickers = np.array(tickers)
    return X, y, feature_cols, tickers

def train_and_recommend(period, threshold, top_n=5):
    X, y, feature_cols, tickers = load_all_stocks(period, threshold)

    X_train, X_test, y_train, y_test, tickers_train, tickers_test = train_test_split(
        X, y, tickers, test_size=0.2, shuffle=False
    )

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        random_state=42
    )
    model.fit(X_train, y_train)

    # Predict probabilities on last available rows (latest test set)
    proba = model.predict_proba(X_test)[:,1]  # probability of Target=1

    results = pd.DataFrame({
        "Ticker": tickers_test,
        "ProbUp": proba
    })

    # Take last row per ticker (most recent info)
    latest = results.groupby("Ticker").tail(1)
    latest = latest.sort_values("ProbUp", ascending=False)

    print(f"\n=== Top {top_n} stocks likely to rise {threshold*100:.1f}% in next {period} days ===")
    print(latest.head(top_n))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--period", type=int, default=30, help="Forecast horizon in days")
    parser.add_argument("--threshold", type=float, default=0.1, help="Target return threshold (e.g., 0.1=10%)")
    parser.add_argument("--topn", type=int, default=5, help="How many stocks to recommend")
    args = parser.parse_args()

    train_and_recommend(args.period, args.threshold, args.topn)
