#!/usr/bin/env python3
"""
增强版三角套利机器人
专注于 Bitget 单交易所内的三角套利机会
"""

import ccxt
import time
import os
import logging
from datetime import datetime
from dotenv import load_dotenv
import requests
import sys
sys.path.append('/root/crypto-arbitrage')
from triangular_arbitrage import TriangularArbitrage

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/triangular_arbitrage.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EnhancedTriangularArbitrage:
    def __init__(self):
        """初始化增强版三角套利机器人"""
        
        # 初始化交易所
        self.exchange = ccxt.bitget({
            'apiKey': os.getenv('BITGET_API_KEY'),
            'secret': os.getenv('BITGET_API_SECRET'),
            'password': os.getenv('BITGET_PASSPHRASE'),
            'enableRateLimit': True,
            'timeout': 30000
        })
        
        # 三角套利引擎
        self.arbitrage_engine = TriangularArbitrage(
            self.exchange, 
            min_profit_percentage=0.1  # 0.1% 最小利润
        )
        
        # 配置
        self.config = {
            'check_interval': 10,  # 10秒检查一次
            'max_trade_amount': 100,  # 最大交易金额 100 USDT
            'min_volume': 1000,  # 最小成交量要求
            'execution_mode': 'simulation',  # simulation 或 live
        }
        
        # 统计
        self.stats = {
            'opportunities_found': 0,
            'profitable_opportunities': 0,
            'total_profit': 0.0,
            'start_time': datetime.now()
        }
        
        # Telegram 通知
        self.telegram_enabled = os.getenv('TELEGRAM_ENABLED', 'false').lower() == 'true'
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID', '')
        
        logger.info("🚀 增强版三角套利机器人启动")
        self._send_telegram("🚀 三角套利机器人已启动\n\n正在监控 Bitget 交易所...")
    
    def _send_telegram(self, message):
        """发送 Telegram 通知"""
        if not self.telegram_enabled:
            return
        
        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            data = {
                'chat_id': self.telegram_chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            requests.post(url, data=data, timeout=5)
        except Exception as e:
            logger.error(f"Telegram 发送失败: {e}")
    
    def scan_opportunities(self):
        """扫描三角套利机会"""
        try:
            # 获取所有市场数据
            logger.info("获取市场数据...")
            tickers = self.exchange.fetch_tickers()
            
            # 过滤出有足够流动性的交易对
            liquid_tickers = {}
            for symbol, ticker in tickers.items():
                if ticker.get('quoteVolume', 0) > self.config['min_volume']:
                    liquid_tickers[symbol] = ticker
            
            logger.info(f"流动性充足的交易对: {len(liquid_tickers)}")
            
            # 构建价格图
            self.arbitrage_engine.build_graph(liquid_tickers)
            
            # 寻找套利机会
            opportunities = self.arbitrage_engine.find_arbitrage_cycles('USDT', max_length=4)
            
            if opportunities:
                self.stats['opportunities_found'] += len(opportunities)
                
                for opp in opportunities:
                    # 扣除手续费后的净利润
                    net_profit = opp['profit_percentage'] - opp['fees_estimated']
                    
                    if net_profit > 0:
                        self.stats['profitable_opportunities'] += 1
                        
                        # 记录机会
                        logger.info(f"🎯 发现套利机会!")
                        logger.info(f"路径: {' → '.join(opp['path'])}")
                        logger.info(f"毛利润: {opp['profit_percentage']:.3f}%")
                        logger.info(f"手续费: {opp['fees_estimated']:.3f}%")
                        logger.info(f"净利润: {net_profit:.3f}%")
                        
                        # 如果利润足够高，发送通知
                        if net_profit > 0.2:  # 0.2% 以上发送通知
                            self._notify_opportunity(opp, net_profit)
                        
                        # 执行交易（如果是实盘模式）
                        if self.config['execution_mode'] == 'live' and net_profit > 0.3:
                            self._execute_arbitrage(opp)
            
            return len(opportunities)
            
        except Exception as e:
            logger.error(f"扫描出错: {e}")
            return 0
    
    def _notify_opportunity(self, opportunity, net_profit):
        """通知套利机会"""
        message = f"""
💎 <b>三角套利机会!</b>

📍 路径: {' → '.join(opportunity['path'])}
💰 净利润: {net_profit:.3f}%
📊 毛利润: {opportunity['profit_percentage']:.3f}%
💸 手续费: {opportunity['fees_estimated']:.3f}%

交易步骤:
"""
        for step in opportunity['path_info'][:3]:  # 只显示前3步
            message += f"\n{step['action'].upper()} {step['symbol']} @ {step['price']:.4f}"
        
        self._send_telegram(message)
    
    def _execute_arbitrage(self, opportunity):
        """执行套利交易"""
        try:
            result = self.arbitrage_engine.execute_arbitrage(
                opportunity, 
                self.config['max_trade_amount']
            )
            
            if result:
                self.stats['total_profit'] += result['profit']
                
                message = f"""
✅ <b>三角套利执行成功!</b>

💎 路径: {' → '.join(result['path'])}
💵 利润: ${result['profit']:.4f}
📊 利润率: {result['profit_percentage']:.3f}%
💰 最终余额: ${result['final_amount']:.2f}
"""
                self._send_telegram(message)
                
        except Exception as e:
            logger.error(f"执行失败: {e}")
    
    def print_statistics(self):
        """打印统计信息"""
        runtime = datetime.now() - self.stats['start_time']
        
        logger.info("="*60)
        logger.info("📊 三角套利统计")
        logger.info(f"⏱️ 运行时间: {runtime}")
        logger.info(f"🔍 发现机会: {self.stats['opportunities_found']}")
        logger.info(f"💰 有利可图: {self.stats['profitable_opportunities']}")
        logger.info(f"💵 总利润: ${self.stats['total_profit']:.4f}")
        logger.info("="*60)
    
    def run(self):
        """运行三角套利机器人"""
        logger.info("开始扫描三角套利机会...")
        logger.info("按 Ctrl+C 停止")
        
        scan_count = 0
        
        try:
            while True:
                scan_count += 1
                logger.info(f"\n🔄 第 {scan_count} 次扫描...")
                
                # 扫描机会
                opportunities = self.scan_opportunities()
                
                # 每10次扫描打印一次统计
                if scan_count % 10 == 0:
                    self.print_statistics()
                
                # 等待下次扫描
                time.sleep(self.config['check_interval'])
                
        except KeyboardInterrupt:
            logger.info("\n🛑 用户停止机器人")
            self.print_statistics()
            self._send_telegram("🛑 三角套利机器人已停止")
        except Exception as e:
            logger.error(f"运行错误: {e}")
            self._send_telegram(f"❌ 三角套利机器人异常: {str(e)}")

def main():
    """主函数"""
    bot = EnhancedTriangularArbitrage()
    bot.run()

if __name__ == "__main__":
    main()