import time
import json
import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
from getpass import getpass

# Configuration
SCREENER_CONFIGS = {
    'bollinger_rsi_lower': {
        'url': 'https://chartink.com/screener/process',
        'params': {
            'condition': '{"exchange":["NSE","NFO","CDS","MCX"],"scan_clause":"( {cash} ( daily close > daily ema( close, 20 ) and daily close > 200 and daily close > 100 ) )"}'
        },
        'name': 'Bollinger Lower Band & RSI < 30'
    },
    'rsi_70_upper_bb': {
        'url': 'https://chartink.com/screener/process',
        'params': {
            'condition': '{"exchange":["NSE","NFO","CDS","MCX"],"scan_clause":"( {cash} ( daily rsi( 14 ) > 70 and daily close > daily upper bollinger( 20, 2 ) ) )"}'
        },
        'name': 'RSI > 70 & Upper BB'
    }
}

LOCAL_URL = "http://127.0.0.1:5000/create_scan/data"
CREDENTIALS_FILE = "chartink_credentials.json"

def load_credentials():
    """Load credentials from file if it exists"""
    try:
        if os.path.exists(CREDENTIALS_FILE):
            with open(CREDENTIALS_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load saved credentials: {str(e)}")
    return None

def save_credentials(email, password):
    """Save credentials to a file"""
    try:
        with open(CREDENTIALS_FILE, 'w') as f:
            json.dump({"email": email, "password": password}, f)
    except Exception as e:
        print(f"Warning: Could not save credentials: {str(e)}")

def get_csrf_token(session, url):
    """Extract CSRF token from the page"""
    try:
        response = session.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Try to find CSRF token in meta tag
        meta_token = soup.find('meta', {'name': 'csrf-token'})
        if meta_token and meta_token.get('content'):
            return meta_token['content']
            
        # Try to find CSRF token in input field
        input_token = soup.find('input', {'name': '_token'})
        if input_token and input_token.get('value'):
            return input_token['value']
            
        print("Warning: Could not find CSRF token in page")
        return None
        
    except Exception as e:
        print(f"Error getting CSRF token: {str(e)}")
        return None

def login_to_chartink(session, email=None, password=None, max_retries=3):
    """Login to Chartink and return the authenticated session"""
    if not email or not password:
        print("\n=== Chartink Login Required ===")
        email = input("Enter your Chartink email: ")
        password = getpass("Enter your Chartink password: ")
        save_credentials(email, password)
    
    login_url = "https://chartink.com/login"
    
    for attempt in range(max_retries):
        try:
            print(f"\nAttempting to login to Chartink (Attempt {attempt + 1}/{max_retries})...")
            
            # First, get the login page to set cookies and get CSRF token
            print("Getting login page...")
            response = session.get(login_url)
            response.raise_for_status()
            
            # Extract CSRF token
            csrf_token = get_csrf_token(session, login_url)
            if not csrf_token:
                print("Warning: Could not find CSRF token, trying with empty token...")
            
            # Prepare login data
            login_data = {
                '_token': csrf_token or '',
                'email': email,
                'password': password,
                'remember': 'on'
            }
            
            # Set headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Origin': 'https://chartink.com',
                'Referer': login_url,
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            # Submit login form
            print("Submitting login form...")
            response = session.post(
                login_url,
                data=login_data,
                headers=headers,
                allow_redirects=True
            )
            
            # Check if login was successful
            if 'dashboard' in response.url:
                print("Successfully logged in to Chartink")
                return True
            else:
                print(f"Login failed. Status code: {response.status_code}")
                print(f"Final URL: {response.url}")
                if response.status_code == 419:
                    print("CSRF token validation failed. The session may have expired.")
                elif response.status_code == 422:
                    print("Validation error. Please check your credentials.")
                
                # Print first 500 characters of response for debugging
                print("Response content (first 500 chars):")
                print(response.text[:500])
                
                # If we have credentials saved, they might be invalid
                if os.path.exists(CREDENTIALS_FILE):
                    print("\nStored credentials might be invalid. Please re-enter your credentials.")
                    os.remove(CREDENTIALS_FILE)
                    return login_to_chartink(session, None, None, max_retries)
                    
        except Exception as e:
            print(f"Error during login attempt {attempt + 1}: {str(e)}")
            
        if attempt < max_retries - 1:
            wait_time = 5 * (attempt + 1)  # Exponential backoff
            print(f"Retrying in {wait_time} seconds... (Attempt {attempt + 2}/{max_retries})")
            time.sleep(wait_time)
    
    print("\nFailed to login after multiple attempts. Please check your credentials and try again.")
    return False

def fetch_screener_results(session, config):
    """Fetch results from a specific screener"""
    try:
        print(f"\nFetching data from: {config['name']}")
        
        # Set headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': 'https://chartink.com/screener/technical'
        }
        
        # Make the request
        response = session.post(
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
    print("Starting Chartink Screener Data Relay...")
    print("Available screeners:")
    for key, config in SCREENER_CONFIGS.items():
        print(f"- {key}: {config['name']}")
    print(f"\nPosting to: {LOCAL_URL}")
    print("Press Ctrl+C to stop\n")
    
    # Set up session
    session = requests.Session()
    
    # Load credentials
    credentials = load_credentials()
    email = credentials.get('email') if credentials else None
    password = credentials.get('password') if credentials else None
    
    try:
        # Login to Chartink
        if not login_to_chartink(session, email, password):
            print("Failed to login. Exiting...")
            return
        
        # Store last results for each screener
        last_results = {key: None for key in SCREENER_CONFIGS.keys()}
        
        while True:
            print("\n" + "="*50)
            print(f"Checking for new data at {time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Check each configured screener
            for screener_key, config in SCREENER_CONFIGS.items():
                print(f"\nChecking {config['name']}...")
                
                # Fetch new results
                current_results = fetch_screener_results(session, config)
                
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
        print("\nStopping Chartink Screener Data Relay...")
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
