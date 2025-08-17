# import requests
# from bs4 import BeautifulSoup as bs
# import random
# import pandas as pd
# import json
# import time

# FALLBACK_DATA = {
#     "bullish": [
#         {"nsecode": "INFY", "name": "Infosys Ltd", "close": 1450.25, "volume": 1250000},
#         {"nsecode": "TCS", "name": "Tata Consultancy Services", "close": 3550.75, "volume": 980000},
#     ],
#     "bearish": [
#         {"nsecode": "RELIANCE", "name": "Reliance Industries", "close": 2500.10, "volume": 1450000},
#         {"nsecode": "HDFCBANK", "name": "HDFC Bank", "close": 1600.55, "volume": 870000},
#     ],
#     "screenshot1_bearish_like": [
#         {"nsecode": "ICICIBANK", "name": "ICICI Bank", "close": 950.20, "volume": 720000},
#     ],
#     "screenshot2_bullish_like": [
#         {
#             "nsecode": "TCS",
#             "name": "Tata Consultancy Services Limited",
#             "close": 3035.4,
#             "volume": 3358232
#         }
#     ]
# }

# def fetch_chartink_scan(scan_clause):
#     user_agents = [
#         "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
#         "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
#     ]
#     with requests.Session() as session:
#         r = session.get("https://chartink.com/screener/")
#         soup = bs(r.content, "html.parser")
#         csrf_token = soup.find("meta", {"name": "csrf-token"})
#         if not csrf_token:
#             print("CSRF token not found. Site may have changed.")
#             return None
#         csrf_token = csrf_token["content"]

#         headers = {
#             "Referer": "https://chartink.com/screener/",
#             "X-Csrf-Token": csrf_token,
#             "Content-Type": "application/x-www-form-urlencoded",
#             "User-Agent": random.choice(user_agents)
#         }
#         payload = {
#             "scan_clause": scan_clause
#         }

#         response = session.post("https://chartink.com/screener/process", headers=headers, data=payload)
#         if response.status_code == 200:
#             try:
#                 data = response.json().get('data', [])
#                 if data:
#                     df = pd.DataFrame(data)
#                     return df
#                 else:
#                     print("No matching stocks found.")
#                     return None
#             except json.JSONDecodeError:
#                 print("Invalid json response")
#                 return None
#         else:
#             print(f"Error: {response.status_code} - {response.text}")
#             return None

# scans = {
#     'bullish': '( {futidx} ( weekly rsi(14) <= 30 and weekly close <= weekly lower bollinger(20,2) ) )',
#     'bearish': '( {futidx} ( weekly rsi(14) >= 70 and weekly close >= weekly upper bollinger(20,2) ) )',
#     'screenshot1_bearish_like': '( {futidx} ( weekly upper bollinger(20,2) > weekly close and weekly rsi(14) >= 70 ) )',
#     'screenshot2_bullish_like': '( {futidx} ( weekly lower bollinger(20,2) < weekly close and weekly rsi(14) <= 30 ) )'
# }

# if __name__ == "__main__":
#     for scan_name, clause in scans.items():
#         print(f"Running {scan_name} scan...")
#         results = fetch_chartink_scan(clause)
#         if results is not None:
#             print(f"{scan_name.capitalize()} Results (sample):")
#             print(results[['nsecode', 'name', 'close', 'volume']].head())
#             results.to_csv(f'{scan_name}_stocks.csv', index=False)
#         time.sleep(10)

# import requests
# from bs4 import BeautifulSoup as bs
# import random
# import pandas as pd
# import json

# # Fallback data from your screenshot (only TCS)
# FALLBACK_DATA = [
#     {
#         "nsecode": "TCS",
#         "name": "Tata Consultancy Services Limited",
#         "close": 3035.4,
#         "volume": 3358232
#     }
# ]

# def fetch_chartink_scan(scan_clause):
#     """Fetch scan results from Chartink using the provided scan clause."""
#     user_agents = [
#         "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
#         "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
#     ]
#     try:
#         with requests.Session() as session:
#             # Get CSRF token
#             r = session.get("https://chartink.com/screener/")
#             soup = bs(r.content, "html.parser")
#             csrf_token = soup.find("meta", {"name": "csrf-token"})
#             if not csrf_token:
#                 print("CSRF token not found. Site may have changed.")
#                 return None
#             csrf_token = csrf_token["content"]

#             headers = {
#                 "Referer": "https://chartink.com/screener/",
#                 "X-Csrf-Token": csrf_token,
#                 "Content-Type": "application/x-www-form-urlencoded",
#                 "User-Agent": random.choice(user_agents)
#             }
#             payload = {
#                 "scan_clause": scan_clause
#             }

#             response = session.post("https://chartink.com/screener/process", headers=headers, data=payload)
#             if response.status_code == 200:
#                 try:
#                     data = response.json().get('data', [])
#                     if data:
#                         return pd.DataFrame(data)
#                     else:
#                         print("No matching stocks found.")
#                         return None
#                 except json.JSONDecodeError:
#                     print("Invalid JSON response")
#                     return None
#             else:
#                 print(f"Error: {response.status_code} - {response.text}")
#                 return None
#     except Exception as e:
#         print(f"Error fetching scan: {e}")
#         return None

# # ✅ Added scans dict so Flask app works
# scans = {
#     'tcs_only': '( {cash} ( {nsecode} = ( "TCS" ) ) )'
# }

# if __name__ == "__main__":
#     print("Running TCS-only scan...")
#     results = fetch_chartink_scan(scans['tcs_only'])
#     if results is not None:
#         print("Live Results:")
#         print(results[['nsecode', 'name', 'close', 'volume']].head())
#         results.to_csv('TCS_stocks.csv', index=False)
#     else:
#         print("Using fallback data for TCS...")
#         fallback_df = pd.DataFrame(FALLBACK_DATA)
#         print(fallback_df)
#         fallback_df.to_csv('TCS_stocks.csv', index=False)


import requests
from bs4 import BeautifulSoup as bs
import random
import pandas as pd
import json
import time

# Fallback data per scan type
FALLBACK_DATA = {
    "bullish": [
        {"nsecode": "INFY", "name": "Infosys Ltd", "close": 1450.25, "volume": 1250000},
        {"nsecode": "TCS", "name": "Tata Consultancy Services", "close": 3550.75, "volume": 980000},
    ],
    "bearish": [
        {"nsecode": "RELIANCE", "name": "Reliance Industries", "close": 2500.10, "volume": 1450000},
        {"nsecode": "HDFCBANK", "name": "HDFC Bank", "close": 1600.55, "volume": 870000},
    ],
    "screenshot1_bearish_like": [
        {"nsecode": "ICICIBANK", "name": "ICICI Bank", "close": 950.20, "volume": 720000},
    ],
    "screenshot2_bullish_like": [
        {"nsecode": "TCS", "name": "Tata Consultancy Services Limited", "close": 3035.4, "volume": 3358232}
    ]
}

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

            response = session.post("https://chartink.com/screener/process", headers=headers, data=payload)
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

def fetch_nse_option_chain(symbol):
    """
    Fetch option chain data for the given symbol from NSE and save to CSV.
    """
    url = f"https://www.nseindia.com/api/option-chain-equities?symbol={symbol.upper()}"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": f"https://www.nseindia.com/option-chain"
    }
    session = requests.Session()
    # Get cookies by visiting NSE homepage first
    session.get("https://www.nseindia.com", headers=headers)
    response = session.get(url, headers=headers)
    if response.status_code == 200:
        try:
            data = response.json()
            records = []
            for item in data.get("records", {}).get("data", []):
                strikePrice = item.get("strikePrice")
                ce = item.get("CE", {})
                pe = item.get("PE", {})
                records.append({
                    "strikePrice": strikePrice,
                    "CE_openInterest": ce.get("openInterest"),
                    "CE_changeInOI": ce.get("changeinOpenInterest"),
                    "CE_lastPrice": ce.get("lastPrice"),
                    "PE_openInterest": pe.get("openInterest"),
                    "PE_changeInOI": pe.get("changeinOpenInterest"),
                    "PE_lastPrice": pe.get("lastPrice"),
                })
            df = pd.DataFrame(records)
            csv_filename = f"{symbol.upper()}_option_chain.csv"
            df.to_csv(csv_filename, index=False)
            print(f"Option chain data saved to {csv_filename}")
            return csv_filename
        except Exception as e:
            print(f"Error parsing option chain data: {e}")
            return None
    else:
        print(f"Failed to fetch option chain for {symbol}. Status: {response.status_code}")
        return None

def run_macro_on_option_chain(csv_filename):
    """
    Placeholder for running macro on the option chain CSV.
    Replace this with your macro logic.
    """
    df = pd.read_csv(csv_filename)
    # ...macro logic here...
    print(f"Macro run on {csv_filename}. Results:")
    print(df.head())  # Example output

def fetch_option_chain_for_symbols(symbols):
    """
    Fetch and save option chain data for all symbols in the list.
    """
    for symbol in symbols:
        symbol = symbol.strip()
        if symbol:
            csv_file = fetch_nse_option_chain(symbol)
            if csv_file:
                run_macro = input(f"Run macro on {csv_file}? (y/n): ").strip().lower()
                if run_macro == "y":
                    run_macro_on_option_chain(csv_file)

# Your scan clauses
scans = {
    'bullish': '( {futidx} ( weekly rsi(14) <= 30 and weekly close <= weekly lower bollinger(20,2) ) )',
    'bearish': '( {futidx} ( weekly rsi(14) >= 70 and weekly close >= weekly upper bollinger(20,2) ) )',
    'screenshot1_bearish_like': '( {futidx} ( weekly upper bollinger(20,2) > weekly close and weekly rsi(14) >= 70 ) )',
    'screenshot2_bullish_like': '( {futidx} ( weekly lower bollinger(20,2) < weekly close and weekly rsi(14) <= 30 ) )'
}

def run_chanakya_analysis(csv_filename):
    """
    Run Chanakya analysis (macro) on the given CSV file.
    """
    df = pd.read_csv(csv_filename)
    # ...insert Chanakya macro logic here...
    print(f"Chanakya analysis results for {csv_filename}:")
    print(df.head())  # Example output

def chartink_bullish_bearish_component():
    """
    Fetch and save Chartink screener data for bullish/bearish conditions.
    """
    chartink_scans = {
        'bullish': '( {futidx} ( weekly rsi(14) <= 30 and weekly close <= weekly lower bollinger(20,2) ) )',
        'bearish': '( {futidx} ( weekly rsi(14) >= 70 and weekly close >= weekly upper bollinger(20,2) ) )'
    }
    for scan_name, clause in chartink_scans.items():
        print(f"Running Chartink {scan_name} scan...")
        results = fetch_chartink_scan(clause)
        if results is not None:
            print(f"{scan_name.capitalize()} Results (sample):")
            print(results[['nsecode', 'name', 'close', 'volume']].head())
            results.to_csv(f'chartink_{scan_name}_stocks.csv', index=False)
        else:
            print(f"No live data for {scan_name}, using fallback.")
            fallback_list = FALLBACK_DATA.get(scan_name, [])
            if fallback_list:
                pd.DataFrame(fallback_list).to_csv(f'chartink_{scan_name}_stocks.csv', index=False)

def open_chartink_magic_filters_scan():
    """
    Generate Chartink scan creation URL with magic filters for futures segment:
    - RSI < 30 with lower Bollinger Band and weekly close
    - RSI > 70 with upper Bollinger Band and weekly close
    """
    # Clause for "Stock passes any of the below filters in futures segment"
    scan_clause = (
        '( {futidx} ( weekly rsi(14) <= 30 and weekly close <= weekly lower bollinger(20,2) ) ) '
        'or ( {futidx} ( weekly rsi(14) >= 70 and weekly close >= weekly upper bollinger(20,2) ) )'
    )
    # Chartink scan creation URL with clause pre-filled (URL-encoded)
    import urllib.parse
    base_url = "https://chartink.com/screener/create-scan"
    params = {"scan_clause": scan_clause}
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    print("Open this URL to create the scan with magic filters in futures segment:")
    print(url)

if __name__ == "__main__":
    for scan_name, clause in scans.items():
        print(f"Running {scan_name} scan...")
        results = fetch_chartink_scan(clause)
        if results is not None:
            print(f"{scan_name.capitalize()} Results (sample):")
            print(results[['nsecode', 'name', 'close', 'volume']].head())
            results.to_csv(f'{scan_name}_stocks.csv', index=False)
        else:
            # Save fallback if no live data
            fallback_list = FALLBACK_DATA.get(scan_name, [])
            if fallback_list:
                pd.DataFrame(fallback_list).to_csv(f'{scan_name}_stocks.csv', index=False)
        time.sleep(10)
    
    # Option chain feature (does not affect existing scans)
    user_symbol = input("Enter NSE symbol for option chain (or press Enter to skip): ").strip()
    if user_symbol:
        csv_file = fetch_nse_option_chain(user_symbol)
        if csv_file:
            run_macro = input("Run macro on option chain CSV? (y/n): ").strip().lower()
            if run_macro == "y":
                run_macro_on_option_chain(csv_file)
    
    # Option chain feature for multiple symbols (does not affect existing scans)
    user_symbols = input("Enter NSE symbols for option chain (comma-separated, or press Enter to skip): ").strip()
    if user_symbols:
        symbol_list = [s.strip() for s in user_symbols.split(",") if s.strip()]
        fetch_option_chain_for_symbols(symbol_list)

    # --- Separate Component 1: Chanakya Analysis ---
    print("\n--- Chanakya Analysis Component ---")
    chanakya_csv = input("Enter CSV filename for Chanakya analysis (or press Enter to skip): ").strip()
    if chanakya_csv:
        run_chanakya_analysis(chanakya_csv)

    # --- Separate Component 2: Chartink Bullish/Bearish Screener ---
    print("\n--- Chartink Bullish/Bearish Screener Component ---")
    run_chartink = input("Run Chartink screener for bullish/bearish scans? (y/n): ").strip().lower()
    if run_chartink == "y":
        chartink_bullish_bearish_component()

    # --- Add this at the end for manual trigger ---
    run_magic_filters = input("\nCreate Chartink scan with magic filters for futures segment? (y/n): ").strip().lower()
    if run_magic_filters == "y":
        open_chartink_magic_filters_scan()
