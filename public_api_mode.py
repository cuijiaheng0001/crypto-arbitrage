#!/usr/bin/env python3
"""
仅使用公共 API 的套利监控器
用于测试套利逻辑，不需要 API 密钥
"""

import ccxt
import asyncio
import time
from decimal import Decimal
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PublicArbitrageMonitor:
    def __init__(self):
        # 初始化交易所（仅使用公共 API）
        self.exchanges = {
            'binance': ccxt.binance({
                'enableRateLimit': True,
                'options': {'defaultType': 'spot'}
            }),
            'bybit': ccxt.bybit({
                'enableRateLimit': True,
                'options': {'defaultType': 'spot'}
            }),
            'okx': ccxt.okx({
                'enableRateLimit': True,
                'options': {'defaultType': 'spot'}
            })
        }
        
        # 监控的交易对
        self.symbols = ['BTC/USDT', 'ETH/USDT']
        
        # 套利参数
        self.min_profit_percentage = 0.3  # 最小利润率 0.3%
        self.estimated_fee = 0.1  # 估计手续费 0.1%
        
    async def load_markets(self):
        """加载市场信息"""
        for name, exchange in self.exchanges.items():
            try:
                await exchange.load_markets()
                logger.info(f"✅ {name} 市场加载成功")
            except Exception as e:
                logger.error(f"❌ {name} 市场加载失败: {e}")
    
    async def get_ticker(self, exchange_name, symbol):
        """获取交易对价格"""
        try:
            exchange = self.exchanges[exchange_name]
            ticker = await exchange.fetch_ticker(symbol)
            return {
                'bid': ticker['bid'],
                'ask': ticker['ask'],
                'last': ticker['last'],
                'timestamp': ticker['timestamp']
            }
        except Exception as e:
            logger.error(f"获取 {exchange_name} {symbol} 价格失败: {e}")
            return None
    
    async def find_arbitrage_opportunities(self, symbol):
        """查找套利机会"""
        # 获取所有交易所的价格
        prices = {}
        for name in self.exchanges.keys():
            ticker = await self.get_ticker(name, symbol)
            if ticker:
                prices[name] = ticker
        
        if len(prices) < 2:
            return
        
        # 检查套利机会
        for buy_exchange, buy_price in prices.items():
            for sell_exchange, sell_price in prices.items():
                if buy_exchange != sell_exchange:
                    # 计算利润率
                    buy_at = buy_price['ask']  # 买入价格
                    sell_at = sell_price['bid']  # 卖出价格
                    
                    if buy_at > 0 and sell_at > buy_at:
                        profit_rate = ((sell_at - buy_at) / buy_at - 2 * self.estimated_fee) * 100
                        
                        if profit_rate > self.min_profit_percentage:
                            logger.info(f"""
🎯 发现套利机会！
交易对: {symbol}
买入: {buy_exchange} @ ${buy_at:,.2f}
卖出: {sell_exchange} @ ${sell_at:,.2f}
预估利润率: {profit_rate:.2f}% (扣除手续费后)
价差: ${sell_at - buy_at:,.2f}
""")
    
    async def monitor(self):
        """持续监控套利机会"""
        await self.load_markets()
        
        logger.info("🔍 开始监控套利机会...")
        logger.info(f"监控交易对: {', '.join(self.symbols)}")
        logger.info(f"最小利润率: {self.min_profit_percentage}%")
        
        while True:
            try:
                for symbol in self.symbols:
                    await self.find_arbitrage_opportunities(symbol)
                
                # 等待一段时间后再次检查
                await asyncio.sleep(5)
                
            except Exception as e:
                logger.error(f"监控出错: {e}")
                await asyncio.sleep(5)

async def main():
    monitor = PublicArbitrageMonitor()
    await monitor.monitor()

if __name__ == "__main__":
    asyncio.run(main())