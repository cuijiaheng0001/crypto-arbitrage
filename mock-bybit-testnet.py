"""
Mock Bybit Testnet - 模拟Bybit价格数据用于测试
"""
import random
import time

class MockBybitExchange:
    def __init__(self):
        self.name = 'bybit'
        self.balance = {'USDT': 10000, 'BTC': 0, 'ETH': 0}
        
    def fetch_ticker(self, symbol):
        """模拟获取价格，基于Binance价格加随机偏差"""
        # 这里可以从Binance获取真实价格，然后加上小幅偏差
        base_price = 45000  # 示例BTC价格
        spread = random.uniform(-0.002, 0.002)  # ±0.2%的价格差
        
        bid = base_price * (1 + spread)
        ask = bid * 1.001  # 0.1%的买卖差价
        
        return {
            'symbol': symbol,
            'bid': bid,
            'ask': ask,
            'last': (bid + ask) / 2
        }
    
    def create_order(self, symbol, type, side, amount, price=None):
        """模拟下单"""
        print(f"[模拟] 在Bybit {side} {amount} {symbol} @ {price or 'market'}")
        return {
            'id': f"mock_{int(time.time())}",
            'status': 'filled',
            'amount': amount,
            'price': price
        }