import ccxt
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_binance():
    print("\n=== Testing Binance Testnet ===")
    try:
        exchange = ccxt.binance({
            'apiKey': os.getenv('BINANCE_API_KEY'),
            'secret': os.getenv('BINANCE_SECRET_KEY'),
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot',
                'recvWindow': 60000,
            },
            'urls': {
                'api': {
                    'public': 'https://testnet.binance.vision/api',
                    'private': 'https://testnet.binance.vision/api',
                }
            }
        })
        
        # Test public API (no authentication needed)
        ticker = exchange.fetch_ticker('BTC/USDT')
        print(f"✓ BTC/USDT Price: ${ticker['last']}")
        
        # Test private API
        try:
            balance = exchange.fetch_balance()
            usdt_balance = balance['USDT']['free'] if 'USDT' in balance else 0
            btc_balance = balance['BTC']['free'] if 'BTC' in balance else 0
            print(f"✓ USDT Balance: {usdt_balance}")
            print(f"✓ BTC Balance: {btc_balance}")
        except Exception as e:
            print(f"✗ Private API Error: {str(e)[:100]}...")
            
    except Exception as e:
        print(f"✗ Error: {str(e)[:100]}...")

def test_bybit():
    print("\n=== Testing Bybit Testnet ===")
    try:
        exchange = ccxt.bybit({
            'apiKey': os.getenv('BYBIT_API_KEY'),
            'secret': os.getenv('BYBIT_SECRET_KEY'),
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot',
            },
            'hostname': 'testnet.bybit.com',
        })
        
        # Test public API
        ticker = exchange.fetch_ticker('BTC/USDT')
        print(f"✓ BTC/USDT Price: ${ticker['last']}")
        
        # Test private API
        try:
            balance = exchange.fetch_balance()
            usdt_balance = balance['USDT']['free'] if 'USDT' in balance else 0
            btc_balance = balance['BTC']['free'] if 'BTC' in balance else 0
            print(f"✓ USDT Balance: {usdt_balance}")
            print(f"✓ BTC Balance: {btc_balance}")
        except Exception as e:
            print(f"✗ Private API Error: {str(e)[:100]}...")
            
    except Exception as e:
        print(f"✗ Error: {str(e)[:100]}...")

if __name__ == "__main__":
    print("Testing Exchange Connections...")
    test_binance()
    test_bybit()
    print("\n✓ Test completed!")