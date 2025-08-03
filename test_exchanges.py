import asyncio
import os
from dotenv import load_dotenv
from src.exchanges import BinanceExchange, BybitExchange
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


async def test_exchange(exchange, name):
    """Test basic exchange functionality"""
    logger.info(f"\n{'='*50}")
    logger.info(f"Testing {name}")
    logger.info(f"{'='*50}")
    
    try:
        # Connect to exchange
        await exchange.connect()
        logger.info(f"✓ Connected to {name}")
        
        # Test getting ticker
        symbol = 'BTC/USDT'
        ticker = await exchange.get_ticker(symbol)
        logger.info(f"✓ {symbol} Ticker - Bid: {ticker['bid']}, Ask: {ticker['ask']}, Last: {ticker['last']}")
        
        # Test getting order book
        order_book = await exchange.get_order_book(symbol, limit=5)
        logger.info(f"✓ Order Book - Top Bid: {order_book['bids'][0][0] if order_book['bids'] else 'N/A'}, "
                   f"Top Ask: {order_book['asks'][0][0] if order_book['asks'] else 'N/A'}")
        
        # Test getting balance
        balance_usdt = await exchange.get_balance('USDT')
        balance_btc = await exchange.get_balance('BTC')
        logger.info(f"✓ Balances - USDT: {balance_usdt}, BTC: {balance_btc}")
        
        # Test getting fees
        maker_fee, taker_fee = await exchange.get_trading_fees(symbol)
        logger.info(f"✓ Fees - Maker: {maker_fee*100}%, Taker: {taker_fee*100}%")
        
    except Exception as e:
        logger.error(f"✗ Error testing {name}: {e}")
    finally:
        await exchange.disconnect()
        logger.info(f"✓ Disconnected from {name}")


async def main():
    """Test both exchanges"""
    
    # Check if API keys are set
    if os.getenv('BINANCE_API_KEY') == 'your_binance_testnet_api_key':
        logger.warning("Please set your actual API keys in the .env file!")
        logger.info("Edit .env and add your:")
        logger.info("- Binance testnet API key and secret")
        logger.info("- Bybit testnet API key and secret")
        return
    
    # Test Binance
    if os.getenv('BINANCE_API_KEY'):
        binance = BinanceExchange(
            api_key=os.getenv('BINANCE_API_KEY'),
            secret_key=os.getenv('BINANCE_SECRET_KEY'),
            testnet=True
        )
        await test_exchange(binance, "Binance Testnet")
    
    # Test Bybit
    if os.getenv('BYBIT_API_KEY'):
        bybit = BybitExchange(
            api_key=os.getenv('BYBIT_API_KEY'),
            secret_key=os.getenv('BYBIT_SECRET_KEY'),
            testnet=True
        )
        await test_exchange(bybit, "Bybit Testnet")
    
    # Show arbitrage opportunity example
    logger.info(f"\n{'='*50}")
    logger.info("Arbitrage Opportunity Example")
    logger.info(f"{'='*50}")
    logger.info("If BTC/USDT on Binance: Bid=45000, Ask=45010")
    logger.info("If BTC/USDT on Bybit: Bid=45020, Ask=45030")
    logger.info("Opportunity: Buy on Binance at 45010, Sell on Bybit at 45020")
    logger.info("Profit (before fees): $10 per BTC")


if __name__ == "__main__":
    asyncio.run(main())