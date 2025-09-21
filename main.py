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

def run_training():
    print("=== Training models (train_model.py) ===")
    train_model.main()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Quant Investment Pipeline")
    parser.add_argument("--step", type=str, choices=["all", "scrap", "preprocess", "train"],
                        default="all",
                        help="Which step to run: scrap, preprocess, train, or all")

    args = parser.parse_args()

    if args.step == "scrap":
        run_scraping()
    elif args.step == "preprocess":
        run_preprocessing()
    elif args.step == "train":
        run_training()
    elif args.step == "all":
        run_scraping()
        run_preprocessing()
        run_training()
