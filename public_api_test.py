import ccxt

def test_public_apis():
    print("Testing Public APIs (No Authentication Required)...\n")
    
    # Test Binance Testnet
    print("=== Binance Testnet ===")
    try:
        binance = ccxt.binance({
            'enableRateLimit': True,
            'urls': {
                'api': {
                    'public': 'https://testnet.binance.vision/api',
                }
            }
        })
        
        ticker = binance.fetch_ticker('BTC/USDT')
        print(f"✓ BTC/USDT Last Price: ${ticker['last']}")
        print(f"✓ Bid: ${ticker['bid']}, Ask: ${ticker['ask']}")
        print(f"✓ 24h Volume: {ticker['baseVolume']} BTC")
    except Exception as e:
        print(f"✗ Error: {str(e)}")
    
    # Test Bybit Testnet
    print("\n=== Bybit Testnet ===")
    try:
        bybit = ccxt.bybit({
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot',
            },
            'hostname': 'testnet.bybit.com',
        })
        
        ticker = bybit.fetch_ticker('BTC/USDT')
        print(f"✓ BTC/USDT Last Price: ${ticker['last']}")
        print(f"✓ Bid: ${ticker['bid']}, Ask: ${ticker['ask']}")
        print(f"✓ 24h Volume: {ticker['baseVolume']} BTC")
    except Exception as e:
        print(f"✗ Error: {str(e)}")
    
    # Calculate potential arbitrage
    print("\n=== Arbitrage Opportunity ===")
    print("If prices differ between exchanges, you can:")
    print("1. Buy on the exchange with lower ask price")
    print("2. Transfer to the exchange with higher bid price")
    print("3. Sell for profit (minus fees and transfer costs)")

if __name__ == "__main__":
    test_public_apis()