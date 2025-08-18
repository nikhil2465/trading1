import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
import json
import time
import random

def fetch_chartink_scan(scan_clause):
    """Fetch scan results from Chartink using the provided scan clause."""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
    ]
    try:
        with requests.Session() as session:
            # Get CSRF token
            r = session.get("https://chartink.com/screener/")
            soup = bs(r.content, "html.parser")
            csrf_token = soup.find("meta", {"name": "csrf-token"})
            if not csrf_token:
                print("CSRF token not found. Site may have changed.")
                return None
            csrf_token = csrf_token["content"]

            headers = {
                "Referer": "https://chartink.com/screener/",
                "X-Csrf-Token": csrf_token,
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": random.choice(user_agents)
            }
            payload = {
                "scan_clause": scan_clause
            }

            print("Fetching data from Chartink...")
            response = session.post("https://chartink.com/screener/process", 
                                 headers=headers, 
                                 data=payload)
            
            if response.status_code == 200:
                try:
                    data = response.json().get('data', [])
                    if data:
                        return pd.DataFrame(data)
                    else:
                        print("No matching stocks found.")
                        return None
                except json.JSONDecodeError:
                    print("Invalid JSON response")
                    return None
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return None
    except Exception as e:
        print(f"Error fetching scan: {e}")
        return None

def post_to_flask(data, scan_type):
    """Post results to Flask app"""
    try:
        if data is None or data.empty:
            print("No data to post")
            return False
            
        # Format data for the endpoint
        formatted_data = []
        for _, row in data.iterrows():
            formatted_data.append({
                "nsecode": row.get('nsecode', ''),
                "name": row.get('name', ''),
                "close": float(row.get('close', 0)),
                "per_chg": float(row.get('per_chg', 0)),
                "volume": int(row.get('volume', 0))
            })
        
        payload = {
            "results": formatted_data,
            "screener_name": f"Chartink {scan_type.capitalize()} Scan",
            "timestamp": pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        local_url = "http://127.0.0.1:5000/create_scan/data"
        headers = {'Content-Type': 'application/json'}
        
        print(f"Posting {len(formatted_data)} results to Flask app...")
        response = requests.post(
            local_url,
            data=json.dumps(payload, default=str),
            headers=headers
        )
        response.raise_for_status()
        print(f"Successfully posted {len(formatted_data)} results to {local_url}")
        return True
        
    except Exception as e:
        print(f"Error posting to Flask app: {str(e)}")
        return False

def verify_weekly_timeframe():
    """Check if the current market is in weekly timeframe"""
    # Get current day (0=Monday, 6=Sunday)
    current_day = pd.Timestamp.now().dayofweek
    # Check if it's Friday (4) or weekend (5,6) for weekly timeframe
    return current_day >= 4  # Friday, Saturday, or Sunday

def main():
    # Define the scan clauses with exact parameters from Chartink URLs
    scan_conditions = {
        # From: https://chartink.com/screener/price-below-lower-bollinger-band-rsi-below-30
        'bullish': '( {futidx} ( weekly rsi(14) <= 30 and weekly close <= weekly lower bollinger(20,2) ) )',
        # From: https://chartink.com/screener/rsi-70-upper-bb
        'bearish': '( {futidx} ( weekly rsi(14) >= 70 and weekly close >= weekly upper bollinger(20,2) ) )',
    }
    
    while True:
        try:
            current_time = pd.Timestamp.now()
            print("\n" + "="*50)
            print(f"Running scans at {current_time}")
            
            # Check if we should run weekly scan
            if not verify_weekly_timeframe():
                print("\nNot in weekly timeframe (Friday-Sunday). Next check in 1 hour...")
                time.sleep(3600)
                continue
                
            # Run bullish scan (oversold condition)
            print("\nRunning BULLISH scan (Weekly RSI <= 30 & Close <= Lower BB)...")
            bullish_results = fetch_chartink_scan(scan_conditions['bullish'])
            
            if bullish_results is not None and not bullish_results.empty:
                print(f"\nFound {len(bullish_results)} BULLISH stocks:")
                print(bullish_results[['nsecode', 'name', 'close', 'volume']])
                
                # Save to CSV
                csv_file = 'bullish_scan_results.csv'
                bullish_results.to_csv(csv_file, index=False)
                print(f"\nBullish results saved to {csv_file}")
                
                # Post to Flask app
                post_to_flask(bullish_results, 'bullish')
            else:
                print("No stocks found in oversold condition (Weekly RSI <= 30 & Close <= Lower BB)")
            
            # Small delay between scans
            time.sleep(5)
            
            # Run bearish scan (overbought condition)
            print("\nRunning BEARISH scan (Weekly RSI >= 70 & Close >= Upper BB)...")
            bearish_results = fetch_chartink_scan(scan_conditions['bearish'])
            
            if bearish_results is not None and not bearish_results.empty:
                print(f"\nFound {len(bearish_results)} BEARISH stocks:")
                print(bearish_results[['nsecode', 'name', 'close', 'volume']])
                
                # Save to CSV
                csv_file = 'bearish_scan_results.csv'
                bearish_results.to_csv(csv_file, index=False)
                print(f"\nBearish results saved to {csv_file}")
                
                # Post to Flask app
                post_to_flask(bearish_results, 'bearish')
            else:
                print("No stocks found in overbought condition (Weekly RSI >= 70 & Close >= Upper BB)")
            
            # Wait before next full scan (1 hour)
            print("\nNext full scan in 1 hour...")
            time.sleep(3600)
            
        except KeyboardInterrupt:
            print("\nStopping scanner...")
            break
        except Exception as e:
            print(f"Error: {str(e)}")
            print("Retrying in 5 minutes...")
            time.sleep(300)  # Wait 5 minutes before retrying

if __name__ == "__main__":
    main()
