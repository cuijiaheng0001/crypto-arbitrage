#!/usr/bin/env python3
"""
测试网套利机器人
使用 Binance 测试网进行套利测试
"""

import asyncio
import os
import time
import logging
from datetime import datetime
from dotenv import load_dotenv
from src.exchanges.binance_testnet import BinanceTestnetExchange

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/testnet_bot_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TestnetArbitrageBot:
    def __init__(self):
        # Binance 测试网交易所
        self.binance = BinanceTestnetExchange(
            api_key=os.getenv('BINANCE_API_KEY'),
            secret_key=os.getenv('BINANCE_SECRET_KEY')
        )
        
        # 监控的交易对
        self.symbols = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT']
        
        # 套利参数
        self.min_profit_percentage = 0.1  # 最小利润率 0.1%（测试网用）
        self.test_amount = 0.001  # 测试交易数量
        
        # 统计
        self.trades_executed = 0
        self.start_time = datetime.now()
        
    async def initialize(self):
        """初始化"""
        logger.info("🚀 启动测试网套利机器人...")
        
        try:
            await self.binance.connect()
            
            # 显示余额
            balances = await self.binance.get_balance()
            logger.info("💰 测试网余额:")
            for asset, balance in balances.items():
                if balance['total'] > 0:
                    logger.info(f"   {asset}: {balance['total']:.4f}")
            
            return True
            
        except Exception as e:
            logger.error(f"初始化失败: {e}")
            return False
    
    async def simulate_arbitrage(self, symbol):
        """模拟套利交易"""
        try:
            # 获取当前价格
            ticker = await self.binance.get_ticker(symbol)
            current_price = (ticker['bid'] + ticker['ask']) / 2
            
            # 模拟另一个交易所的价格（随机波动）
            import random
            price_diff = random.uniform(-0.5, 0.5)  # -0.5% 到 +0.5%
            other_price = current_price * (1 + price_diff / 100)
            
            # 计算利润
            profit_rate = abs(price_diff)
            
            if profit_rate > self.min_profit_percentage:
                logger.info(f"""
🎯 发现套利机会！
交易对: {symbol}
Binance 价格: ${current_price:,.2f}
模拟交易所价格: ${other_price:,.2f}
价差: {price_diff:.3f}%
预计利润率: {profit_rate:.3f}%
""")
                
                # 执行测试交易
                if symbol == 'BTC/USDT':
                    # 在测试网执行小额交易
                    if price_diff > 0:
                        # 在 Binance 买入
                        logger.info(f"📈 在 Binance 测试网买入 {self.test_amount} BTC @ ${current_price:,.2f}")
                        try:
                            order = await self.binance.place_order(
                                symbol='BTC/USDT',
                                side='buy',
                                amount=self.test_amount,
                                price=ticker['ask']
                            )
                            logger.info(f"✅ 买单成功: 订单ID {order['orderId']}")
                            self.trades_executed += 1
                        except Exception as e:
                            logger.error(f"买单失败: {e}")
                    else:
                        # 在 Binance 卖出
                        logger.info(f"📉 在 Binance 测试网卖出 {self.test_amount} BTC @ ${current_price:,.2f}")
                        try:
                            order = await self.binance.place_order(
                                symbol='BTC/USDT',
                                side='sell',
                                amount=self.test_amount,
                                price=ticker['bid']
                            )
                            logger.info(f"✅ 卖单成功: 订单ID {order['orderId']}")
                            self.trades_executed += 1
                        except Exception as e:
                            logger.error(f"卖单失败: {e}")
                
        except Exception as e:
            logger.error(f"模拟套利失败: {e}")
    
    async def monitor_and_trade(self):
        """监控并交易"""
        check_count = 0
        
        while True:
            try:
                check_count += 1
                
                # 每10次检查显示统计
                if check_count % 10 == 0:
                    runtime = datetime.now() - self.start_time
                    logger.info(f"""
📊 运行统计:
运行时间: {runtime}
检查次数: {check_count}
执行交易: {self.trades_executed}
""")
                
                # 检查所有交易对
                for symbol in self.symbols:
                    await self.simulate_arbitrage(symbol)
                
                # 获取最新余额
                if check_count % 20 == 0:
                    balances = await self.binance.get_balance()
                    usdt_balance = balances.get('USDT', {}).get('total', 0)
                    btc_balance = balances.get('BTC', {}).get('total', 0)
                    logger.info(f"当前余额: USDT: {usdt_balance:.2f}, BTC: {btc_balance:.4f}")
                
                # 等待
                await asyncio.sleep(5)
                
            except KeyboardInterrupt:
                logger.info("👋 停止监控")
                break
                
            except Exception as e:
                logger.error(f"监控错误: {e}")
                await asyncio.sleep(10)
    
    async def run(self):
        """运行机器人"""
        if await self.initialize():
            await self.monitor_and_trade()
        
        await self.binance.disconnect()

async def main():
    bot = TestnetArbitrageBot()
    await bot.run()

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════╗
║        测试网套利机器人 v1.0             ║
║                                          ║
║  使用 Binance 测试网进行套利模拟         ║
║  无风险测试套利策略                      ║
╔══════════════════════════════════════════╝
""")
    
    asyncio.run(main())