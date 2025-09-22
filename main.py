import argparse
import scrap
import preprocess
import train_model

def run_scraping():
    print("=== Updating raw stock data (scrap.py) ===")
    scrap.updateDatas()

def run_preprocessing():
    print("=== Preprocessing stock data (preprocess.py) ===")
    preprocess.preprocess_all()

def run_training(period, threshold, topn):
    print("=== Training models (train_model.py) ===")
    train_model.train_and_recommend(period, threshold, topn)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Quant Investment Pipeline")
    parser.add_argument("--step", type=str, choices=["all", "scrap", "preprocess", "train"],
                        default="all",
                        help="Which step to run: scrap, preprocess, train, or all")
    parser.add_argument("--period", type=int, default=30, help="Forecast horizon in days")
    parser.add_argument("--threshold", type=float, default=0.1, help="Target return threshold (e.g., 0.1=10%)")
    parser.add_argument("--topn", type=int, default=5, help="How many stocks to recommend")

    args = parser.parse_args()

    if args.step == "scrap":
        run_scraping()
    elif args.step == "preprocess":
        run_preprocessing()
    elif args.step == "train":
        run_training(args.period, args.threshold, args.topn)
    elif args.step == "all":
        run_scraping()
        run_preprocessing()
        run_training(args.period, args.threshold, args.topn)
