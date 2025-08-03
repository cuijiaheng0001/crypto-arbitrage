#!/usr/bin/env python3
"""
Binance 测试网 + 公共 API 套利监控
使用 Binance 测试网进行实际交易，其他交易所使用公共 API 监控价格
"""

import asyncio
import os
import time
import ccxt
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

class MultiExchangeArbitrage:
    def __init__(self):
        # Binance 测试网（可交易）
        self.binance_testnet = BinanceTestnetExchange(
            api_key=os.getenv('BINANCE_API_KEY'),
            secret_key=os.getenv('BINANCE_SECRET_KEY')
        )
        
        # 其他交易所（仅价格监控）
        self.price_monitors = {
            'binance_spot': ccxt.binance({'enableRateLimit': True}),
            'bybit': ccxt.bybit({
                'enableRateLimit': True,
                'options': {'defaultType': 'spot'}
            }),
            'okx': ccxt.okx({'enableRateLimit': True}),
            'kucoin': ccxt.kucoin({'enableRateLimit': True})
        }
        
        # 监控的交易对
        self.symbols = ['BTC/USDT', 'ETH/USDT']
        
        # 套利参数
        self.min_profit_percentage = 0.3  # 最小利润率
        self.test_amount = {
            'BTC/USDT': 0.001,
            'ETH/USDT': 0.01
        }
        
        # 统计
        self.opportunities_found = 0
        self.trades_executed = 0
        self.start_time = datetime.now()
        
    async def initialize(self):
        """初始化"""
        logger.info("🚀 启动多交易所套利监控")
        logger.info("="*60)
        
        # 连接 Binance 测试网
        await self.binance_testnet.connect()
        
        # 显示余额
        balances = await self.binance_testnet.get_balance()
        logger.info("💰 Binance 测试网余额:")
        for asset in ['USDT', 'BTC', 'ETH']:
            if asset in balances:
                logger.info(f"   {asset}: {balances[asset]['total']:.4f}")
        
        logger.info("\n📊 监控交易所:")
        logger.info("   - Binance Testnet (可交易)")
        for name in self.price_monitors.keys():
            logger.info(f"   - {name} (仅监控)")
        
        return True
    
    def get_public_price(self, exchange_name, symbol):
        """获取公共 API 价格"""
        try:
            exchange = self.price_monitors[exchange_name]
            ticker = exchange.fetch_ticker(symbol)
            return {
                'bid': ticker['bid'],
                'ask': ticker['ask'],
                'last': ticker['last'],
                'timestamp': ticker['timestamp']
            }
        except Exception as e:
            logger.debug(f"获取 {exchange_name} {symbol} 价格失败: {e}")
            return None
    
    async def find_arbitrage_opportunities(self, symbol):
        """查找套利机会"""
        # 获取 Binance 测试网价格
        try:
            testnet_ticker = await self.binance_testnet.get_ticker(symbol)
            testnet_bid = testnet_ticker['bid']
            testnet_ask = testnet_ticker['ask']
        except Exception as e:
            logger.error(f"获取测试网价格失败: {e}")
            return
        
        # 获取其他交易所价格
        market_prices = {}
        for name, exchange in self.price_monitors.items():
            price = self.get_public_price(name, symbol)
            if price:
                market_prices[name] = price
        
        if not market_prices:
            return
        
        # 分析套利机会
        opportunities = []
        
        # 1. 测试网买入，其他交易所卖出的机会
        for exchange_name, price_data in market_prices.items():
            other_bid = price_data['bid']
            
            if other_bid > testnet_ask:
                profit_rate = ((other_bid - testnet_ask) / testnet_ask - 0.002) * 100  # 扣除手续费
                
                if profit_rate > self.min_profit_percentage:
                    opportunities.append({
                        'type': 'buy_testnet_sell_other',
                        'symbol': symbol,
                        'buy_exchange': 'binance_testnet',
                        'sell_exchange': exchange_name,
                        'buy_price': testnet_ask,
                        'sell_price': other_bid,
                        'profit_rate': profit_rate
                    })
        
        # 2. 其他交易所买入，测试网卖出的机会
        for exchange_name, price_data in market_prices.items():
            other_ask = price_data['ask']
            
            if testnet_bid > other_ask:
                profit_rate = ((testnet_bid - other_ask) / other_ask - 0.002) * 100
                
                if profit_rate > self.min_profit_percentage:
                    opportunities.append({
                        'type': 'buy_other_sell_testnet',
                        'symbol': symbol,
                        'buy_exchange': exchange_name,
                        'sell_exchange': 'binance_testnet',
                        'buy_price': other_ask,
                        'sell_price': testnet_bid,
                        'profit_rate': profit_rate
                    })
        
        # 显示最佳机会
        if opportunities:
            best_opp = max(opportunities, key=lambda x: x['profit_rate'])
            self.opportunities_found += 1
            
            logger.info(f"""
🎯 套利机会 #{self.opportunities_found}
交易对: {best_opp['symbol']}
买入: {best_opp['buy_exchange']} @ ${best_opp['buy_price']:,.2f}
卖出: {best_opp['sell_exchange']} @ ${best_opp['sell_price']:,.2f}
利润率: {best_opp['profit_rate']:.3f}%
""")
            
            # 如果涉及测试网，执行模拟交易
            if 'testnet' in best_opp['buy_exchange'] or 'testnet' in best_opp['sell_exchange']:
                await self.execute_testnet_trade(best_opp)
    
    async def execute_testnet_trade(self, opportunity):
        """在测试网执行交易"""
        try:
            symbol = opportunity['symbol']
            amount = self.test_amount.get(symbol, 0.001)
            
            if opportunity['type'] == 'buy_testnet_sell_other':
                # 在测试网买入
                logger.info(f"📈 在 Binance 测试网买入 {amount} @ ${opportunity['buy_price']:,.2f}")
                
                order = await self.binance_testnet.place_order(
                    symbol=symbol,
                    side='buy',
                    amount=amount,
                    price=opportunity['buy_price']
                )
                
                logger.info(f"✅ 买单成功: 订单ID {order['orderId']}")
                self.trades_executed += 1
                
            elif opportunity['type'] == 'buy_other_sell_testnet':
                # 在测试网卖出
                logger.info(f"📉 在 Binance 测试网卖出 {amount} @ ${opportunity['sell_price']:,.2f}")
                
                order = await self.binance_testnet.place_order(
                    symbol=symbol,
                    side='sell',
                    amount=amount,
                    price=opportunity['sell_price']
                )
                
                logger.info(f"✅ 卖单成功: 订单ID {order['orderId']}")
                self.trades_executed += 1
                
        except Exception as e:
            logger.error(f"执行交易失败: {e}")
    
    async def monitor(self):
        """持续监控"""
        check_count = 0
        
        while True:
            try:
                check_count += 1
                
                # 检查所有交易对
                for symbol in self.symbols:
                    await self.find_arbitrage_opportunities(symbol)
                
                # 定期显示统计
                if check_count % 20 == 0:
                    runtime = datetime.now() - self.start_time
                    logger.info(f"""
📊 运行统计:
运行时间: {runtime}
检查次数: {check_count}
发现机会: {self.opportunities_found}
执行交易: {self.trades_executed}
""")
                
                # 等待
                await asyncio.sleep(5)
                
            except KeyboardInterrupt:
                logger.info("\n👋 停止监控")
                break
                
            except Exception as e:
                logger.error(f"监控错误: {e}")
                await asyncio.sleep(10)
    
    async def run(self):
        """运行"""
        if await self.initialize():
            await self.monitor()
        
        await self.binance_testnet.disconnect()

async def main():
    bot = MultiExchangeArbitrage()
    await bot.run()

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════╗
║        多交易所套利监控 (Binance 测试网)         ║
║                                                  ║
║  功能：                                          ║
║  - 使用 Binance 测试网进行实际交易              ║
║  - 监控多个交易所的实时价格                     ║
║  - 发现套利机会时自动在测试网交易               ║
║  - 无需其他交易所 API 密钥                      ║
╚══════════════════════════════════════════════════╝
""")
    
    asyncio.run(main())