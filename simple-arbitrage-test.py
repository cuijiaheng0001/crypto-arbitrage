"""
简单套利测试 - 使用Binance Testnet模拟跨交易所套利
"""
import ccxt
import time
import os
from dotenv import load_dotenv

load_dotenv()

# 配置
BINANCE_TESTNET_API_KEY = os.getenv('BINANCE_API_KEY')
BINANCE_TESTNET_SECRET = os.getenv('BINANCE_SECRET_KEY')

# 初始化Binance测试网
exchange = ccxt.binance({
    'apiKey': BINANCE_TESTNET_API_KEY,
    'secret': BINANCE_TESTNET_SECRET,
    'options': {
        'defaultType': 'spot',
    },
    'urls': {
        'api': {
            'public': 'https://testnet.binance.vision/api',
            'private': 'https://testnet.binance.vision/api',
        }
    }
})

def check_arbitrage_opportunity(symbol='BTC/USDT'):
    """检查套利机会（模拟两个交易所）"""
    try:
        # 获取订单簿
        orderbook = exchange.fetch_order_book(symbol)
        
        # 模拟第二个交易所的价格（加入随机偏差）
        best_bid = orderbook['bids'][0][0] if orderbook['bids'] else 0
        best_ask = orderbook['asks'][0][0] if orderbook['asks'] else 0
        
        # 模拟价格差异
        mock_exchange_bid = best_bid * 1.003  # 模拟另一个交易所出价高0.3%
        mock_exchange_ask = best_ask * 0.997  # 模拟另一个交易所要价低0.3%
        
        # 计算套利机会
        # 在真实交易所买入，在模拟交易所卖出
        profit_pct_1 = ((mock_exchange_bid - best_ask) / best_ask) * 100
        
        # 在模拟交易所买入，在真实交易所卖出
        profit_pct_2 = ((best_bid - mock_exchange_ask) / mock_exchange_ask) * 100
        
        print(f"\n=== {time.strftime('%Y-%m-%d %H:%M:%S')} ===")
        print(f"Binance Testnet - Bid: ${best_bid:.2f}, Ask: ${best_ask:.2f}")
        print(f"模拟交易所 - Bid: ${mock_exchange_bid:.2f}, Ask: ${mock_exchange_ask:.2f}")
        
        if profit_pct_1 > 0.1:  # 0.1%以上利润
            print(f"🎯 套利机会！在Binance买入@${best_ask:.2f}，在模拟交易所卖出@${mock_exchange_bid:.2f}")
            print(f"💰 预期利润: {profit_pct_1:.3f}%")
            
        if profit_pct_2 > 0.1:
            print(f"🎯 套利机会！在模拟交易所买入@${mock_exchange_ask:.2f}，在Binance卖出@${best_bid:.2f}")
            print(f"💰 预期利润: {profit_pct_2:.3f}%")
            
    except Exception as e:
        print(f"错误: {e}")

# 主循环
if __name__ == "__main__":
    print("开始监控套利机会...")
    print("按 Ctrl+C 停止")
    
    while True:
        try:
            check_arbitrage_opportunity()
            time.sleep(5)  # 每5秒检查一次
        except KeyboardInterrupt:
            print("\n停止监控")
            break
        except Exception as e:
            print(f"主循环错误: {e}")
            time.sleep(5)