#!/usr/bin/env python3
"""
Crypto Arbitrage Bot - Main Entry Point
"""

import asyncio
import logging
import os
import signal
import sys
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/bot_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# 导入交易所模块
from src.exchanges import BinanceExchange, BybitExchange


class CryptoArbitrageBot:
    def __init__(self):
        self.running = True
        self.exchanges = {}
        
    async def setup(self):
        """初始化交易所连接"""
        logger.info("🚀 启动 Crypto Arbitrage Bot...")
        
        # 初始化 Binance
        if os.getenv('BINANCE_API_KEY'):
            self.exchanges['binance'] = BinanceExchange(
                api_key=os.getenv('BINANCE_API_KEY'),
                secret_key=os.getenv('BINANCE_SECRET_KEY'),
                testnet=os.getenv('BINANCE_TESTNET', 'True').lower() == 'true'
            )
            
        # 初始化 Bybit
        if os.getenv('BYBIT_API_KEY'):
            self.exchanges['bybit'] = BybitExchange(
                api_key=os.getenv('BYBIT_API_KEY'),
                secret_key=os.getenv('BYBIT_SECRET_KEY'),
                testnet=os.getenv('BYBIT_TESTNET', 'True').lower() == 'true'
            )
        
        # 连接所有交易所
        for name, exchange in self.exchanges.items():
            try:
                await exchange.connect()
                logger.info(f"✅ 已连接到 {name}")
            except Exception as e:
                logger.error(f"❌ 连接 {name} 失败: {e}")
                
    async def monitor_prices(self):
        """监控价格并寻找套利机会"""
        symbol = 'BTC/USDT'  # 可以配置多个交易对
        
        while self.running:
            try:
                # 获取各交易所价格
                prices = {}
                for name, exchange in self.exchanges.items():
                    try:
                        ticker = await exchange.get_ticker(symbol)
                        prices[name] = ticker
                        logger.info(f"{name} - {symbol}: Bid={ticker['bid']}, Ask={ticker['ask']}")
                    except Exception as e:
                        logger.error(f"获取 {name} 价格失败: {e}")
                
                # 检查套利机会
                if len(prices) >= 2:
                    await self.check_arbitrage_opportunity(prices, symbol)
                
                # 等待下一次检查
                await asyncio.sleep(5)  # 每5秒检查一次
                
            except Exception as e:
                logger.error(f"监控循环错误: {e}")
                await asyncio.sleep(10)
                
    async def check_arbitrage_opportunity(self, prices, symbol):
        """检查套利机会"""
        exchanges = list(prices.keys())
        
        for i in range(len(exchanges)):
            for j in range(i + 1, len(exchanges)):
                ex1, ex2 = exchanges[i], exchanges[j]
                
                # 计算潜在利润
                # 在 ex1 买入，在 ex2 卖出
                profit1 = float(prices[ex2]['bid'] - prices[ex1]['ask'])
                profit1_percent = (profit1 / float(prices[ex1]['ask'])) * 100
                
                # 在 ex2 买入，在 ex1 卖出
                profit2 = float(prices[ex1]['bid'] - prices[ex2]['ask'])
                profit2_percent = (profit2 / float(prices[ex2]['ask'])) * 100
                
                min_profit_percent = float(os.getenv('MIN_PROFIT_PERCENTAGE', '0.5'))
                
                if profit1_percent > min_profit_percent:
                    logger.warning(f"💰 套利机会: 在 {ex1} 买入 @{prices[ex1]['ask']}, "
                                 f"在 {ex2} 卖出 @{prices[ex2]['bid']}, "
                                 f"利润: {profit1_percent:.2f}%")
                    
                if profit2_percent > min_profit_percent:
                    logger.warning(f"💰 套利机会: 在 {ex2} 买入 @{prices[ex2]['ask']}, "
                                 f"在 {ex1} 卖出 @{prices[ex1]['bid']}, "
                                 f"利润: {profit2_percent:.2f}%")
    
    async def run(self):
        """主运行循环"""
        await self.setup()
        
        if not self.exchanges:
            logger.error("❌ 没有可用的交易所连接")
            return
            
        logger.info("🔍 开始监控价格...")
        await self.monitor_prices()
        
    def stop(self):
        """停止机器人"""
        logger.info("🛑 正在停止机器人...")
        self.running = False


# 全局机器人实例
bot = CryptoArbitrageBot()


def signal_handler(signum, frame):
    """处理退出信号"""
    logger.info("收到退出信号")
    bot.stop()
    sys.exit(0)


async def main():
    """主函数"""
    # 注册信号处理
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        await bot.run()
    except Exception as e:
        logger.error(f"主程序错误: {e}")
    finally:
        logger.info("程序退出")


if __name__ == "__main__":
    asyncio.run(main())