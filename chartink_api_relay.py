import time
import requests
import pandas as pd

# Configuration
SCREENER_CONFIGS = {
    'bollinger_rsi_lower': {
        'url': 'https://chartink.com/screener/process',
        'params': {
            'scan_clause': '( {cash} ( daily close > daily ema( close, 20 ) and daily close > 200 and daily close > 100 ) )',
            'exchange': 'NSE,NFO,CDS,MCX'
        },
        'name': 'Bollinger Lower Band & RSI < 30'
    },
    'rsi_70_upper_bb': {
        'url': 'https://chartink.com/screener/process',
        'params': {
            'scan_clause': '( {cash} ( daily rsi( 14 ) > 70 and daily close > daily upper bollinger( 20, 2 ) ) )',
            'exchange': 'NSE,NFO,CDS,MCX'
        },
        'name': 'RSI > 70 & Upper BB'
    }
}

LOCAL_URL = "http://127.0.0.1:5000/create_scan/data"

def fetch_screener_results(config):
    """Fetch results from a specific screener"""
    try:
        print(f"\nFetching data from: {config['name']}")
        
        # Set headers to mimic a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.9',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://chartink.com',
            'Referer': 'https://chartink.com/screener/technical',
            'X-Requested-With': 'XMLHttpRequest'
        }
        
        # Make the request
        response = requests.post(
            config['url'],
            data=config['params'],
            headers=headers
        )
        
        response.raise_for_status()
        data = response.json()
        
        if data.get('status') == 'success' and 'data' in data:
            df = pd.DataFrame(data['data'])
            print(f"Found {len(df)} results")
            return df.to_dict('records')
        else:
            print(f"Error in response: {data.get('message', 'Unknown error')}")
            return None
            
    except Exception as e:
        print(f"Error fetching screener results: {str(e)}")
        return None

def post_to_local(data, screener_name):
    """Post results to local Flask app"""
    try:
        payload = {
            'screener': screener_name,
            'data': data,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        response = requests.post(LOCAL_URL, json=payload)
        response.raise_for_status()
        print(f"Successfully posted {len(data)} results to {LOCAL_URL}")
        return True
    except Exception as e:
        print(f"Error posting to local app: {str(e)}")
        return False

def main():
    print("Starting Chartink API Data Relay...")
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
                current_results = fetch_screener_results(config)
                
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
        print("\nStopping Chartink API Data Relay...")
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
