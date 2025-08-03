#!/usr/bin/env python3
"""
Binance 测试网套利演示
展示如何在单个交易所内进行价格监控和交易
"""

import asyncio
import os
import time
import logging
from datetime import datetime
from decimal import Decimal
from dotenv import load_dotenv
from src.exchanges.binance_testnet import BinanceTestnetExchange

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BinanceTestnetDemo:
    def __init__(self):
        self.exchange = BinanceTestnetExchange(
            api_key=os.getenv('BINANCE_API_KEY'),
            secret_key=os.getenv('BINANCE_SECRET_KEY')
        )
        
        # 交易参数
        self.symbols = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT']
        self.test_amount = {
            'BTC/USDT': 0.001,
            'ETH/USDT': 0.01,
            'BNB/USDT': 0.1
        }
        
        # 统计
        self.start_time = datetime.now()
        self.trades = []
        
    async def initialize(self):
        """初始化"""
        logger.info("🚀 Binance 测试网套利演示")
        logger.info("="*50)
        
        await self.exchange.connect()
        
        # 显示初始余额
        balances = await self.exchange.get_balance()
        logger.info("💰 初始余额:")
        
        self.initial_balances = {}
        for asset in ['USDT', 'BTC', 'ETH', 'BNB']:
            if asset in balances:
                balance = balances[asset]['total']
                self.initial_balances[asset] = balance
                logger.info(f"   {asset}: {balance:.4f}")
        
        return True
    
    async def simulate_price_movement(self, symbol):
        """模拟价格变动并执行交易"""
        try:
            # 获取当前市场价格
            ticker = await self.exchange.get_ticker(symbol)
            current_bid = ticker['bid']
            current_ask = ticker['ask']
            spread = current_ask - current_bid
            spread_percentage = (spread / current_bid) * 100
            
            logger.info(f"\n📊 {symbol}")
            logger.info(f"   买价: ${current_bid:,.2f}")
            logger.info(f"   卖价: ${current_ask:,.2f}")
            logger.info(f"   价差: ${spread:.2f} ({spread_percentage:.3f}%)")
            
            # 模拟套利策略：当价差大于0.1%时执行交易
            if spread_percentage > 0.1 and len(self.trades) < 10:
                amount = self.test_amount.get(symbol, 0.001)
                
                # 买入（以略高于买价的价格挂单）
                buy_price = current_bid * 1.0001
                logger.info(f"   📈 下买单: {amount} @ ${buy_price:,.2f}")
                
                try:
                    buy_order = await self.exchange.place_order(
                        symbol=symbol,
                        side='buy',
                        amount=amount,
                        price=buy_price
                    )
                    
                    self.trades.append({
                        'time': datetime.now(),
                        'symbol': symbol,
                        'side': 'buy',
                        'amount': amount,
                        'price': buy_price,
                        'order_id': buy_order['orderId']
                    })
                    
                    logger.info(f"   ✅ 买单成功: ID {buy_order['orderId']}")
                    
                    # 立即下一个卖单（套利）
                    sell_price = current_ask * 0.9999
                    logger.info(f"   📉 下卖单: {amount} @ ${sell_price:,.2f}")
                    
                    sell_order = await self.exchange.place_order(
                        symbol=symbol,
                        side='sell',
                        amount=amount,
                        price=sell_price
                    )
                    
                    self.trades.append({
                        'time': datetime.now(),
                        'symbol': symbol,
                        'side': 'sell',
                        'amount': amount,
                        'price': sell_price,
                        'order_id': sell_order['orderId']
                    })
                    
                    logger.info(f"   ✅ 卖单成功: ID {sell_order['orderId']}")
                    
                    # 计算理论利润
                    profit = (sell_price - buy_price) * amount
                    profit_rate = ((sell_price - buy_price) / buy_price) * 100
                    logger.info(f"   💰 理论利润: ${profit:.4f} ({profit_rate:.3f}%)")
                    
                except Exception as e:
                    logger.error(f"   ❌ 交易失败: {e}")
                    
        except Exception as e:
            logger.error(f"获取 {symbol} 数据失败: {e}")
    
    async def show_performance(self):
        """显示交易表现"""
        runtime = datetime.now() - self.start_time
        
        logger.info("\n" + "="*50)
        logger.info("📊 交易统计")
        logger.info("="*50)
        logger.info(f"运行时间: {runtime}")
        logger.info(f"总交易数: {len(self.trades)}")
        
        # 按交易对统计
        symbol_stats = {}
        for trade in self.trades:
            symbol = trade['symbol']
            if symbol not in symbol_stats:
                symbol_stats[symbol] = {'buy': 0, 'sell': 0}
            symbol_stats[symbol][trade['side']] += 1
        
        for symbol, stats in symbol_stats.items():
            logger.info(f"{symbol}: 买单 {stats['buy']}, 卖单 {stats['sell']}")
        
        # 显示当前余额
        try:
            balances = await self.exchange.get_balance()
            logger.info("\n💰 当前余额:")
            
            for asset in ['USDT', 'BTC', 'ETH', 'BNB']:
                if asset in balances:
                    current = balances[asset]['total']
                    initial = self.initial_balances.get(asset, 0)
                    change = current - initial
                    logger.info(f"   {asset}: {current:.4f} (变化: {change:+.4f})")
                    
        except Exception as e:
            logger.error(f"获取余额失败: {e}")
    
    async def run(self):
        """运行演示"""
        if not await self.initialize():
            return
        
        logger.info("\n开始监控和交易...")
        logger.info("提示: 按 Ctrl+C 停止\n")
        
        try:
            while True:
                # 检查所有交易对
                for symbol in self.symbols:
                    await self.simulate_price_movement(symbol)
                
                # 每5轮显示一次统计
                if len(self.trades) > 0 and len(self.trades) % 10 == 0:
                    await self.show_performance()
                
                # 等待
                await asyncio.sleep(10)
                
        except KeyboardInterrupt:
            logger.info("\n⏹️  停止交易...")
            await self.show_performance()
            
        finally:
            await self.exchange.disconnect()
            logger.info("\n👋 演示结束")

async def main():
    demo = BinanceTestnetDemo()
    await demo.run()

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════╗
║          Binance 测试网套利演示                  ║
║                                                  ║
║  功能：                                          ║
║  1. 实时监控多个交易对价格                       ║
║  2. 当价差超过阈值时自动交易                     ║
║  3. 展示套利策略的基本原理                       ║
║  4. 统计交易表现                                 ║
╚══════════════════════════════════════════════════╝
""")
    
    asyncio.run(main())