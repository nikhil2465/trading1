import time
import json
import os
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from getpass import getpass

# Configuration
SCREENER_CONFIGS = {
    'bollinger_rsi_lower': {
        'url': 'https://chartink.com/screener/price-below-lower-bollinger-band-rsi-below-30',
        'name': 'Bollinger Lower Band & RSI < 30'
    },
    'rsi_70_upper_bb': {
        'url': 'https://chartink.com/screener/rsi-70-upper-bb',
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
    """Save credentials to file"""
    try:
        with open(CREDENTIALS_FILE, 'w') as f:
            json.dump({"email": email, "password": password}, f)
    except Exception as e:
        print(f"Warning: Could not save credentials: {str(e)}")

def setup_driver():
    """Set up undetected Chrome WebDriver with options"""
    print("Setting up undetected Chrome WebDriver...")
    
    # Configure Chrome options
    options = uc.ChromeOptions()
    
    # Add arguments to make Chrome less detectable
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-notifications')
    options.add_argument('--no-first-run')
    options.add_argument('--no-service-autorun')
    options.add_argument('--password-store=basic')
    options.add_argument('--start-maximized')
    
    # Disable automation flags that expose WebDriver
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    try:
        # Initialize undetected ChromeDriver
        driver = uc.Chrome(
            options=options,
            use_subprocess=True,
            headless=False,  # Start with visible browser for debugging
            version_main=None  # Automatically find the Chrome version
        )
        
        # Execute CDP commands to further avoid detection
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                window.navigator.chrome = {
                    runtime: {},
                    // etc.
                };
            """
        })
        
        # Set a normal user agent
        driver.execute_cdp_cmd("Network.setUserAgentOverride", {
            "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })
        
        print("WebDriver setup complete")
        return driver
        
    except Exception as e:
        print(f"Error setting up WebDriver: {str(e)}")
        raise

def login_to_chartink(driver, email=None, password=None):
    """Login to Chartink using Selenium"""
    if not email or not password:
        print("\n=== Chartink Login Required ===")
        email = input("Enter your Chartink email: ")
        password = getpass("Enter your Chartink password: ")
        
        # Save credentials for next time
        save_credentials(email, password)
    
    print("\nLogging in to Chartink...")
    
    try:
        # Go to login page
        driver.get("https://chartink.com/login")
        
        # Wait for the login form to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "email"))
        )
        
        # Find and fill in the login form
        email_field = driver.find_element(By.NAME, "email")
        password_field = driver.find_element(By.NAME, "password")
        
        email_field.clear()
        email_field.send_keys(email)
        password_field.clear()
        password_field.send_keys(password)
        
        # Find and click the login button
        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        login_button.click()
        
        # Wait for login to complete (check for dashboard or error)
        try:
            WebDriverWait(driver, 10).until(
                lambda d: "dashboard" in d.current_url or 
                         d.find_elements(By.CLASS_NAME, "alert-danger")
            )
            
            # Check if login was successful
            if "dashboard" in driver.current_url:
                print("Successfully logged in to Chartink")
                return True
            else:
                # Check for error message
                error_elements = driver.find_elements(By.CLASS_NAME, "alert-danger")
                if error_elements:
                    print(f"Login failed: {error_elements[0].text}")
                else:
                    print("Login failed. Unknown error.")
                return False
                
        except Exception as e:
            print(f"Login attempt failed: {str(e)}")
            return False
            
    except Exception as e:
        print(f"Error during login: {str(e)}")
        return False

def fetch_screener_results(driver, config):
    """Fetch results from a specific screener"""
    try:
        print(f"\nFetching data from: {config['name']}")
        driver.get(config['url'])
        
        # Wait for the results to load
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table.dataTable"))
        )
        
        # Find the table with results
        table = driver.find_element(By.CSS_SELECTOR, "table.dataTable")
        rows = table.find_elements(By.TAG_NAME, "tr")
        
        # Extract headers
        headers = [th.text for th in rows[0].find_elements(By.TAG_NAME, "th")]
        
        # Extract data rows
        results = []
        for row in rows[1:]:  # Skip header row
            cells = row.find_elements(By.TAG_NAME, "td")
            if cells:  # Make sure it's a data row
                row_data = {headers[i]: cell.text for i, cell in enumerate(cells)}
                results.append(row_data)
        
        print(f"Found {len(results)} results")
        return results
        
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
    print("Starting Chartink Screener Data Relay with Selenium...")
    print("Available screeners:")
    for key, config in SCREENER_CONFIGS.items():
        print(f"- {key}: {config['name']}")
    print(f"\nPosting to: {LOCAL_URL}")
    print("Press Ctrl+C to stop\n")
    
    # Load credentials
    credentials = load_credentials()
    email = credentials.get('email') if credentials else None
    password = credentials.get('password') if credentials else None
    
    # Set up the WebDriver
    driver = setup_driver()
    
    try:
        # Login to Chartink
        if not login_to_chartink(driver, email, password):
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
                current_results = fetch_screener_results(driver, config)
                
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
    finally:
        # Close the browser
        driver.quit()

if __name__ == "__main__":
    main()
