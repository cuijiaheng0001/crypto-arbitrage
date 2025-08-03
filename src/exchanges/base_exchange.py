from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple
import asyncio
from decimal import Decimal


class BaseExchange(ABC):
    """Base class for all exchange implementations"""
    
    def __init__(self, api_key: str, secret_key: str, testnet: bool = True):
        self.api_key = api_key
        self.secret_key = secret_key
        self.testnet = testnet
        self.name = self.__class__.__name__
        
    @abstractmethod
    async def connect(self):
        """Initialize connection to the exchange"""
        pass
    
    @abstractmethod
    async def disconnect(self):
        """Close connection to the exchange"""
        pass
    
    @abstractmethod
    async def get_balance(self, asset: str) -> Decimal:
        """Get balance for a specific asset"""
        pass
    
    @abstractmethod
    async def get_ticker(self, symbol: str) -> Dict:
        """Get current ticker data for a symbol"""
        pass
    
    @abstractmethod
    async def get_order_book(self, symbol: str, limit: int = 10) -> Dict:
        """Get order book for a symbol"""
        pass
    
    @abstractmethod
    async def place_order(
        self, 
        symbol: str, 
        side: str, 
        order_type: str, 
        quantity: Decimal, 
        price: Optional[Decimal] = None
    ) -> Dict:
        """Place an order on the exchange"""
        pass
    
    @abstractmethod
    async def cancel_order(self, symbol: str, order_id: str) -> bool:
        """Cancel an existing order"""
        pass
    
    @abstractmethod
    async def get_order_status(self, symbol: str, order_id: str) -> Dict:
        """Get status of a specific order"""
        pass
    
    @abstractmethod
    async def get_trading_fees(self, symbol: str) -> Tuple[Decimal, Decimal]:
        """Get maker and taker fees for a symbol"""
        pass
    
    def calculate_profit(
        self, 
        buy_price: Decimal, 
        sell_price: Decimal, 
        quantity: Decimal, 
        buy_fee: Decimal, 
        sell_fee: Decimal
    ) -> Decimal:
        """Calculate profit from arbitrage opportunity"""
        buy_cost = buy_price * quantity * (1 + buy_fee)
        sell_revenue = sell_price * quantity * (1 - sell_fee)
        return sell_revenue - buy_cost