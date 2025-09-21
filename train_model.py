import pandas as pd
import os
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score

# Directories
current_directory = os.getcwd()
processed_dir = os.path.join(current_directory, 'processed_data')

def load_data(file):
    """Load one processed CSV and prepare features/labels."""
    df = pd.read_csv(file)
    df = df.sort_values('Date').reset_index(drop=True)

    # Target: next-day return direction (binary classification)
    df['Target'] = (df['Return'].shift(-1) > 0).astype(int)

    # Drop last row (no next-day label available)
    df = df.dropna().reset_index(drop=True)

    # Features: everything except Date, Close columns, Target
    drop_cols = ['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Target']
    feature_cols = [c for c in df.columns if c not in drop_cols]

    X = df[feature_cols]
    y = df['Target']

    return X, y, feature_cols

def train_single_stock(filename):
    filepath = os.path.join(processed_dir, filename)
    X, y, feature_cols = load_data(filepath)

    # Train/test split (80/20)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=False
    )

    # Model
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=6,
        random_state=42
    )
    model.fit(X_train, y_train)

    # Predictions
    y_pred = model.predict(X_test)

    # Metrics
    print(f"\n===== {filename} =====")
    print(f"Features used: {feature_cols}")
    print("Accuracy:", accuracy_score(y_test, y_pred))
    print(classification_report(y_test, y_pred))

def main():
    for filename in os.listdir(processed_dir):
        if filename.endswith(".csv"):
            try:
                train_single_stock(filename)
            except Exception as e:
                print(f"Failed to train on {filename}: {e}")

if __name__ == "__main__":
    main()
