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

# Your scan clauses
scans = {
    'bullish': '( {futidx} ( weekly rsi(14) <= 30 and weekly close <= weekly lower bollinger(20,2) ) )',
    'bearish': '( {futidx} ( weekly rsi(14) >= 70 and weekly close >= weekly upper bollinger(20,2) ) )',
    'screenshot1_bearish_like': '( {futidx} ( weekly upper bollinger(20,2) > weekly close and weekly rsi(14) >= 70 ) )',
    'screenshot2_bullish_like': '( {futidx} ( weekly lower bollinger(20,2) < weekly close and weekly rsi(14) <= 30 ) )'
}

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
