import time
import yfinance as yf
import pandas as pd
import requests
import ta  # Using ta library instead of pandas_ta
import json
import numpy as np
from datetime import datetime, timedelta

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj) if not (np.isnan(obj) or np.isinf(obj)) else 0.0
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

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
        'name': 'Enhanced NIFTY 50 Analysis'
    }
}

LOCAL_URL = "http://127.0.0.1:5000/create_scan/data"

def get_historical_data(ticker, period="1mo", interval="1d"):
    """Fetch historical data for technical analysis"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period, interval=interval)
        return hist
    except Exception as e:
        print(f"Error fetching historical data for {ticker}: {str(e)}")
        return None

def calculate_technicals(df):
    """Calculate technical indicators using ta library"""
    try:
        # Ensure we have enough data
        if len(df) < 21:  # Need at least 21 days for SMA20
            return df
            
        # Initialize indicators
        df['SMA20'] = ta.trend.sma_indicator(df['Close'], window=20)
        df['SMA50'] = ta.trend.sma_indicator(df['Close'], window=50)
        df['SMA200'] = ta.trend.sma_indicator(df['Close'], window=200)
        
        # RSI
        df['RSI'] = ta.momentum.RSIIndicator(df['Close']).rsi()
        
        # MACD
        macd = ta.trend.MACD(df['Close'])
        df['MACD'] = macd.macd()
        df['MACD_Signal'] = macd.macd_signal()
        
        # Bollinger Bands
        bollinger = ta.volatility.BollingerBands(df['Close'])
        df['BB_High'] = bollinger.bollinger_hband()
        df['BB_Low'] = bollinger.bollinger_lband()
        
        # ATR
        df['ATR'] = ta.volatility.average_true_range(df['High'], df['Low'], df['Close'])
        
        return df
    except Exception as e:
        print(f"Error calculating technicals: {str(e)}")
        return df

def analyze_stock(ticker):
    """Analyze a single stock with technical indicators"""
    try:
        # Get historical data
        hist = get_historical_data(ticker)
        if hist is None or hist.empty:
            return None
            
        # Calculate technicals
        hist = calculate_technicals(hist)
        
        # Get latest values
        latest = hist.iloc[-1]
        prev = hist.iloc[-2] if len(hist) > 1 else latest
        
        # Prepare analysis
        analysis = {
            'symbol': ticker.replace('.NS', ''),
            'name': ticker.replace('.NS', ''),
            'close': round(latest['Close'], 2),
            'prev_close': round(prev['Close'], 2) if len(hist) > 1 else round(latest['Close'], 2),
            'change_pct': round(((latest['Close'] / prev['Close']) - 1) * 100, 2) if len(hist) > 1 else 0,
            'volume': int(latest['Volume']),
            'rsi': round(latest.get('RSI', 0), 2),
            'sma20': round(latest.get('SMA20', 0), 2),
            'sma50': round(latest.get('SMA50', 0), 2),
            'sma200': round(latest.get('SMA200', 0), 2),
            'macd': round(latest.get('MACD', 0), 2),
            'macd_signal': round(latest.get('MACD_Signal', 0), 2),
            'bb_upper': round(latest.get('BB_High', 0), 2),
            'bb_lower': round(latest.get('BB_Low', 0), 2),
            'atr': round(latest.get('ATR', 0), 2),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Generate signals
        analysis['trend'] = 'Uptrend' if analysis['sma20'] > analysis['sma50'] > analysis['sma200'] else 'Downtrend' if analysis['sma20'] < analysis['sma50'] < analysis['sma200'] else 'Neutral'
        analysis['rsi_signal'] = 'Oversold' if analysis['rsi'] < 30 else 'Overbought' if analysis['rsi'] > 70 else 'Neutral'
        analysis['macd_signal'] = 'Bullish' if analysis['macd'] > analysis['macd_signal'] else 'Bearish' if analysis['macd'] < analysis['macd_signal'] else 'Neutral'
        
        return analysis
        
    except Exception as e:
        print(f"Error analyzing {ticker}: {str(e)}")
        return None

def fetch_market_data(tickers):
    """Fetch enhanced market data with technical analysis"""
    results = []
    for ticker in tickers:
        analysis = analyze_stock(ticker)
        if analysis:
            results.append(analysis)
        time.sleep(0.5)  # Rate limiting
    return results

def clean_numpy_values(obj):
    """Recursively clean numpy values for JSON serialization"""
    import numpy as np
    if isinstance(obj, (np.generic, np.ndarray)):
        return obj.item() if obj.size == 1 else [clean_numpy_values(x) for x in obj]
    elif isinstance(obj, dict):
        return {k: clean_numpy_values(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [clean_numpy_values(x) for x in obj]
    elif isinstance(obj, float) and (np.isnan(obj) or np.isinf(obj)):
        return 0.0
    return obj

def post_to_local(data, screener_name):
    """Post results to local Flask app"""
    try:
        # Format data to match existing endpoint
        formatted_data = []
        for item in data:
            # Clean all values in the item
            clean_item = {
                'nsecode': item['symbol'],
                'name': item['name'],
                'close': float(item['close']) if not (pd.isna(item['close']) or np.isinf(item['close'])) else 0.0,
                'per_chg': float(item['change_pct']) if not (pd.isna(item['change_pct']) or np.isinf(item['change_pct'])) else 0.0,
                'volume': int(item['volume']) if not (pd.isna(item['volume']) or np.isinf(item['volume'])) else 0,
                'rsi': float(item['rsi']) if not (pd.isna(item['rsi']) or np.isinf(item['rsi'])) else 0.0,
                'trend': str(item['trend']),
                'rsi_signal': str(item['rsi_signal']),
                'macd_signal': str(item['macd_signal']),
                'sma20': float(item['sma20']) if not (pd.isna(item['sma20']) or np.isinf(item['sma20'])) else 0.0,
                'sma50': float(item['sma50']) if not (pd.isna(item['sma50']) or np.isinf(item['sma50'])) else 0.0,
                'sma200': float(item['sma200']) if not (pd.isna(item['sma200']) or np.isinf(item['sma200'])) else 0.0
            }
            formatted_data.append(clean_item)
            
        payload = {
            'results': formatted_data,
            'screener_name': screener_name,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Convert to JSON string using our custom encoder
        headers = {'Content-Type': 'application/json'}
        json_payload = json.dumps(payload, cls=NpEncoder)
        response = requests.post(LOCAL_URL, data=json_payload, headers=headers)
        response.raise_for_status()
        print(f"Successfully posted {len(data)} results to {LOCAL_URL}")
        return True
    except Exception as e:
        print(f"Error posting to local app: {str(e)}")
        return False

def main():
    print("Starting Enhanced Market Data Relay...")
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
            print(f"Checking for new data at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Check each configured screener
            for screener_key, config in SCREENER_CONFIGS.items():
                print(f"\nAnalyzing {config['name']}...")
                
                # Fetch new results with technical analysis
                current_results = fetch_market_data(config['tickers'])
                
                if current_results:
                    if current_results != last_results.get(screener_key):
                        print(f"New analysis available for {config['name']}!")
                        if post_to_local(current_results, config['name']):
                            last_results[screener_key] = current_results
                    else:
                        print(f"No new data in {config['name']} since last check.")
                else:
                    print(f"No valid results from {config['name']}.")
            
            # Wait before next check (5 minutes between full cycles)
            wait_time = 300  # 5 minutes
            print(f"\nNext check in {wait_time//60} minutes...")
            time.sleep(wait_time)
            
    except KeyboardInterrupt:
        print("\nStopping Enhanced Market Data Relay...")
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        import traceback
        traceback.print_exc()

def install_required_packages():
    """Install required Python packages"""
    import sys
    import subprocess
    import importlib.metadata
    
    required_packages = {
        'pandas': 'pandas',
        'yfinance': 'yfinance',
        'requests': 'requests',
        'ta': 'ta'
    }
    
    print("Checking for required packages...")
    for package_name, import_name in required_packages.items():
        try:
            importlib.import_module(import_name if import_name != 'pandas_ta' else 'pandas_ta')
            print(f"✓ {package_name} is already installed")
        except ImportError:
            print(f"Installing {package_name}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])

if __name__ == "__main__":
    # Install required packages if not already installed
    install_required_packages()
    
    # Now run the main function
    main()
