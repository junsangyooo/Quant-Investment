import argparse
import scrap
import preprocess
import train_model

# KIS OpenAPI modules
import auth as au
import domestic as dm
import time

def run_scrap():
    print("=== Running scrap.py ===")
    scrap.updateDatas()

def run_preprocess():
    print("=== Running preprocess.py ===")
    preprocess.run_preprocess()

def run_train(period, threshold, topn):
    print("=== Running train_model.py ===")
    return train_model.run_training(period=period, threshold=threshold, topn=topn)

def run_autotrade(recommendations, buy_price):
    print("=== Running Auto Trading ===")
    au.auth()  # 인증
    for stock_code in recommendations:
        try:
            # 주문 가능 수량 확인
            psbl = dm.get_inquire_psbl_order(pdno=stock_code, ord_unpr=buy_price)
            qty = int(psbl.loc[0, 'nrcvb_buy_qty'])  # 가능한 매수 수량
            if qty > 0:
                res = dm.get_order_cash(
                    ord_dv="buy",
                    itm_no=stock_code,
                    qty=qty,
                    unpr=buy_price
                )
                print(f"[BUY ORDER PLACED] {stock_code} x {qty} @ {buy_price}")
                print(res)
            else:
                print(f"[SKIP] {stock_code}: No available buy qty.")
        except Exception as e:
            print(f"[ERROR] Trading {stock_code}: {e}")
        time.sleep(0.2)  # API rate-limit 안전 대기

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--step", choices=["all", "scrap", "preprocess", "train"], required=True)
    parser.add_argument("--period", type=int, default=30)
    parser.add_argument("--threshold", type=float, default=0.1)
    parser.add_argument("--topn", type=int, default=5)
    parser.add_argument("--buy_price", type=int, default=None, help="If provided, auto-buy recommended stocks at this price")
    args = parser.parse_args()

    if args.step == "scrap":
        run_scrap()
    elif args.step == "preprocess":
        run_preprocess()
    elif args.step == "train":
        recos = run_train(args.period, args.threshold, args.topn)
        if args.buy_price:
            run_autotrade(recos, args.buy_price)
    elif args.step == "all":
        run_scrap()
        run_preprocess()
        recos = run_train(args.period, args.threshold, args.topn)
        if args.buy_price:
            run_autotrade(recos, args.buy_price)

if __name__ == "__main__":
    main()

# Simple data scrapping, preprocessing and training
# python main.py --step all --period 30 --threshold 0.1 --topn 5

# After getting a suggestion, buy the suggested stocks at a specific price
# python main.py --step all --period 30 --threshold 0.1 --topn 5 --buy_price 65000