# paper_trading.py
import pandas as pd
from datetime import datetime
from data1 import fetch_chartink_scan, scans, FALLBACK_DATA

CAPITAL = 100000  # starting cash
TRADE_LOG = "trade_log.csv"

def run_paper_trade():
    cash = CAPITAL
    positions = {}

    # Get bullish stocks
    df = fetch_chartink_scan(scans['bullish'])
    if df is None:
        df = pd.DataFrame(FALLBACK_DATA['bullish'])

    for _, row in df.iterrows():
        symbol = row['nsecode']
        price = row['close']
        qty = int(cash // (price * 10))  # example position size
        if qty > 0:
            cost = qty * price
            cash -= cost
            positions[symbol] = {'qty': qty, 'buy_price': price}
            log_trade("BUY", symbol, price, qty, cash)

    print("📊 Final positions:", positions)
    print(f"💰 Remaining cash: {cash}")

def log_trade(action, symbol, price, qty, cash):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = pd.DataFrame([[now, action, symbol, price, qty, cash]],
                             columns=["datetime", "action", "symbol", "price", "quantity", "cash_balance"])
    try:
        existing = pd.read_csv(TRADE_LOG)
        log_entry = pd.concat([existing, log_entry], ignore_index=True)
    except FileNotFoundError:
        pass
    log_entry.to_csv(TRADE_LOG, index=False)

if __name__ == "__main__":
    run_paper_trade()
