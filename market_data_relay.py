import time
import yfinance as yf
import pandas as pd
import requests

# Configuration
SCREENER_CONFIGS = {
    'nifty50': {
        'tickers': ['^NSEI'] + [f'{ticker}.NS' for ticker in [
            'RELIANCE', 'TCS', 'HDFCBANK', 'ICICIBANK', 'HINDUNILVR', 'INFY', 'ITC', 
            'KOTAKBANK', 'HDFC', 'SBIN', 'BHARTIARTL', 'LT', 'BAJFINANCE', 'ASIANPAINT', 
            'HCLTECH', 'MARUTI', 'TITAN', 'SUNPHARMA', 'TATAMOTORS', 'AXISBANK', 
            'BAJAJFINSV', 'ULTRACEMCO', 'NTPC', 'TATASTEEL', 'POWERGRID', 'NESTLEIND', 
            'INDUSINDBK', 'BAJAJ-AUTO', 'TECHM', 'JSWSTEEL', 'GRASIM', 'ADANIPORTS', 
            'TATACONSUM', 'BRITANNIA', 'HINDALCO', 'DIVISLAB', 'CIPLA', 'UPL', 'WIPRO', 
            'ONGC', 'COALINDIA', 'BPCL', 'HDFCLIFE', 'IOC', 'SHREECEM', 'SBILIFE', 
            'HINDCOPPER', 'DRREDDY', 'EICHERMOT', 'TATAPOWER'
        ]],
        'name': 'NIFTY 50 Stocks'
    }
}

LOCAL_URL = "http://127.0.0.1:5000/create_scan/data"

def fetch_market_data(tickers):
    """Fetch market data using yfinance"""
    try:
        print(f"Fetching data for {len(tickers)} tickers...")
        data = yf.download(tickers, period="1d", group_by='ticker')
        
        results = []
        for ticker in tickers:
            try:
                ticker_data = data[ticker] if len(tickers) > 1 else data
                if not ticker_data.empty:
                    last_row = ticker_data.iloc[-1]
                    results.append({
                        'symbol': ticker,
                        'close': last_row['Close'],
                        'volume': int(last_row['Volume']),
                        'change_pct': ((last_row['Close'] - last_row['Open']) / last_row['Open']) * 100
                    })
            except Exception as e:
                print(f"Error processing {ticker}: {str(e)}")
        
        print(f"Successfully fetched data for {len(results)} tickers")
        return results
        
    except Exception as e:
        print(f"Error fetching market data: {str(e)}")
        return None

def post_to_local(data, screener_name):
    """Post results to local Flask app"""
    try:
        # Format data to match Chartink's expected format
        formatted_data = []
        for item in data:
            formatted_data.append({
                'nsecode': item['symbol'].replace('.NS', ''),
                'name': item['symbol'].replace('.NS', ''),
                'close': round(item['close'], 2),
                'per_chg': round(item['change_pct'], 2),
                'volume': item['volume']
            })
            
        payload = {
            'results': formatted_data,
            'screener_name': screener_name,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        headers = {'Content-Type': 'application/json'}
        response = requests.post(LOCAL_URL, json=payload, headers=headers)
        response.raise_for_status()
        print(f"Successfully posted {len(data)} results to {LOCAL_URL}")
        return True
    except Exception as e:
        print(f"Error posting to local app: {str(e)}")
        return False

def main():
    print("Starting Market Data Relay...")
    print("Available screeners:")
    for key, config in SCREENER_CONFIGS.items():
        print(f"- {key}: {config['name']}")
    print(f"\nPosting to: {LOCAL_URL}")
    print("Press Ctrl+C to stop\n")
    
    try:
        # Store last results for each screener
        last_results = {key: None for key in SCREENER_CONFIGS.keys()}
        
        while True:
            print("\n" + "="*50)
            print(f"Checking for new data at {time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Check each configured screener
            for screener_key, config in SCREENER_CONFIGS.items():
                print(f"\nChecking {config['name']}...")
                
                # Fetch new results
                current_results = fetch_market_data(config['tickers'])
                
                if current_results:
                    if current_results != last_results.get(screener_key):
                        print(f"New results detected in {config['name']}!")
                        if post_to_local(current_results, config['name']):
                            last_results[screener_key] = current_results
                    else:
                        print(f"No new results in {config['name']} since last check.")
                else:
                    print(f"No valid results from {config['name']}.")
            
            # Wait before next check (60 seconds between full cycles)
            print("\nNext check in 60 seconds...")
            time.sleep(60)
            
    except KeyboardInterrupt:
        print("\nStopping Market Data Relay...")
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
