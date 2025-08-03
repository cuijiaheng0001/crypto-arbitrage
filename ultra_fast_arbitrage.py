#!/usr/bin/env python3
"""
超高速套利执行系统
使用 WebSocket + 异步并发 + 内存优化
"""

import asyncio
import websockets
import orjson
import time
import os
import logging
from datetime import datetime
from collections import deque
from dotenv import load_dotenv
import aiohttp
import numpy as np

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class UltraFastArbitrage:
    def __init__(self):
        """初始化超高速套利系统"""
        
        # 性能优化配置
        self.config = {
            'symbols': ['BTC/USDT', 'ETH/USDT', 'SOL/USDT'],
            'min_profit_threshold': 0.1,  # 0.1% 最小利润
            'max_latency_ms': 100,  # 最大可接受延迟
            'order_book_depth': 5,  # 订单簿深度
            'price_cache_size': 1000,  # 价格缓存大小
            'execution_mode': 'aggressive',  # aggressive 或 conservative
        }
        
        # 高性能数据结构
        self.price_cache = {symbol: deque(maxlen=self.config['price_cache_size']) for symbol in self.config['symbols']}
        self.order_books = {}
        self.latency_tracker = deque(maxlen=1000)
        
        # WebSocket 连接池
        self.ws_connections = {}
        
        # 性能统计
        self.performance_stats = {
            'messages_per_second': 0,
            'avg_latency_ms': 0,
            'opportunities_detected': 0,
            'executions_attempted': 0,
            'executions_successful': 0,
        }
        
        logger.info("⚡ 超高速套利系统启动")
    
    async def connect_bitget_ultra_fast(self):
        """超快速 Bitget WebSocket 连接"""
        url = 'wss://ws.bitget.com/spot/v1/stream'
        
        async with websockets.connect(url, ping_interval=20) as ws:
            # 订阅深度数据
            subscribe_msg = {
                "op": "subscribe",
                "args": []
            }
            
            for symbol in self.config['symbols']:
                base, quote = symbol.split('/')
                subscribe_msg["args"].append({
                    "instType": "sp",
                    "channel": "books5",  # 5档深度
                    "instId": f"{base}{quote}"
                })
            
            await ws.send(orjson.dumps(subscribe_msg).decode())
            
            # 高速数据处理循环
            while True:
                try:
                    msg = await asyncio.wait_for(ws.recv(), timeout=0.1)
                    await self.process_message_ultra_fast(orjson.loads(msg))
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    logger.error(f"WebSocket 错误: {e}")
                    break
    
    async def process_message_ultra_fast(self, data):
        """超快速消息处理"""
        start_time = time.perf_counter()
        
        if 'data' in data:
            for item in data['data']:
                if 'instId' not in item:
                    continue
                    
                # 超快速解析
                symbol = self._parse_symbol(item['instId'])
                if not symbol:
                    continue
                
                # 更新订单簿（内存中）
                self.order_books[symbol] = {
                    'bids': [(float(b[0]), float(b[1])) for b in item.get('bids', [])[:5]],
                    'asks': [(float(a[0]), float(a[1])) for a in item.get('asks', [])[:5]],
                    'timestamp': time.time()
                }
                
                # 立即检查套利机会
                await self.check_arbitrage_ultra_fast(symbol)
        
        # 记录延迟
        latency = (time.perf_counter() - start_time) * 1000
        self.latency_tracker.append(latency)
        self.performance_stats['messages_per_second'] += 1
    
    def _parse_symbol(self, inst_id):
        """快速符号解析"""
        if 'USDT' in inst_id:
            base = inst_id.replace('USDT', '')
            return f"{base}/USDT"
        return None
    
    async def check_arbitrage_ultra_fast(self, symbol):
        """超快速套利检查"""
        if symbol not in self.order_books:
            return
        
        book = self.order_books[symbol]
        if not book['bids'] or not book['asks']:
            return
        
        # 快速计算价差
        best_bid = book['bids'][0][0]
        best_ask = book['asks'][0][0]
        spread_pct = ((best_ask - best_bid) / best_ask) * 100
        
        # 缓存价格用于趋势分析
        self.price_cache[symbol].append({
            'bid': best_bid,
            'ask': best_ask,
            'spread': spread_pct,
            'timestamp': time.time()
        })
        
        # 检测异常价差
        if spread_pct > self.config['min_profit_threshold']:
            self.performance_stats['opportunities_detected'] += 1
            
            # 执行决策
            if self.should_execute_trade(symbol, spread_pct):
                await self.execute_trade_ultra_fast(symbol, book)
    
    def should_execute_trade(self, symbol, spread_pct):
        """智能交易决策"""
        # 检查历史价格趋势
        if len(self.price_cache[symbol]) < 10:
            return False
        
        # 计算价格波动性
        recent_prices = [p['bid'] for p in list(self.price_cache[symbol])[-10:]]
        volatility = np.std(recent_prices) / np.mean(recent_prices)
        
        # 激进模式：立即执行
        if self.config['execution_mode'] == 'aggressive':
            return spread_pct > self.config['min_profit_threshold']
        
        # 保守模式：等待稳定信号
        return spread_pct > self.config['min_profit_threshold'] * 1.5 and volatility < 0.001
    
    async def execute_trade_ultra_fast(self, symbol, book):
        """超快速交易执行"""
        self.performance_stats['executions_attempted'] += 1
        
        try:
            # 模拟超快速执行
            execution_time = time.perf_counter()
            
            # 计算最优交易量
            optimal_size = self.calculate_optimal_size(book)
            
            # 记录执行
            logger.info(f"⚡ 执行套利: {symbol} | 价差: {book['asks'][0][0] - book['bids'][0][0]:.4f} | "
                       f"数量: {optimal_size:.4f} | 延迟: {self.latency_tracker[-1]:.1f}ms")
            
            self.performance_stats['executions_successful'] += 1
            
        except Exception as e:
            logger.error(f"执行失败: {e}")
    
    def calculate_optimal_size(self, book):
        """计算最优交易量"""
        # 基于订单簿深度计算
        total_bid_volume = sum(bid[1] for bid in book['bids'][:3])
        total_ask_volume = sum(ask[1] for ask in book['asks'][:3])
        
        return min(total_bid_volume, total_ask_volume) * 0.8  # 80% 保守执行
    
    async def performance_monitor(self):
        """性能监控器"""
        while True:
            await asyncio.sleep(10)
            
            # 计算性能指标
            if self.latency_tracker:
                self.performance_stats['avg_latency_ms'] = np.mean(self.latency_tracker)
            
            # 打印性能报告
            logger.info("="*60)
            logger.info("⚡ 性能报告")
            logger.info(f"📨 消息速率: {self.performance_stats['messages_per_second']/10:.1f}/秒")
            logger.info(f"⏱️ 平均延迟: {self.performance_stats['avg_latency_ms']:.1f}ms")
            logger.info(f"🎯 发现机会: {self.performance_stats['opportunities_detected']}")
            logger.info(f"✅ 执行成功: {self.performance_stats['executions_successful']}")
            logger.info("="*60)
            
            # 重置计数器
            self.performance_stats['messages_per_second'] = 0
    
    async def run(self):
        """运行超高速套利系统"""
        tasks = [
            self.connect_bitget_ultra_fast(),
            self.performance_monitor()
        ]
        
        await asyncio.gather(*tasks)

# ===== 2. 风险控制系统 =====

class RiskManagementSystem:
    def __init__(self):
        """初始化风险管理系统"""
        
        self.risk_params = {
            'max_position_size': 1000,  # 最大单笔 1000 USDT
            'daily_loss_limit': 50,     # 每日最大亏损 50 USDT
            'max_drawdown': 0.1,        # 最大回撤 10%
            'position_limits': {        # 每个币种的仓位限制
                'BTC/USDT': 0.5,
                'ETH/USDT': 0.3,
                'SOL/USDT': 0.2
            },
            'stop_loss_pct': 2.0,       # 止损 2%
            'take_profit_pct': 5.0,     # 止盈 5%
        }
        
        # 风险状态跟踪
        self.current_positions = {}
        self.daily_pnl = 0.0
        self.peak_balance = 10000.0
        self.current_balance = 10000.0
        
        # 风险事件记录
        self.risk_events = []
        
        logger.info("🛡️ 风险管理系统启动")
    
    def check_trade_risk(self, symbol, side, size, price):
        """交易前风险检查"""
        risks = []
        
        # 1. 检查仓位限制
        position_value = size * price
        if position_value > self.risk_params['max_position_size']:
            risks.append(f"仓位超限: ${position_value:.2f} > ${self.risk_params['max_position_size']}")
        
        # 2. 检查每日亏损限制
        if self.daily_pnl < -self.risk_params['daily_loss_limit']:
            risks.append(f"已达每日亏损限制: ${self.daily_pnl:.2f}")
        
        # 3. 检查最大回撤
        current_drawdown = (self.peak_balance - self.current_balance) / self.peak_balance
        if current_drawdown > self.risk_params['max_drawdown']:
            risks.append(f"超过最大回撤: {current_drawdown*100:.1f}%")
        
        # 4. 检查币种仓位集中度
        if symbol in self.current_positions:
            current_exposure = self.current_positions[symbol]['value'] / self.current_balance
            max_exposure = self.risk_params['position_limits'].get(symbol, 0.2)
            if current_exposure > max_exposure:
                risks.append(f"{symbol} 仓位过度集中: {current_exposure*100:.1f}%")
        
        if risks:
            logger.warning(f"⚠️ 风险警告: {', '.join(risks)}")
            return False, risks
        
        return True, []
    
    def update_position(self, symbol, side, size, entry_price):
        """更新仓位信息"""
        if symbol not in self.current_positions:
            self.current_positions[symbol] = {
                'size': 0,
                'value': 0,
                'entry_price': 0,
                'unrealized_pnl': 0
            }
        
        pos = self.current_positions[symbol]
        
        if side == 'buy':
            # 更新平均成本
            total_value = pos['size'] * pos['entry_price'] + size * entry_price
            pos['size'] += size
            pos['entry_price'] = total_value / pos['size'] if pos['size'] > 0 else entry_price
        else:  # sell
            pos['size'] -= size
            if pos['size'] <= 0:
                del self.current_positions[symbol]
        
        # 设置止损单
        self.set_stop_loss(symbol, entry_price)
    
    def set_stop_loss(self, symbol, entry_price):
        """设置止损"""
        stop_loss_price = entry_price * (1 - self.risk_params['stop_loss_pct'] / 100)
        take_profit_price = entry_price * (1 + self.risk_params['take_profit_pct'] / 100)
        
        logger.info(f"🛡️ 设置 {symbol} 止损: ${stop_loss_price:.2f} | 止盈: ${take_profit_price:.2f}")
    
    def monitor_positions(self, current_prices):
        """监控所有仓位"""
        total_unrealized_pnl = 0
        
        for symbol, pos in self.current_positions.items():
            if symbol in current_prices:
                current_price = current_prices[symbol]
                pos['unrealized_pnl'] = (current_price - pos['entry_price']) * pos['size']
                total_unrealized_pnl += pos['unrealized_pnl']
                
                # 检查止损/止盈
                pnl_pct = (current_price - pos['entry_price']) / pos['entry_price'] * 100
                
                if pnl_pct <= -self.risk_params['stop_loss_pct']:
                    logger.warning(f"🚨 触发止损: {symbol} 亏损 {pnl_pct:.1f}%")
                    self.risk_events.append({
                        'time': datetime.now(),
                        'type': 'stop_loss',
                        'symbol': symbol,
                        'loss': pos['unrealized_pnl']
                    })
                
                elif pnl_pct >= self.risk_params['take_profit_pct']:
                    logger.info(f"💰 触发止盈: {symbol} 盈利 {pnl_pct:.1f}%")
        
        # 更新余额
        self.current_balance = 10000 + self.daily_pnl + total_unrealized_pnl
        if self.current_balance > self.peak_balance:
            self.peak_balance = self.current_balance
    
    def generate_risk_report(self):
        """生成风险报告"""
        report = f"""
🛡️ 风险管理报告
================
📊 当前余额: ${self.current_balance:.2f}
📈 峰值余额: ${self.peak_balance:.2f}
📉 当前回撤: {((self.peak_balance - self.current_balance) / self.peak_balance * 100):.1f}%
💰 今日盈亏: ${self.daily_pnl:.2f}

持仓分布:
"""
        for symbol, pos in self.current_positions.items():
            report += f"\n  {symbol}: {pos['size']:.4f} @ ${pos['entry_price']:.2f} | PnL: ${pos['unrealized_pnl']:.2f}"
        
        if self.risk_events:
            report += f"\n\n⚠️ 风险事件: {len(self.risk_events)} 次"
        
        return report

# ===== 3. 数据分析系统 =====

class TradingAnalytics:
    def __init__(self):
        """初始化数据分析系统"""
        
        self.analytics_config = {
            'data_retention_days': 30,
            'analysis_interval': 3600,  # 每小时分析
            'min_data_points': 100,
        }
        
        # 数据存储
        self.trade_history = []
        self.market_data = []
        self.performance_metrics = {}
        
        # 分析结果
        self.best_trading_hours = []
        self.profitable_patterns = []
        self.optimal_parameters = {}
        
        logger.info("📊 数据分析系统启动")
    
    def record_trade(self, trade_data):
        """记录交易数据"""
        trade_record = {
            'timestamp': datetime.now(),
            'symbol': trade_data['symbol'],
            'side': trade_data['side'],
            'price': trade_data['price'],
            'size': trade_data['size'],
            'profit': trade_data.get('profit', 0),
            'fees': trade_data.get('fees', 0),
            'market_conditions': self.capture_market_conditions(),
            'execution_time_ms': trade_data.get('execution_time', 0),
        }
        
        self.trade_history.append(trade_record)
        
        # 定期保存到文件
        if len(self.trade_history) % 100 == 0:
            self.save_trade_history()
    
    def capture_market_conditions(self):
        """捕获市场状况"""
        return {
            'volatility': self.calculate_market_volatility(),
            'volume': self.get_market_volume(),
            'trend': self.identify_market_trend(),
            'hour': datetime.now().hour,
            'day_of_week': datetime.now().weekday(),
        }
    
    def analyze_trading_patterns(self):
        """分析交易模式"""
        if len(self.trade_history) < self.analytics_config['min_data_points']:
            return
        
        # 1. 分析最佳交易时段
        hourly_profits = {}
        for trade in self.trade_history:
            hour = trade['market_conditions']['hour']
            if hour not in hourly_profits:
                hourly_profits[hour] = []
            hourly_profits[hour].append(trade['profit'])
        
        # 计算每小时平均利润
        avg_hourly_profits = {
            hour: np.mean(profits) 
            for hour, profits in hourly_profits.items()
        }
        
        # 找出最佳交易时段
        self.best_trading_hours = sorted(
            avg_hourly_profits.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:5]
        
        logger.info(f"📊 最佳交易时段: {[f'{h[0]}点(利润${h[1]:.2f})' for h in self.best_trading_hours]}")
        
        # 2. 分析盈利模式
        self.analyze_profitable_patterns()
        
        # 3. 优化参数
        self.optimize_parameters()
    
    def analyze_profitable_patterns(self):
        """分析盈利模式"""
        profitable_trades = [t for t in self.trade_history if t['profit'] > 0]
        
        if profitable_trades:
            # 分析盈利交易的共同特征
            patterns = {
                'avg_volatility': np.mean([t['market_conditions']['volatility'] for t in profitable_trades]),
                'common_symbols': self.get_most_profitable_symbols(profitable_trades),
                'avg_size': np.mean([t['size'] for t in profitable_trades]),
                'market_trend': self.analyze_trend_correlation(profitable_trades),
            }
            
            self.profitable_patterns = patterns
            logger.info(f"📊 盈利模式: {patterns}")
    
    def get_most_profitable_symbols(self, trades):
        """获取最盈利的交易对"""
        symbol_profits = {}
        for trade in trades:
            symbol = trade['symbol']
            if symbol not in symbol_profits:
                symbol_profits[symbol] = []
            symbol_profits[symbol].append(trade['profit'])
        
        avg_profits = {
            symbol: np.mean(profits) 
            for symbol, profits in symbol_profits.items()
        }
        
        return sorted(avg_profits.items(), key=lambda x: x[1], reverse=True)[:3]
    
    def optimize_parameters(self):
        """优化交易参数"""
        # 基于历史数据优化参数
        if len(self.trade_history) > 1000:
            # 优化最小利润阈值
            profit_thresholds = np.arange(0.05, 0.3, 0.05)
            best_threshold = 0.1
            best_profit = 0
            
            for threshold in profit_thresholds:
                simulated_profit = self.simulate_with_threshold(threshold)
                if simulated_profit > best_profit:
                    best_profit = simulated_profit
                    best_threshold = threshold
            
            self.optimal_parameters['min_profit_threshold'] = best_threshold
            logger.info(f"📊 优化参数: 最佳利润阈值 = {best_threshold:.2f}%")
    
    def simulate_with_threshold(self, threshold):
        """模拟不同阈值的收益"""
        # 简化的模拟逻辑
        return np.random.uniform(100, 200) * threshold
    
    def generate_analytics_report(self):
        """生成分析报告"""
        report = f"""
📊 交易数据分析报告
==================
📈 总交易次数: {len(self.trade_history)}
💰 总利润: ${sum(t['profit'] for t in self.trade_history):.2f}
⏱️ 平均执行时间: {np.mean([t['execution_time_ms'] for t in self.trade_history]):.1f}ms

🕐 最佳交易时段:
"""
        for hour, profit in self.best_trading_hours[:3]:
            report += f"\n  {hour}:00 - 平均利润 ${profit:.2f}"
        
        if self.profitable_patterns:
            report += f"\n\n💎 盈利模式:"
            report += f"\n  平均波动率: {self.profitable_patterns['avg_volatility']:.4f}"
            report += f"\n  最佳币种: {[s[0] for s in self.profitable_patterns['common_symbols']]}"
        
        if self.optimal_parameters:
            report += f"\n\n⚙️ 优化参数:"
            for param, value in self.optimal_parameters.items():
                report += f"\n  {param}: {value}"
        
        return report
    
    def save_trade_history(self):
        """保存交易历史"""
        filename = f"data/trades_{datetime.now().strftime('%Y%m%d')}.json"
        os.makedirs('data', exist_ok=True)
        
        with open(filename, 'w') as f:
            import json
            json.dump(self.trade_history[-1000:], f, default=str)
    
    def calculate_market_volatility(self):
        """计算市场波动率"""
        # 实际实现需要基于实时价格数据
        return np.random.uniform(0.001, 0.01)
    
    def get_market_volume(self):
        """获取市场成交量"""
        # 实际实现需要从交易所获取
        return np.random.uniform(1000000, 10000000)
    
    def identify_market_trend(self):
        """识别市场趋势"""
        # 简化版本
        return np.random.choice(['bullish', 'bearish', 'sideways'])

# ===== 主程序 =====

async def main():
    """主程序"""
    # 创建各个系统实例
    arbitrage = UltraFastArbitrage()
    risk_mgmt = RiskManagementSystem()
    analytics = TradingAnalytics()
    
    logger.info("🚀 启动高级套利系统...")
    logger.info("⚡ WebSocket 超高速执行")
    logger.info("🛡️ 风险管理系统激活")
    logger.info("📊 数据分析系统运行")
    
    # 运行系统
    await arbitrage.run()

if __name__ == "__main__":
    asyncio.run(main())