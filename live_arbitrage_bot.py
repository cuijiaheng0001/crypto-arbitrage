#!/usr/bin/env python3
"""
实时套利机器人 v2.0
包含模拟交易、风险管理、实时统计
"""

import ccxt
import time
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import logging

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/live_arbitrage.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LiveArbitrageBot:
    def __init__(self, simulation_mode=True):
        """初始化实时套利机器人"""
        
        self.simulation_mode = simulation_mode  # 模拟模式
        
        # 初始化交易所
        self.exchanges = self._init_exchanges()
        
        # 交易配置
        self.config = {
            'symbols': ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'DOGE/USDT'],
            'min_profit_percentage': float(os.getenv('MIN_PROFIT_PERCENTAGE', 0.05)),  # 降低到0.05%
            'max_trade_amount': float(os.getenv('MAX_TRADE_AMOUNT', 50)),  # 降低到50 USDT
            'check_interval': float(os.getenv('PRICE_UPDATE_INTERVAL', 5)),  # 5秒检查
            'slippage_tolerance': 0.02,  # 2% 滑点容忍度
            'max_daily_trades': 20,  # 每日最大交易次数
            'fees': {
                'bitget': {'maker': 0.001, 'taker': 0.001},  # 0.1%
                'bybit': {'maker': 0.001, 'taker': 0.001}    # 0.1%
            }
        }
        
        # 账户状态
        self.account = {
            'initial_balance': 1000.0,  # 初始余额 1000 USDT
            'current_balance': 1000.0,
            'daily_pnl': 0.0,
            'total_pnl': 0.0,
            'trades_today': 0,
            'positions': {}  # 当前持仓
        }
        
        # 统计数据
        self.stats = {
            'total_opportunities': 0,
            'executed_trades': 0,
            'successful_trades': 0,
            'failed_trades': 0,
            'total_fees_paid': 0.0,
            'best_profit': 0.0,
            'worst_loss': 0.0,
            'start_time': datetime.now(),
            'last_reset_time': datetime.now(),
            'trade_history': []
        }
        
        # 创建日志目录
        os.makedirs('logs', exist_ok=True)
        
        mode_text = "模拟模式" if simulation_mode else "实盘模式"
        logger.info(f"🚀 实时套利机器人启动 - {mode_text}")
        logger.info(f"💰 初始资金: ${self.account['initial_balance']:.2f}")
        logger.info(f"📊 监控币种: {', '.join(self.config['symbols'])}")
        logger.info(f"🎯 最小利润率: {self.config['min_profit_percentage']}%")
    
    def _init_exchanges(self):
        """初始化交易所"""
        exchanges = {}
        
        try:
            # Bitget (使用您已配置的API)
            if self.simulation_mode:
                exchanges['bitget'] = ccxt.bitget({
                    'enableRateLimit': True,
                    'timeout': 10000
                })
            else:
                exchanges['bitget'] = ccxt.bitget({
                    'apiKey': os.getenv('BITGET_API_KEY'),
                    'secret': os.getenv('BITGET_API_SECRET'),
                    'password': os.getenv('BITGET_PASSPHRASE'),
                    'enableRateLimit': True
                })
            
            # Bybit (使用公共API或您的API)
            exchanges['bybit'] = ccxt.bybit({
                'enableRateLimit': True,
                'timeout': 10000
            })
            
            logger.info("✅ 交易所连接初始化成功")
            
        except Exception as e:
            logger.error(f"❌ 交易所初始化失败: {str(e)}")
            raise
        
        return exchanges
    
    def get_orderbook(self, exchange_name, symbol, limit=5):
        """获取订单簿数据"""
        try:
            exchange = self.exchanges[exchange_name]
            orderbook = exchange.fetch_order_book(symbol, limit)
            return orderbook
        except Exception as e:
            logger.warning(f"⚠️ 获取 {exchange_name} {symbol} 订单簿失败: {str(e)[:100]}")
            return None
    
    def calculate_precise_arbitrage(self, symbol):
        """精确计算套利机会"""
        
        # 获取订单簿
        bitget_book = self.get_orderbook('bitget', symbol)
        bybit_book = self.get_orderbook('bybit', symbol)
        
        if not bitget_book or not bybit_book:
            return None
        
        # 获取最优价格
        bitget_best_bid = bitget_book['bids'][0][0] if bitget_book['bids'] else 0
        bitget_best_ask = bitget_book['asks'][0][0] if bitget_book['asks'] else 0
        bybit_best_bid = bybit_book['bids'][0][0] if bybit_book['bids'] else 0
        bybit_best_ask = bybit_book['asks'][0][0] if bybit_book['asks'] else 0
        
        if not all([bitget_best_bid, bitget_best_ask, bybit_best_bid, bybit_best_ask]):
            return None
        
        opportunities = []
        
        # 场景1: Bitget买入 -> Bybit卖出
        buy_price = bitget_best_ask  # 在Bitget以卖价买入
        sell_price = bybit_best_bid  # 在Bybit以买价卖出
        
        # 计算利润（考虑手续费）
        buy_fee = buy_price * self.config['fees']['bitget']['taker']
        sell_fee = sell_price * self.config['fees']['bybit']['taker'] 
        
        total_cost = buy_price + buy_fee
        total_revenue = sell_price - sell_fee
        profit_per_unit = total_revenue - total_cost
        profit_percentage = (profit_per_unit / total_cost) * 100
        
        if profit_percentage > self.config['min_profit_percentage']:
            # 计算最大交易量
            max_quantity = min(
                self.config['max_trade_amount'] / buy_price,  # 资金限制
                bitget_book['asks'][0][1],  # Bitget卖单量
                bybit_book['bids'][0][1]    # Bybit买单量
            )
            
            opportunities.append({
                'direction': 'Bitget -> Bybit',
                'buy_exchange': 'Bitget',
                'sell_exchange': 'Bybit',
                'buy_price': buy_price,
                'sell_price': sell_price,
                'profit_percentage': profit_percentage,
                'profit_per_unit': profit_per_unit,
                'max_quantity': max_quantity,
                'estimated_profit': profit_per_unit * max_quantity
            })
        
        # 场景2: Bybit买入 -> Bitget卖出
        buy_price = bybit_best_ask
        sell_price = bitget_best_bid
        
        buy_fee = buy_price * self.config['fees']['bybit']['taker']
        sell_fee = sell_price * self.config['fees']['bitget']['taker']
        
        total_cost = buy_price + buy_fee
        total_revenue = sell_price - sell_fee
        profit_per_unit = total_revenue - total_cost
        profit_percentage = (profit_per_unit / total_cost) * 100
        
        if profit_percentage > self.config['min_profit_percentage']:
            max_quantity = min(
                self.config['max_trade_amount'] / buy_price,
                bybit_book['asks'][0][1],
                bitget_book['bids'][0][1]
            )
            
            opportunities.append({
                'direction': 'Bybit -> Bitget',
                'buy_exchange': 'Bybit', 
                'sell_exchange': 'Bitget',
                'buy_price': buy_price,
                'sell_price': sell_price,
                'profit_percentage': profit_percentage,
                'profit_per_unit': profit_per_unit,
                'max_quantity': max_quantity,
                'estimated_profit': profit_per_unit * max_quantity
            })
        
        return {
            'symbol': symbol,
            'timestamp': datetime.now(),
            'opportunities': opportunities,
            'market_data': {
                'bitget_bid': bitget_best_bid,
                'bitget_ask': bitget_best_ask,
                'bybit_bid': bybit_best_bid,
                'bybit_ask': bybit_best_ask
            }
        }
    
    def simulate_trade_execution(self, opportunity):
        """模拟交易执行"""
        
        if self.account['trades_today'] >= self.config['max_daily_trades']:
            logger.warning("📊 今日交易次数已达上限")
            return False
        
        # 模拟执行时间和滑点
        execution_delay = 2.0  # 2秒执行延迟
        slippage = 0.001  # 0.1% 滑点
        
        # 计算实际执行价格（考虑滑点）
        actual_buy_price = opportunity['buy_price'] * (1 + slippage)
        actual_sell_price = opportunity['sell_price'] * (1 - slippage)
        
        # 重新计算利润
        buy_fee = actual_buy_price * self.config['fees'][opportunity['buy_exchange'].lower()]['taker']
        sell_fee = actual_sell_price * self.config['fees'][opportunity['sell_exchange'].lower()]['taker']
        
        total_cost = actual_buy_price + buy_fee
        total_revenue = actual_sell_price - sell_fee
        actual_profit = total_revenue - total_cost
        
        # 确定交易数量
        trade_quantity = min(opportunity['max_quantity'], self.config['max_trade_amount'] / actual_buy_price)
        
        if actual_profit <= 0:
            logger.warning(f"⚠️ 考虑滑点后无利润，取消交易")
            return False
        
        # 执行模拟交易
        total_profit = actual_profit * trade_quantity
        total_fees = (buy_fee + sell_fee) * trade_quantity
        
        # 更新账户
        self.account['current_balance'] += total_profit
        self.account['daily_pnl'] += total_profit
        self.account['total_pnl'] += total_profit
        self.account['trades_today'] += 1
        
        # 更新统计
        self.stats['executed_trades'] += 1
        self.stats['total_fees_paid'] += total_fees
        
        if total_profit > 0:
            self.stats['successful_trades'] += 1
            self.stats['best_profit'] = max(self.stats['best_profit'], total_profit)
        else:
            self.stats['failed_trades'] += 1
            self.stats['worst_loss'] = min(self.stats['worst_loss'], total_profit)
        
        # 记录交易
        trade_record = {
            'timestamp': datetime.now(),
            'symbol': opportunity['symbol'],
            'direction': opportunity['direction'],
            'quantity': trade_quantity,
            'buy_price': actual_buy_price,
            'sell_price': actual_sell_price,
            'profit': total_profit,
            'fees': total_fees,
            'balance_after': self.account['current_balance']
        }
        
        self.stats['trade_history'].append(trade_record)
        
        # 记录日志
        logger.info("🎯" + "="*60)
        logger.info(f"💰 模拟交易执行成功! {opportunity['symbol']}")
        logger.info(f"📊 方向: {opportunity['direction']}")
        logger.info(f"💎 数量: {trade_quantity:.6f}")
        logger.info(f"💵 利润: ${total_profit:.4f}")
        logger.info(f"🏦 余额: ${self.account['current_balance']:.2f}")
        logger.info("🎯" + "="*60)
        
        return True
    
    def check_daily_reset(self):
        """检查是否需要重置每日统计"""
        now = datetime.now()
        if now.date() > self.stats['last_reset_time'].date():
            self.account['trades_today'] = 0
            self.account['daily_pnl'] = 0.0
            self.stats['last_reset_time'] = now
            logger.info("🌅 新的一天开始，重置每日统计")
    
    def print_dashboard(self):
        """打印仪表板"""
        runtime = datetime.now() - self.stats['start_time']
        
        print("\n" + "="*80)
        print("📊 实时套利机器人仪表板")
        print("="*80)
        print(f"⏱️ 运行时间: {runtime}")
        print(f"💰 当前余额: ${self.account['current_balance']:.2f} (初始: ${self.account['initial_balance']:.2f})")
        print(f"📈 总盈亏: ${self.account['total_pnl']:.2f} ({(self.account['total_pnl']/self.account['initial_balance']*100):+.2f}%)")
        print(f"📊 今日盈亏: ${self.account['daily_pnl']:.2f}")
        print(f"🔄 今日交易: {self.account['trades_today']}/{self.config['max_daily_trades']}")
        print()
        print(f"🎯 发现机会: {self.stats['total_opportunities']}")
        print(f"✅ 执行交易: {self.stats['executed_trades']}")
        print(f"🎉 成功交易: {self.stats['successful_trades']}")
        print(f"❌ 失败交易: {self.stats['failed_trades']}")
        
        if self.stats['executed_trades'] > 0:
            success_rate = (self.stats['successful_trades'] / self.stats['executed_trades']) * 100
            print(f"📊 成功率: {success_rate:.1f}%")
        
        if self.stats['best_profit'] > 0:
            print(f"🏆 最佳交易: ${self.stats['best_profit']:.4f}")
        
        print("="*80)
    
    def run(self):
        """运行套利机器人"""
        logger.info("🚀 开始实时套利监控...")
        logger.info("按 Ctrl+C 停止")
        
        try:
            while True:
                self.check_daily_reset()
                
                for symbol in self.config['symbols']:
                    try:
                        # 分析套利机会
                        analysis = self.calculate_precise_arbitrage(symbol)
                        
                        if analysis and analysis['opportunities']:
                            self.stats['total_opportunities'] += len(analysis['opportunities'])
                            
                            for opp in analysis['opportunities']:
                                logger.info(f"🎯 发现机会: {symbol} {opp['direction']} "
                                          f"利润率: {opp['profit_percentage']:.3f}%")
                                
                                # 尝试执行交易
                                if self.simulate_trade_execution(opp):
                                    # 执行成功后短暂暂停
                                    time.sleep(5)
                        
                        else:
                            # 显示当前价格状态
                            if analysis:
                                data = analysis['market_data']
                                spread = abs(data['bitget_ask'] - data['bybit_bid']) / data['bitget_ask'] * 100
                                logger.info(f"📊 {symbol}: 价差 {spread:.3f}% "
                                          f"(Bitget: ${data['bitget_ask']:.2f} | Bybit: ${data['bybit_bid']:.2f})")
                        
                        time.sleep(1)  # 避免API限制
                        
                    except Exception as e:
                        logger.error(f"❌ 处理 {symbol} 时出错: {str(e)}")
                
                # 定期显示仪表板
                if self.stats['executed_trades'] > 0 and self.stats['executed_trades'] % 5 == 0:
                    self.print_dashboard()
                
                time.sleep(self.config['check_interval'])
                
        except KeyboardInterrupt:
            logger.info("\n🛑 用户停止机器人")
        except Exception as e:
            logger.error(f"❌ 运行错误: {str(e)}")
        finally:
            self.print_dashboard()
            logger.info("👋 套利机器人已停止")

def main():
    """主函数"""
    
    # 创建日志目录
    os.makedirs('logs', exist_ok=True)
    
    print("🚀 实时套利机器人 v2.0")
    print("🎯 启动模拟模式")
    
    try:
        # 直接使用模拟模式
        bot = LiveArbitrageBot(simulation_mode=True)
        bot.run()
        
    except Exception as e:
        logger.error(f"❌ 启动失败: {str(e)}")

if __name__ == "__main__":
    main()