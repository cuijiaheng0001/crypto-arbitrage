import ccxt
import asyncio
from decimal import Decimal
from typing import Dict, List, Optional, Tuple
from .base_exchange import BaseExchange
import logging

logger = logging.getLogger(__name__)


class BinanceExchange(BaseExchange):
    """Binance exchange implementation using ccxt"""
    
    def __init__(self, api_key: str, secret_key: str, testnet: bool = True):
        super().__init__(api_key, secret_key, testnet)
        
        # Configure exchange
        exchange_config = {
            'apiKey': api_key,
            'secret': secret_key,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot',
            }
        }
        
        if testnet:
            exchange_config['urls'] = {
                'api': {
                    'fapiPublic': 'https://testnet.binance.vision/fapi',
                    'fapiPrivate': 'https://testnet.binance.vision/fapi',
                    'public': 'https://testnet.binance.vision/api',
                    'private': 'https://testnet.binance.vision/api',
                    'sapi': 'https://testnet.binance.vision/sapi',
                }
            }
            exchange_config['hostname'] = 'testnet.binance.vision'
        
        self.exchange = ccxt.binance(exchange_config)
        
    async def connect(self):
        """Initialize connection to Binance"""
        try:
            await self.exchange.load_markets()
            logger.info(f"Connected to Binance {'testnet' if self.testnet else 'mainnet'}")
        except Exception as e:
            logger.error(f"Failed to connect to Binance: {e}")
            raise
    
    async def disconnect(self):
        """Close connection to Binance"""
        # ccxt doesn't have close method for spot trading
        logger.info("Disconnected from Binance")
    
    async def get_balance(self, asset: str) -> Decimal:
        """Get balance for a specific asset"""
        try:
            balance = await self.exchange.fetch_balance()
            return Decimal(str(balance.get(asset, {}).get('free', 0)))
        except Exception as e:
            logger.error(f"Failed to get balance for {asset}: {e}")
            raise
    
    async def get_ticker(self, symbol: str) -> Dict:
        """Get current ticker data for a symbol"""
        try:
            ticker = await self.exchange.fetch_ticker(symbol)
            return {
                'symbol': symbol,
                'bid': Decimal(str(ticker['bid'])) if ticker['bid'] else Decimal('0'),
                'ask': Decimal(str(ticker['ask'])) if ticker['ask'] else Decimal('0'),
                'last': Decimal(str(ticker['last'])) if ticker['last'] else Decimal('0'),
                'volume': Decimal(str(ticker['baseVolume'])) if ticker['baseVolume'] else Decimal('0'),
                'timestamp': ticker['timestamp']
            }
        except Exception as e:
            logger.error(f"Failed to get ticker for {symbol}: {e}")
            raise
    
    async def get_order_book(self, symbol: str, limit: int = 10) -> Dict:
        """Get order book for a symbol"""
        try:
            order_book = await self.exchange.fetch_order_book(symbol, limit)
            return {
                'bids': [(Decimal(str(price)), Decimal(str(amount))) for price, amount in order_book['bids']],
                'asks': [(Decimal(str(price)), Decimal(str(amount))) for price, amount in order_book['asks']],
                'timestamp': order_book['timestamp']
            }
        except Exception as e:
            logger.error(f"Failed to get order book for {symbol}: {e}")
            raise
    
    async def place_order(
        self, 
        symbol: str, 
        side: str, 
        order_type: str, 
        quantity: Decimal, 
        price: Optional[Decimal] = None
    ) -> Dict:
        """Place an order on Binance"""
        try:
            params = {}
            if order_type == 'limit' and price:
                order = await self.exchange.create_limit_order(
                    symbol, side, float(quantity), float(price), params
                )
            else:
                order = await self.exchange.create_market_order(
                    symbol, side, float(quantity), params
                )
            
            return {
                'id': order['id'],
                'symbol': order['symbol'],
                'side': order['side'],
                'type': order['type'],
                'quantity': Decimal(str(order['amount'])),
                'price': Decimal(str(order['price'])) if order['price'] else None,
                'status': order['status'],
                'timestamp': order['timestamp']
            }
        except Exception as e:
            logger.error(f"Failed to place order: {e}")
            raise
    
    async def cancel_order(self, symbol: str, order_id: str) -> bool:
        """Cancel an existing order"""
        try:
            result = await self.exchange.cancel_order(order_id, symbol)
            return result['status'] == 'canceled'
        except Exception as e:
            logger.error(f"Failed to cancel order {order_id}: {e}")
            raise
    
    async def get_order_status(self, symbol: str, order_id: str) -> Dict:
        """Get status of a specific order"""
        try:
            order = await self.exchange.fetch_order(order_id, symbol)
            return {
                'id': order['id'],
                'status': order['status'],
                'filled': Decimal(str(order['filled'])),
                'remaining': Decimal(str(order['remaining'])),
                'price': Decimal(str(order['price'])) if order['price'] else None,
                'average_price': Decimal(str(order['average'])) if order['average'] else None
            }
        except Exception as e:
            logger.error(f"Failed to get order status for {order_id}: {e}")
            raise
    
    async def get_trading_fees(self, symbol: str) -> Tuple[Decimal, Decimal]:
        """Get maker and taker fees for a symbol"""
        try:
            # Binance default fees (may vary by user level)
            # You might want to fetch actual fees from API if available
            maker_fee = Decimal('0.001')  # 0.1%
            taker_fee = Decimal('0.001')  # 0.1%
            return maker_fee, taker_fee
        except Exception as e:
            logger.error(f"Failed to get trading fees for {symbol}: {e}")
            raise