#!/usr/bin/env python3
"""
简单的套利监控器 - 使用公共 API
"""

import ccxt
import time
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SimpleArbitrageMonitor:
    def __init__(self):
        # 初始化交易所
        self.exchanges = {
            'binance': ccxt.binance({'enableRateLimit': True}),
            'bybit': ccxt.bybit({'enableRateLimit': True, 'options': {'defaultType': 'spot'}}),
            'okx': ccxt.okx({'enableRateLimit': True})
        }
        
        # 监控的交易对
        self.symbols = ['BTC/USDT', 'ETH/USDT']
        
        # 套利参数
        self.min_profit_percentage = 0.3  # 最小利润率 0.3%
        self.estimated_fee = 0.1  # 每次交易手续费 0.1%
        
    def get_price(self, exchange_name, symbol):
        """获取价格"""
        try:
            exchange = self.exchanges[exchange_name]
            ticker = exchange.fetch_ticker(symbol)
            return {
                'bid': ticker['bid'],  # 买入价
                'ask': ticker['ask'],  # 卖出价
                'last': ticker['last'],
                'timestamp': datetime.now()
            }
        except Exception as e:
            logger.error(f"❌ {exchange_name} {symbol}: {str(e)[:50]}")
            return None
    
    def check_arbitrage(self, symbol):
        """检查套利机会"""
        prices = {}
        
        # 获取所有交易所的价格
        for name in self.exchanges.keys():
            price = self.get_price(name, symbol)
            if price:
                prices[name] = price
                logger.info(f"{name} {symbol}: 买${price['bid']:,.2f} / 卖${price['ask']:,.2f}")
        
        if len(prices) < 2:
            return
        
        # 查找套利机会
        opportunities = []
        
        for buy_exchange, buy_data in prices.items():
            for sell_exchange, sell_data in prices.items():
                if buy_exchange != sell_exchange:
                    # 在 buy_exchange 买入（使用卖价 ask）
                    # 在 sell_exchange 卖出（使用买价 bid）
                    buy_price = buy_data['ask']
                    sell_price = sell_data['bid']
                    
                    if buy_price > 0 and sell_price > buy_price:
                        # 计算利润
                        gross_profit_rate = (sell_price - buy_price) / buy_price * 100
                        net_profit_rate = gross_profit_rate - 2 * self.estimated_fee
                        
                        if net_profit_rate > self.min_profit_percentage:
                            opportunities.append({
                                'symbol': symbol,
                                'buy_exchange': buy_exchange,
                                'sell_exchange': sell_exchange,
                                'buy_price': buy_price,
                                'sell_price': sell_price,
                                'gross_profit_rate': gross_profit_rate,
                                'net_profit_rate': net_profit_rate,
                                'spread': sell_price - buy_price
                            })
        
        # 显示套利机会
        if opportunities:
            print("\n" + "="*60)
            print(f"🎯 发现 {len(opportunities)} 个套利机会!")
            print("="*60)
            
            for opp in sorted(opportunities, key=lambda x: x['net_profit_rate'], reverse=True):
                print(f"""
币种: {opp['symbol']}
路径: {opp['buy_exchange']} → {opp['sell_exchange']}
买入价: ${opp['buy_price']:,.2f}
卖出价: ${opp['sell_price']:,.2f}
价差: ${opp['spread']:,.2f}
毛利润率: {opp['gross_profit_rate']:.3f}%
净利润率: {opp['net_profit_rate']:.3f}% (扣除手续费)
""")
        else:
            logger.info(f"未发现 {symbol} 的套利机会")
    
    def run(self):
        """运行监控"""
        logger.info("🚀 启动套利监控器...")
        logger.info(f"监控交易对: {', '.join(self.symbols)}")
        logger.info(f"最小利润率: {self.min_profit_percentage}%")
        logger.info(f"预估手续费: {self.estimated_fee}% x 2")
        
        while True:
            try:
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 检查价格...")
                
                for symbol in self.symbols:
                    print(f"\n--- {symbol} ---")
                    self.check_arbitrage(symbol)
                
                # 等待5秒
                time.sleep(5)
                
            except KeyboardInterrupt:
                logger.info("\n👋 停止监控")
                break
            except Exception as e:
                logger.error(f"错误: {e}")
                time.sleep(5)

if __name__ == "__main__":
    monitor = SimpleArbitrageMonitor()
    monitor.run()