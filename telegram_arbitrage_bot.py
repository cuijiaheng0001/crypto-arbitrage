#!/usr/bin/env python3
"""
增强版套利机器人 v3.0
集成 Telegram 通知功能
"""

import ccxt
import time
import json
import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
import logging
import asyncio
import threading

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/telegram_arbitrage.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TelegramNotifier:
    """Telegram 通知管理器"""
    
    def __init__(self):
        self.enabled = os.getenv('TELEGRAM_ENABLED', 'false').lower() == 'true'
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID', '')
        
        if self.enabled and self.bot_token and self.chat_id:
            self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
            logger.info("✅ Telegram 通知已启用")
            self.send_message("🚀 套利机器人已启动！\n\n开始监控市场机会...")
        else:
            logger.info("ℹ️ Telegram 通知未启用")
    
    def send_message(self, message, parse_mode='HTML'):
        """发送 Telegram 消息"""
        if not self.enabled:
            return
        
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': parse_mode
            }
            
            response = requests.post(url, data=data, timeout=10)
            if response.status_code != 200:
                logger.warning(f"Telegram 发送失败: {response.text}")
        except Exception as e:
            logger.error(f"Telegram 发送错误: {str(e)}")

class EnhancedArbitrageBot:
    def __init__(self, simulation_mode=True):
        """初始化增强版套利机器人"""
        
        self.simulation_mode = simulation_mode
        self.notifier = TelegramNotifier()
        
        # 初始化交易所
        self.exchanges = self._init_exchanges()
        
        # 交易配置（降低阈值以便测试）
        self.config = {
            'symbols': ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'DOGE/USDT', 'XRP/USDT', 'ADA/USDT'],
            'min_profit_percentage': 0.005,  # 降低到 0.005% 以便测试
            'max_trade_amount': 50.0,
            'check_interval': 3.0,
            'slippage_tolerance': 0.02,
            'max_daily_trades': 50,
            'fees': {
                'bitget': {'maker': 0.001, 'taker': 0.001},
                'bybit': {'maker': 0.001, 'taker': 0.001}
            }
        }
        
        # 账户状态
        self.account = {
            'initial_balance': 1000.0,
            'current_balance': 1000.0,
            'daily_pnl': 0.0,
            'total_pnl': 0.0,
            'trades_today': 0,
            'positions': {}
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
            'trade_history': [],
            'last_notification_time': datetime.now()
        }
        
        # 启动通知
        self._send_startup_notification()
    
    def _init_exchanges(self):
        """初始化交易所"""
        exchanges = {}
        
        try:
            # Bitget
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
            
            # Bybit
            exchanges['bybit'] = ccxt.bybit({
                'enableRateLimit': True,
                'timeout': 10000
            })
            
            logger.info("✅ 交易所连接初始化成功")
            
        except Exception as e:
            logger.error(f"❌ 交易所初始化失败: {str(e)}")
            self.notifier.send_message(f"❌ 交易所初始化失败: {str(e)}")
            raise
        
        return exchanges
    
    def _send_startup_notification(self):
        """发送启动通知"""
        mode = "模拟模式" if self.simulation_mode else "实盘模式"
        
        message = f"""
<b>🚀 套利机器人启动成功</b>

📊 <b>运行模式</b>: {mode}
💰 <b>初始资金</b>: ${self.account['initial_balance']:.2f}
🎯 <b>最小利润率</b>: {self.config['min_profit_percentage']}%
📈 <b>监控币种</b>: {', '.join(self.config['symbols'])}
⏱️ <b>检查间隔</b>: {self.config['check_interval']}秒

<i>市场监控已开始，发现机会将立即通知您！</i>
"""
        self.notifier.send_message(message)
    
    def get_orderbook(self, exchange_name, symbol, limit=5):
        """获取订单簿数据"""
        try:
            exchange = self.exchanges[exchange_name]
            orderbook = exchange.fetch_order_book(symbol, limit)
            return orderbook
        except Exception as e:
            logger.warning(f"⚠️ 获取 {exchange_name} {symbol} 订单簿失败: {str(e)[:100]}")
            return None
    
    def calculate_arbitrage_opportunity(self, symbol):
        """计算套利机会"""
        
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
        buy_price = bitget_best_ask
        sell_price = bybit_best_bid
        
        # 计算利润
        buy_fee = buy_price * self.config['fees']['bitget']['taker']
        sell_fee = sell_price * self.config['fees']['bybit']['taker']
        
        total_cost = buy_price + buy_fee
        total_revenue = sell_price - sell_fee
        profit_per_unit = total_revenue - total_cost
        profit_percentage = (profit_per_unit / total_cost) * 100
        
        if profit_percentage > self.config['min_profit_percentage']:
            max_quantity = min(
                self.config['max_trade_amount'] / buy_price,
                bitget_book['asks'][0][1] * 0.8,  # 80% 的挂单量
                bybit_book['bids'][0][1] * 0.8
            )
            
            opportunities.append({
                'direction': 'Bitget → Bybit',
                'buy_exchange': 'Bitget',
                'sell_exchange': 'Bybit',
                'buy_price': buy_price,
                'sell_price': sell_price,
                'profit_percentage': profit_percentage,
                'profit_per_unit': profit_per_unit,
                'max_quantity': max_quantity,
                'estimated_profit': profit_per_unit * max_quantity,
                'symbol': symbol
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
                bybit_book['asks'][0][1] * 0.8,
                bitget_book['bids'][0][1] * 0.8
            )
            
            opportunities.append({
                'direction': 'Bybit → Bitget',
                'buy_exchange': 'Bybit',
                'sell_exchange': 'Bitget',
                'buy_price': buy_price,
                'sell_price': sell_price,
                'profit_percentage': profit_percentage,
                'profit_per_unit': profit_per_unit,
                'max_quantity': max_quantity,
                'estimated_profit': profit_per_unit * max_quantity,
                'symbol': symbol
            })
        
        return {
            'symbol': symbol,
            'timestamp': datetime.now(),
            'opportunities': opportunities,
            'spread': abs(bitget_best_ask - bybit_best_bid) / bitget_best_ask * 100
        }
    
    def send_opportunity_notification(self, opportunity):
        """发送套利机会通知"""
        
        # 限制通知频率（每分钟最多一次同币种通知）
        current_time = datetime.now()
        if (current_time - self.stats['last_notification_time']).seconds < 60:
            return
        
        message = f"""
🎯 <b>发现套利机会!</b>

💎 <b>币种</b>: {opportunity['symbol']}
📊 <b>方向</b>: {opportunity['direction']}
💰 <b>利润率</b>: {opportunity['profit_percentage']:.3f}%
💵 <b>预期利润</b>: ${opportunity['estimated_profit']:.4f}

📈 <b>买入</b>: ${opportunity['buy_price']:.2f} ({opportunity['buy_exchange']})
📉 <b>卖出</b>: ${opportunity['sell_price']:.2f} ({opportunity['sell_exchange']})
📦 <b>最大数量</b>: {opportunity['max_quantity']:.6f}

<i>机器人正在模拟执行交易...</i>
"""
        
        self.notifier.send_message(message)
        self.stats['last_notification_time'] = current_time
    
    def send_trade_notification(self, trade_record):
        """发送交易执行通知"""
        
        emoji = "✅" if trade_record['profit'] > 0 else "❌"
        
        message = f"""
{emoji} <b>交易执行完成</b>

💎 <b>币种</b>: {trade_record['symbol']}
📊 <b>方向</b>: {trade_record['direction']}
📦 <b>数量</b>: {trade_record['quantity']:.6f}
💰 <b>利润</b>: ${trade_record['profit']:.4f}
💸 <b>手续费</b>: ${trade_record['fees']:.4f}
🏦 <b>余额</b>: ${trade_record['balance_after']:.2f}

📈 <b>今日盈亏</b>: ${self.account['daily_pnl']:.2f}
🎯 <b>今日交易</b>: {self.account['trades_today']}次
"""
        
        self.notifier.send_message(message)
    
    def send_daily_summary(self):
        """发送每日统计"""
        
        if self.stats['executed_trades'] == 0:
            return
        
        success_rate = (self.stats['successful_trades'] / self.stats['executed_trades']) * 100
        
        message = f"""
📊 <b>每日交易统计</b>

⏰ <b>运行时间</b>: {datetime.now() - self.stats['start_time']}
💰 <b>当前余额</b>: ${self.account['current_balance']:.2f}
📈 <b>总盈亏</b>: ${self.account['total_pnl']:.2f} ({self.account['total_pnl']/self.account['initial_balance']*100:+.2f}%)

🎯 <b>发现机会</b>: {self.stats['total_opportunities']}次
✅ <b>执行交易</b>: {self.stats['executed_trades']}次
🎉 <b>成功率</b>: {success_rate:.1f}%
💸 <b>手续费</b>: ${self.stats['total_fees_paid']:.2f}

🏆 <b>最佳交易</b>: ${self.stats['best_profit']:.4f}
📉 <b>最差交易</b>: ${self.stats['worst_loss']:.4f}
"""
        
        self.notifier.send_message(message)
    
    def simulate_trade_execution(self, opportunity):
        """模拟交易执行"""
        
        if self.account['trades_today'] >= self.config['max_daily_trades']:
            logger.warning("📊 今日交易次数已达上限")
            return False
        
        # 模拟执行
        execution_delay = 2.0
        slippage = 0.001
        
        # 计算实际执行价格
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
        
        # 发送通知
        self.send_trade_notification(trade_record)
        
        # 记录日志
        logger.info(f"💰 交易执行: {opportunity['symbol']} {opportunity['direction']} 利润: ${total_profit:.4f}")
        
        return True
    
    def run(self):
        """运行套利机器人"""
        logger.info("🚀 开始监控套利机会...")
        
        try:
            check_count = 0
            
            while True:
                check_count += 1
                
                for symbol in self.config['symbols']:
                    try:
                        # 分析套利机会
                        analysis = self.calculate_arbitrage_opportunity(symbol)
                        
                        if analysis and analysis['opportunities']:
                            self.stats['total_opportunities'] += len(analysis['opportunities'])
                            
                            for opp in analysis['opportunities']:
                                logger.info(f"🎯 发现机会: {symbol} {opp['direction']} "
                                          f"利润率: {opp['profit_percentage']:.3f}%")
                                
                                # 发送通知
                                self.send_opportunity_notification(opp)
                                
                                # 尝试执行交易
                                if self.simulate_trade_execution(opp):
                                    time.sleep(5)
                        
                        else:
                            # 显示当前价差
                            if analysis:
                                logger.info(f"📊 {symbol}: 价差 {analysis['spread']:.3f}%")
                        
                        time.sleep(0.5)  # 避免API限制
                        
                    except Exception as e:
                        logger.error(f"❌ 处理 {symbol} 时出错: {str(e)}")
                
                # 每100次检查发送一次统计
                if check_count % 100 == 0 and self.stats['executed_trades'] > 0:
                    self.send_daily_summary()
                
                time.sleep(self.config['check_interval'])
                
        except KeyboardInterrupt:
            logger.info("\n🛑 用户停止机器人")
            self.notifier.send_message("🛑 套利机器人已停止")
        except Exception as e:
            logger.error(f"❌ 运行错误: {str(e)}")
            self.notifier.send_message(f"❌ 机器人异常: {str(e)}")
        finally:
            self.send_daily_summary()
            logger.info("👋 套利机器人已停止")

def main():
    """主函数"""
    
    # 创建日志目录
    os.makedirs('logs', exist_ok=True)
    
    print("🚀 增强版套利机器人 v3.0 (带Telegram通知)")
    print("🎯 启动模拟模式，监控极小价差机会")
    
    try:
        bot = EnhancedArbitrageBot(simulation_mode=True)
        bot.run()
        
    except Exception as e:
        logger.error(f"❌ 启动失败: {str(e)}")

if __name__ == "__main__":
    main()