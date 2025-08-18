import time
import requests
from bs4 import BeautifulSoup
import pandas as pd

CHARTINK_URL = "https://chartink.com/screener/create-scan"
LOCAL_URL = "http://127.0.0.1:5000/create_scan"

def fetch_chartink_results():
    resp = requests.get(CHARTINK_URL)
    soup = BeautifulSoup(resp.text, 'html.parser')
    table = soup.find("table")
    if not table:
        print("No results table found.")
        return None
    headers = [th.get_text(strip=True) for th in table.find_all("th")]
    rows = []
    for row in table.find_all("tr"):
        cols = [td.get_text(strip=True) for td in row.find_all("td")]
        if cols:
            rows.append(dict(zip(headers, cols)))
    print(f"Fetched {len(rows)} rows from Chartink.")
    return rows

def post_to_local(results):
    if not results:
        print("No data to post.")
        return None
    resp = requests.post(LOCAL_URL, json={"results": results})
    print("Posted to local:", resp.status_code)
    return resp

def main():
    last_snapshot = None
    while True:
        results = fetch_chartink_results()
        if results and results != last_snapshot:
            print("New scan results detected! Posting to local...")
            post_to_local(results)
            last_snapshot = results
        else:
            print("No new results or no data.")
        time.sleep(60)

if __name__ == "__main__":
    main()
