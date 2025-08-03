#!/usr/bin/env python3
"""
公共 API 套利监控机器人
不需要 API 密钥，仅监控和显示套利机会
"""

import ccxt
import time
import logging
from datetime import datetime
from decimal import Decimal
import json

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/public_bot_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PublicArbitrageBot:
    def __init__(self):
        # 初始化多个交易所
        self.exchanges = {
            'binance': ccxt.binance({'enableRateLimit': True}),
            'bybit': ccxt.bybit({'enableRateLimit': True, 'options': {'defaultType': 'spot'}}),
            'okx': ccxt.okx({'enableRateLimit': True}),
            'kucoin': ccxt.kucoin({'enableRateLimit': True}),
            'gate': ccxt.gate({'enableRateLimit': True})
        }
        
        # 监控的交易对
        self.symbols = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT']
        
        # 套利参数
        self.min_profit_percentage = 0.3  # 最小利润率
        self.maker_fee = 0.1  # Maker 手续费
        self.taker_fee = 0.1  # Taker 手续费
        
        # 统计数据
        self.opportunities_found = 0
        self.start_time = datetime.now()
        
    def calculate_profit(self, buy_price, sell_price, amount=1000):
        """计算套利利润"""
        # 买入成本（包括手续费）
        buy_cost = amount * (1 + self.taker_fee / 100)
        buy_quantity = buy_cost / buy_price
        
        # 卖出收益（扣除手续费）
        sell_revenue = buy_quantity * sell_price * (1 - self.maker_fee / 100)
        
        # 净利润
        net_profit = sell_revenue - buy_cost
        profit_rate = (net_profit / buy_cost) * 100
        
        return {
            'buy_cost': buy_cost,
            'buy_quantity': buy_quantity,
            'sell_revenue': sell_revenue,
            'net_profit': net_profit,
            'profit_rate': profit_rate
        }
    
    def get_orderbook(self, exchange_name, symbol):
        """获取订单簿"""
        try:
            exchange = self.exchanges[exchange_name]
            orderbook = exchange.fetch_order_book(symbol, limit=5)
            return {
                'bids': orderbook['bids'][:5],  # 买单（最高5档）
                'asks': orderbook['asks'][:5],  # 卖单（最低5档）
                'timestamp': datetime.now()
            }
        except Exception as e:
            logger.debug(f"获取 {exchange_name} {symbol} 订单簿失败: {str(e)[:50]}")
            return None
    
    def find_arbitrage_opportunities(self, symbol):
        """查找套利机会"""
        orderbooks = {}
        
        # 获取所有交易所的订单簿
        for name in self.exchanges.keys():
            orderbook = self.get_orderbook(name, symbol)
            if orderbook and len(orderbook['bids']) > 0 and len(orderbook['asks']) > 0:
                orderbooks[name] = orderbook
        
        if len(orderbooks) < 2:
            return []
        
        opportunities = []
        
        # 比较所有交易所对
        for buy_exchange, buy_book in orderbooks.items():
            for sell_exchange, sell_book in orderbooks.items():
                if buy_exchange != sell_exchange:
                    # 获取最佳价格
                    buy_price = buy_book['asks'][0][0]  # 最低卖价
                    sell_price = sell_book['bids'][0][0]  # 最高买价
                    
                    # 计算利润
                    if sell_price > buy_price:
                        profit_info = self.calculate_profit(buy_price, sell_price)
                        
                        if profit_info['profit_rate'] > self.min_profit_percentage:
                            opportunities.append({
                                'symbol': symbol,
                                'buy_exchange': buy_exchange,
                                'sell_exchange': sell_exchange,
                                'buy_price': buy_price,
                                'sell_price': sell_price,
                                'spread': sell_price - buy_price,
                                'spread_percentage': ((sell_price - buy_price) / buy_price) * 100,
                                **profit_info,
                                'timestamp': datetime.now()
                            })
        
        return opportunities
    
    def display_opportunity(self, opp):
        """显示套利机会"""
        self.opportunities_found += 1
        
        print("\n" + "="*60)
        print(f"🎯 套利机会 #{self.opportunities_found}")
        print("="*60)
        print(f"交易对: {opp['symbol']}")
        print(f"路径: {opp['buy_exchange']} → {opp['sell_exchange']}")
        print(f"买入价: ${opp['buy_price']:,.2f}")
        print(f"卖出价: ${opp['sell_price']:,.2f}")
        print(f"价差: ${opp['spread']:,.2f} ({opp['spread_percentage']:.3f}%)")
        print(f"净利润率: {opp['profit_rate']:.3f}% (扣除手续费)")
        print(f"$1000 预计利润: ${opp['net_profit']:.2f}")
        print(f"时间: {opp['timestamp'].strftime('%H:%M:%S')}")
        
        # 保存到日志
        logger.info(f"套利机会: {opp['symbol']} {opp['buy_exchange']}→{opp['sell_exchange']} 利润率:{opp['profit_rate']:.3f}%")
    
    def show_statistics(self):
        """显示统计信息"""
        runtime = datetime.now() - self.start_time
        hours = runtime.total_seconds() / 3600
        
        print(f"\n📊 运行统计:")
        print(f"运行时间: {runtime}")
        print(f"发现机会: {self.opportunities_found} 个")
        if hours > 0:
            print(f"平均每小时: {self.opportunities_found / hours:.1f} 个")
    
    def run(self):
        """运行监控"""
        print("🚀 启动公共 API 套利监控机器人")
        print(f"监控交易所: {', '.join(self.exchanges.keys())}")
        print(f"监控交易对: {', '.join(self.symbols)}")
        print(f"最小利润率: {self.min_profit_percentage}%")
        print(f"手续费: Maker {self.maker_fee}%, Taker {self.taker_fee}%")
        print("-" * 60)
        
        check_count = 0
        
        while True:
            try:
                check_count += 1
                
                # 每10次检查显示一次状态
                if check_count % 10 == 0:
                    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 已检查 {check_count} 次")
                    self.show_statistics()
                
                # 检查所有交易对
                for symbol in self.symbols:
                    opportunities = self.find_arbitrage_opportunities(symbol)
                    
                    # 显示最佳机会
                    if opportunities:
                        best_opp = max(opportunities, key=lambda x: x['profit_rate'])
                        self.display_opportunity(best_opp)
                
                # 等待一段时间
                time.sleep(3)
                
            except KeyboardInterrupt:
                print("\n\n👋 停止监控")
                self.show_statistics()
                break
                
            except Exception as e:
                logger.error(f"错误: {e}")
                time.sleep(5)

if __name__ == "__main__":
    bot = PublicArbitrageBot()
    bot.run()