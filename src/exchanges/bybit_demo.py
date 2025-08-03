import asyncio
import time
import requests
import hmac
import hashlib
import json
from urllib.parse import urlencode
from decimal import Decimal
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class BybitDemoExchange:
    """Bybit Demo Trading 实现"""
    
    def __init__(self, api_key: str, secret_key: str):
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = 'https://api-demo.bybit.com'  # Demo Trading 端点
        self.session = requests.Session()
        self.recv_window = '5000'
        
    def _generate_signature(self, params_str: str) -> str:
        """生成签名"""
        return hmac.new(
            self.secret_key.encode('utf-8'),
            params_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def _prepare_request(self, method: str, endpoint: str, params: dict = None) -> tuple:
        """准备请求"""
        timestamp = str(int(time.time() * 1000))
        
        if method == 'GET' and params:
            # GET 请求：参数在 query string 中
            query_string = urlencode(sorted(params.items()))
            sign_str = f"{timestamp}{self.api_key}{self.recv_window}{query_string}"
            signature = self._generate_signature(sign_str)
            
            headers = {
                'X-BAPI-KEY': self.api_key,
                'X-BAPI-SIGN': signature,
                'X-BAPI-TIMESTAMP': timestamp,
                'X-BAPI-RECV-WINDOW': self.recv_window
            }
            
            return f"{self.base_url}{endpoint}?{query_string}", headers, None
            
        else:
            # POST 请求：参数在 body 中
            body_str = json.dumps(params) if params else ''
            sign_str = f"{timestamp}{self.api_key}{self.recv_window}{body_str}"
            signature = self._generate_signature(sign_str)
            
            headers = {
                'X-BAPI-KEY': self.api_key,
                'X-BAPI-SIGN': signature,
                'X-BAPI-TIMESTAMP': timestamp,
                'X-BAPI-RECV-WINDOW': self.recv_window,
                'Content-Type': 'application/json'
            }
            
            return f"{self.base_url}{endpoint}", headers, body_str
    
    async def connect(self):
        """测试连接"""
        try:
            # 测试服务器时间
            response = self.session.get(f'{self.base_url}/v5/market/time')
            data = response.json()
            
            if data['retCode'] == 0:
                logger.info(f"✅ 连接到 Bybit Demo Trading")
                
                # 测试账户信息
                url, headers, _ = self._prepare_request('GET', '/v5/account/wallet-balance', {
                    'accountType': 'UNIFIED'
                })
                
                response = self.session.get(url, headers=headers)
                data = response.json()
                
                if data['retCode'] == 0:
                    logger.info("✅ API 密钥验证成功")
                else:
                    raise Exception(f"API 验证失败: {data}")
            else:
                raise Exception(f"连接失败: {data}")
                
        except Exception as e:
            logger.error(f"连接 Bybit Demo 失败: {e}")
            raise
    
    async def get_ticker(self, symbol: str) -> Dict:
        """获取价格"""
        try:
            # 转换符号格式 BTC/USDT -> BTCUSDT
            bybit_symbol = symbol.replace('/', '')
            
            # 获取最新价格
            response = self.session.get(
                f'{self.base_url}/v5/market/tickers',
                params={'category': 'spot', 'symbol': bybit_symbol}
            )
            
            data = response.json()
            
            if data['retCode'] == 0 and data['result']['list']:
                ticker_data = data['result']['list'][0]
                
                return {
                    'bid': float(ticker_data['bid1Price']),
                    'ask': float(ticker_data['ask1Price']),
                    'last': float(ticker_data['lastPrice']),
                    'symbol': symbol,
                    'timestamp': int(data['time'])
                }
            else:
                raise Exception(f"获取价格失败: {data}")
                
        except Exception as e:
            logger.error(f"获取 {symbol} 价格失败: {e}")
            raise
    
    async def get_balance(self) -> Dict:
        """获取余额"""
        try:
            url, headers, _ = self._prepare_request('GET', '/v5/account/wallet-balance', {
                'accountType': 'UNIFIED'
            })
            
            response = self.session.get(url, headers=headers)
            data = response.json()
            
            if data['retCode'] == 0:
                balances = {}
                
                if 'list' in data['result'] and len(data['result']['list']) > 0:
                    account = data['result']['list'][0]
                    
                    # 获取所有币种余额
                    for coin_data in account.get('coin', []):
                        coin = coin_data['coin']
                        balances[coin] = {
                            'free': float(coin_data.get('walletBalance', 0)),
                            'locked': float(coin_data.get('locked', 0)),
                            'total': float(coin_data.get('walletBalance', 0))
                        }
                
                return balances
            else:
                raise Exception(f"获取余额失败: {data}")
                
        except Exception as e:
            logger.error(f"获取余额失败: {e}")
            raise
    
    async def place_order(self, symbol: str, side: str, amount: float, price: float):
        """下单"""
        try:
            bybit_symbol = symbol.replace('/', '')
            
            # 准备订单参数
            order_params = {
                'category': 'spot',
                'symbol': bybit_symbol,
                'side': side.capitalize(),
                'orderType': 'Limit',
                'qty': str(amount),
                'price': str(price),
                'timeInForce': 'GTC'
            }
            
            url, headers, body = self._prepare_request('POST', '/v5/order/create', order_params)
            
            response = self.session.post(url, headers=headers, data=body)
            data = response.json()
            
            if data['retCode'] == 0:
                order_id = data['result']['orderId']
                logger.info(f"✅ 订单已提交: {order_id}")
                return {
                    'orderId': order_id,
                    'symbol': symbol,
                    'side': side,
                    'amount': amount,
                    'price': price,
                    'status': 'new'
                }
            else:
                raise Exception(f"下单失败: {data}")
                
        except Exception as e:
            logger.error(f"下单失败: {e}")
            raise
    
    async def get_order_status(self, order_id: str, symbol: str = None):
        """查询订单状态"""
        try:
            params = {
                'category': 'spot',
                'orderId': order_id
            }
            
            if symbol:
                params['symbol'] = symbol.replace('/', '')
            
            url, headers, _ = self._prepare_request('GET', '/v5/order/realtime', params)
            
            response = self.session.get(url, headers=headers)
            data = response.json()
            
            if data['retCode'] == 0 and data['result']['list']:
                order = data['result']['list'][0]
                return {
                    'orderId': order['orderId'],
                    'status': order['orderStatus'],
                    'filled': float(order.get('cumExecQty', 0)),
                    'remaining': float(order.get('leavesQty', 0))
                }
            else:
                return None
                
        except Exception as e:
            logger.error(f"查询订单失败: {e}")
            return None
    
    async def cancel_order(self, order_id: str, symbol: str):
        """取消订单"""
        try:
            cancel_params = {
                'category': 'spot',
                'orderId': order_id,
                'symbol': symbol.replace('/', '')
            }
            
            url, headers, body = self._prepare_request('POST', '/v5/order/cancel', cancel_params)
            
            response = self.session.post(url, headers=headers, data=body)
            data = response.json()
            
            if data['retCode'] == 0:
                logger.info(f"✅ 订单已取消: {order_id}")
                return True
            else:
                logger.error(f"取消订单失败: {data}")
                return False
                
        except Exception as e:
            logger.error(f"取消订单失败: {e}")
            return False
    
    async def disconnect(self):
        """关闭连接"""
        self.session.close()