import asyncio
import time
import requests
import hmac
import hashlib
from urllib.parse import urlencode
from decimal import Decimal
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class BinanceTestnetExchange:
    """Binance Testnet 专用实现"""
    
    def __init__(self, api_key: str, secret_key: str):
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = 'https://testnet.binance.vision'
        self.session = requests.Session()
        self.session.headers.update({
            'X-MBX-APIKEY': api_key
        })
        
    def _sign_request(self, params: dict) -> dict:
        """签名请求"""
        params['timestamp'] = int(time.time() * 1000)
        params['recvWindow'] = 5000
        
        query_string = urlencode(params)
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        params['signature'] = signature
        return params
    
    async def connect(self):
        """测试连接"""
        try:
            # 测试公共端点
            response = self.session.get(f'{self.base_url}/api/v3/ping')
            response.raise_for_status()
            
            # 测试账户端点
            params = self._sign_request({})
            response = self.session.get(
                f'{self.base_url}/api/v3/account',
                params=params
            )
            response.raise_for_status()
            
            logger.info("✅ 成功连接到 Binance 测试网")
            
        except Exception as e:
            logger.error(f"连接 Binance 测试网失败: {e}")
            raise
    
    async def get_ticker(self, symbol: str) -> Dict:
        """获取价格"""
        try:
            # 转换符号格式 BTC/USDT -> BTCUSDT
            binance_symbol = symbol.replace('/', '')
            
            # 获取订单簿
            response = self.session.get(
                f'{self.base_url}/api/v3/depth',
                params={'symbol': binance_symbol, 'limit': 5}
            )
            response.raise_for_status()
            
            data = response.json()
            
            # 获取最佳买卖价
            best_bid = float(data['bids'][0][0]) if data['bids'] else 0
            best_ask = float(data['asks'][0][0]) if data['asks'] else 0
            
            return {
                'bid': best_bid,
                'ask': best_ask,
                'symbol': symbol,
                'timestamp': time.time()
            }
            
        except Exception as e:
            logger.error(f"获取 {symbol} 价格失败: {e}")
            raise
    
    async def get_balance(self) -> Dict:
        """获取余额"""
        try:
            params = self._sign_request({})
            response = self.session.get(
                f'{self.base_url}/api/v3/account',
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            balances = {}
            
            for asset in data['balances']:
                free = float(asset['free'])
                locked = float(asset['locked'])
                if free > 0 or locked > 0:
                    balances[asset['asset']] = {
                        'free': free,
                        'locked': locked,
                        'total': free + locked
                    }
            
            return balances
            
        except Exception as e:
            logger.error(f"获取余额失败: {e}")
            raise
    
    async def place_order(self, symbol: str, side: str, amount: float, price: float):
        """下单（测试网）"""
        try:
            binance_symbol = symbol.replace('/', '')
            
            params = {
                'symbol': binance_symbol,
                'side': side.upper(),
                'type': 'LIMIT',
                'timeInForce': 'GTC',
                'quantity': f"{amount:.8f}",
                'price': f"{price:.2f}"
            }
            
            params = self._sign_request(params)
            
            response = self.session.post(
                f'{self.base_url}/api/v3/order',
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"✅ 订单已提交: {data['orderId']}")
            return data
            
        except Exception as e:
            logger.error(f"下单失败: {e}")
            raise
    
    async def disconnect(self):
        """关闭连接"""
        self.session.close()