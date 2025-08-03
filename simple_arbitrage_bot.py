#!/usr/bin/env python3
"""
简化版套利监控机器人
基于 Bitget + Bybit 的价格差监控和套利机会提醒

灵感来源：Passivbot 和其他成熟开源项目
适合初学者理解套利原理和实现
"""

import ccxt
import time
import json
import os
from datetime import datetime
from dotenv import load_dotenv
import logging

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/arbitrage_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SimpleArbitrageBot:
    def __init__(self):
        """初始化套利机器人"""
        
        # 初始化交易所
        self.exchanges = self._init_exchanges()
        
        # 套利配置
        self.config = {
            'symbols': ['BTC/USDT', 'ETH/USDT', 'SOL/USDT'],  # 监控的交易对
            'min_profit_percentage': float(os.getenv('MIN_PROFIT_PERCENTAGE', 0.3)),  # 最小利润率
            'check_interval': int(os.getenv('PRICE_UPDATE_INTERVAL', 10)),  # 检查间隔(秒)
            'max_trade_amount': float(os.getenv('MAX_TRADE_AMOUNT', 100)),  # 最大交易金额
            'fees': {
                'bitget': 0.001,  # 0.1% 手续费
                'bybit': 0.001    # 0.1% 手续费
            }
        }
        
        # 统计数据
        self.stats = {
            'opportunities_found': 0,
            'total_checks': 0,
            'start_time': datetime.now(),
            'best_opportunity': None
        }
        
        logger.info("🚀 简化版套利监控机器人已启动")
        logger.info(f"📊 监控交易对: {', '.join(self.config['symbols'])}")
        logger.info(f"💰 最小利润率: {self.config['min_profit_percentage']}%")
    
    def _init_exchanges(self):
        """初始化交易所连接"""
        exchanges = {}
        
        try:
            # Bitget 配置
            exchanges['bitget'] = ccxt.bitget({
                'apiKey': os.getenv('BITGET_API_KEY'),
                'secret': os.getenv('BITGET_API_SECRET'),
                'password': os.getenv('BITGET_PASSPHRASE'),
                'sandbox': False,  # 使用主网
                'enableRateLimit': True,
            })
            
            # Bybit 配置 (先用测试网)
            exchanges['bybit'] = ccxt.bybit({
                'apiKey': os.getenv('BYBIT_API_KEY'),
                'secret': os.getenv('BYBIT_SECRET_KEY'),
                'sandbox': True,  # 使用测试网
                'enableRateLimit': True,
            })
            
            logger.info("✅ 交易所连接初始化成功")
            
        except Exception as e:
            logger.error(f"❌ 交易所初始化失败: {str(e)}")
            raise
        
        return exchanges
    
    def get_ticker(self, exchange_name, symbol):
        """获取交易对价格"""
        try:
            exchange = self.exchanges[exchange_name]
            ticker = exchange.fetch_ticker(symbol)
            return {
                'bid': float(ticker['bid']),  # 买一价
                'ask': float(ticker['ask']),  # 卖一价
                'last': float(ticker['last']), # 最新价
                'timestamp': ticker['timestamp']
            }
        except Exception as e:
            logger.warning(f"⚠️ 获取 {exchange_name} {symbol} 价格失败: {str(e)}")
            return None
    
    def calculate_arbitrage_opportunity(self, symbol):
        """计算套利机会"""
        
        # 获取两个交易所的价格
        bitget_ticker = self.get_ticker('bitget', symbol)
        bybit_ticker = self.get_ticker('bybit', symbol)
        
        if not bitget_ticker or not bybit_ticker:
            return None
        
        # 计算套利机会
        opportunities = []
        
        # 场景1: Bitget买入 -> Bybit卖出
        buy_price = bitget_ticker['ask']  # Bitget卖价(我们买入价)
        sell_price = bybit_ticker['bid']  # Bybit买价(我们卖出价)
        
        # 考虑手续费
        total_fees = self.config['fees']['bitget'] + self.config['fees']['bybit']
        profit_percentage = ((sell_price - buy_price) / buy_price - total_fees) * 100
        
        if profit_percentage > self.config['min_profit_percentage']:
            opportunities.append({
                'direction': 'Bitget -> Bybit',
                'buy_exchange': 'Bitget',
                'sell_exchange': 'Bybit',
                'buy_price': buy_price,
                'sell_price': sell_price,
                'profit_percentage': profit_percentage,
                'profit_per_usdt': sell_price - buy_price - (buy_price * total_fees)
            })
        
        # 场景2: Bybit买入 -> Bitget卖出
        buy_price = bybit_ticker['ask']   # Bybit卖价(我们买入价)
        sell_price = bitget_ticker['bid'] # Bitget买价(我们卖出价)
        
        profit_percentage = ((sell_price - buy_price) / buy_price - total_fees) * 100
        
        if profit_percentage > self.config['min_profit_percentage']:
            opportunities.append({
                'direction': 'Bybit -> Bitget',
                'buy_exchange': 'Bybit',
                'sell_exchange': 'Bitget',
                'buy_price': buy_price,
                'sell_price': sell_price,
                'profit_percentage': profit_percentage,
                'profit_per_usdt': sell_price - buy_price - (buy_price * total_fees)
            })
        
        return {
            'symbol': symbol,
            'timestamp': datetime.now(),
            'bitget_price': bitget_ticker['last'],
            'bybit_price': bybit_ticker['last'],
            'opportunities': opportunities
        }
    
    def log_opportunity(self, opportunity_data):
        """记录套利机会"""
        if not opportunity_data['opportunities']:
            return
        
        self.stats['opportunities_found'] += len(opportunity_data['opportunities'])
        
        for opp in opportunity_data['opportunities']:
            logger.info("=" * 60)
            logger.info(f"🎯 发现套利机会! {opportunity_data['symbol']}")
            logger.info(f"📊 方向: {opp['direction']}")
            logger.info(f"💰 利润率: {opp['profit_percentage']:.3f}%")
            logger.info(f"🔥 每USDT利润: ${opp['profit_per_usdt']:.4f}")
            logger.info(f"📈 买入价格: ${opp['buy_price']:.2f} ({opp['buy_exchange']})")
            logger.info(f"📉 卖出价格: ${opp['sell_price']:.2f} ({opp['sell_exchange']})")
            logger.info(f"💵 建议交易金额: ${self.config['max_trade_amount']:.0f}")
            logger.info(f"💸 预期利润: ${opp['profit_per_usdt'] * self.config['max_trade_amount']:.2f}")
            logger.info("=" * 60)
            
            # 更新最佳机会
            if (not self.stats['best_opportunity'] or 
                opp['profit_percentage'] > self.stats['best_opportunity']['profit_percentage']):
                self.stats['best_opportunity'] = opp.copy()
                self.stats['best_opportunity']['symbol'] = opportunity_data['symbol']
                self.stats['best_opportunity']['timestamp'] = opportunity_data['timestamp']
    
    def print_statistics(self):
        """打印统计信息"""
        runtime = datetime.now() - self.stats['start_time']
        
        print("\n" + "=" * 60)
        print("📊 套利监控统计")
        print("=" * 60)
        print(f"⏱️ 运行时间: {runtime}")
        print(f"🔍 总检查次数: {self.stats['total_checks']}")
        print(f"🎯 发现机会数: {self.stats['opportunities_found']}")
        
        if self.stats['best_opportunity']:
            best = self.stats['best_opportunity']
            print(f"🏆 最佳机会: {best['symbol']} ({best['direction']})")
            print(f"💰 最高利润率: {best['profit_percentage']:.3f}%")
        else:
            print("🤷 暂未发现符合条件的套利机会")
        
        print("=" * 60)
    
    def check_all_symbols(self):
        """检查所有交易对的套利机会"""
        self.stats['total_checks'] += 1
        
        logger.info(f"🔍 第 {self.stats['total_checks']} 次价格检查...")
        
        for symbol in self.config['symbols']:
            try:
                opportunity_data = self.calculate_arbitrage_opportunity(symbol)
                if opportunity_data:
                    self.log_opportunity(opportunity_data)
                    
                    # 简单显示当前价格
                    logger.info(f"💎 {symbol}: Bitget ${opportunity_data['bitget_price']:.2f} | "
                              f"Bybit ${opportunity_data['bybit_price']:.2f}")
                
                # 避免API限制
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"❌ 检查 {symbol} 时出错: {str(e)}")
    
    def run(self):
        """运行套利监控"""
        logger.info("🎯 开始监控套利机会...")
        logger.info("按 Ctrl+C 停止监控\n")
        
        try:
            while True:
                self.check_all_symbols()
                
                # 每10次检查显示一次统计
                if self.stats['total_checks'] % 10 == 0:
                    self.print_statistics()
                
                # 等待下次检查
                logger.info(f"😴 等待 {self.config['check_interval']} 秒...\n")
                time.sleep(self.config['check_interval'])
                
        except KeyboardInterrupt:
            logger.info("\n🛑 用户停止监控")
        except Exception as e:
            logger.error(f"❌ 监控过程中出错: {str(e)}")
        finally:
            self.print_statistics()
            logger.info("👋 套利监控已停止")

def main():
    """主函数"""
    
    # 检查日志目录
    os.makedirs('logs', exist_ok=True)
    
    # 检查API配置
    required_env_vars = [
        'BITGET_API_KEY', 'BITGET_API_SECRET', 'BITGET_PASSPHRASE',
        'BYBIT_API_KEY', 'BYBIT_SECRET_KEY'
    ]
    
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        print(f"❌ 缺少环境变量: {', '.join(missing_vars)}")
        print("请确保在 .env 文件中配置了所有必要的API密钥")
        return
    
    # 启动机器人
    try:
        bot = SimpleArbitrageBot()
        bot.run()
    except Exception as e:
        logger.error(f"❌ 机器人启动失败: {str(e)}")

if __name__ == "__main__":
    main()