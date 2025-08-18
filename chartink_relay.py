import time
import requests
from bs4 import BeautifulSoup

CHARTINK_URL = "https://chartink.com/screener/create-scan"
LOCAL_URL = "http://127.0.0.1:5000/create_scan"


def fetch_chartink_scan_clause():
    try:
        response = requests.get(CHARTINK_URL)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        textarea = soup.find("textarea")
        if textarea:
            return textarea.text.strip()
    except Exception as e:
        print("Error fetching Chartink scan clause:", e)
    return None


def post_to_local(scan_clause):
    try:
        data = {'scan_clause': scan_clause}
        resp = requests.post(LOCAL_URL, data=data)
        print("Posted to local:", resp.status_code)
        return resp
    except Exception as e:
        print("Error posting to local:", e)
        return None


def main():
    last_clause = None
    while True:
        clause = fetch_chartink_scan_clause()
        if clause and clause != last_clause:
            print("New scan clause detected! Posting to local...")
            post_to_local(clause)
            last_clause = clause
        time.sleep(60)  # Check every 60 seconds


if __name__ == "__main__":
    main()
