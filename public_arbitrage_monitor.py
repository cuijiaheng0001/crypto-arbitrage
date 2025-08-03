#!/usr/bin/env python3
"""
公共API套利监控器
只监控价格差，不执行交易
适合在没有所有API密钥的情况下测试
"""

import ccxt
import time
import os
from datetime import datetime
from dotenv import load_dotenv
import logging

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PublicArbitrageMonitor:
    def __init__(self):
        """初始化公共API监控器"""
        
        # 初始化交易所（只使用公共API）
        self.exchanges = {
            'bitget': ccxt.bitget({
                'enableRateLimit': True,
                'timeout': 10000
            }),
            'bybit': ccxt.bybit({
                'enableRateLimit': True,
                'timeout': 10000
            })
        }
        
        # 配置
        self.config = {
            'symbols': ['BTC/USDT', 'ETH/USDT', 'SOL/USDT'],
            'min_profit_percentage': 0.3,  # 最小利润率 0.3%
            'check_interval': 10,  # 检查间隔
            'fees': {
                'bitget': 0.001,  # 0.1%
                'bybit': 0.001    # 0.1%
            }
        }
        
        self.stats = {
            'opportunities': 0,
            'total_checks': 0,
            'start_time': datetime.now(),
            'best_spread': 0
        }
        
        logger.info("🚀 公共API套利监控器已启动")
        logger.info(f"📊 监控交易对: {', '.join(self.config['symbols'])}")
    
    def get_public_ticker(self, exchange_name, symbol):
        """获取公共ticker数据"""
        try:
            exchange = self.exchanges[exchange_name]
            ticker = exchange.fetch_ticker(symbol)
            return {
                'bid': float(ticker['bid']) if ticker['bid'] else 0,
                'ask': float(ticker['ask']) if ticker['ask'] else 0,
                'last': float(ticker['last']) if ticker['last'] else 0,
                'timestamp': ticker['timestamp']
            }
        except Exception as e:
            logger.warning(f"⚠️ 获取 {exchange_name} {symbol} 失败: {str(e)[:100]}")
            return None
    
    def analyze_spread(self, symbol):
        """分析价格差"""
        
        # 获取价格数据
        bitget_ticker = self.get_public_ticker('bitget', symbol)
        bybit_ticker = self.get_public_ticker('bybit', symbol)
        
        if not bitget_ticker or not bybit_ticker:
            return None
        
        # 计算价格差
        bitget_price = bitget_ticker['last']
        bybit_price = bybit_ticker['last']
        
        if bitget_price == 0 or bybit_price == 0:
            return None
        
        # 计算价差百分比
        spread_percentage = abs(bitget_price - bybit_price) / ((bitget_price + bybit_price) / 2) * 100
        
        # 确定套利方向
        if bitget_price > bybit_price:
            direction = "Bybit买入 -> Bitget卖出"
            potential_profit = (bitget_price - bybit_price) / bybit_price * 100
        else:
            direction = "Bitget买入 -> Bybit卖出"
            potential_profit = (bybit_price - bitget_price) / bitget_price * 100
        
        # 减去手续费
        total_fees = sum(self.config['fees'].values()) * 100  # 转换为百分比
        net_profit = potential_profit - total_fees
        
        return {
            'symbol': symbol,
            'bitget_price': bitget_price,
            'bybit_price': bybit_price,
            'spread_percentage': spread_percentage,
            'direction': direction,
            'gross_profit': potential_profit,
            'net_profit': net_profit,
            'is_opportunity': net_profit > self.config['min_profit_percentage'],
            'timestamp': datetime.now()
        }
    
    def log_analysis(self, analysis):
        """记录分析结果"""
        if not analysis:
            return
        
        symbol = analysis['symbol']
        
        # 更新统计
        self.stats['best_spread'] = max(self.stats['best_spread'], analysis['spread_percentage'])
        
        if analysis['is_opportunity']:
            self.stats['opportunities'] += 1
            logger.info("🎯" + "="*50)
            logger.info(f"💰 发现套利机会! {symbol}")
            logger.info(f"📊 {analysis['direction']}")
            logger.info(f"💵 毛利润: {analysis['gross_profit']:.3f}%")
            logger.info(f"💸 净利润: {analysis['net_profit']:.3f}%")
            logger.info(f"📈 Bitget: ${analysis['bitget_price']:.2f}")
            logger.info(f"📉 Bybit: ${analysis['bybit_price']:.2f}")
            logger.info("🎯" + "="*50)
        else:
            # 正常价格显示
            status = "🟢" if analysis['spread_percentage'] < 0.1 else "🟡" if analysis['spread_percentage'] < 0.2 else "🔴"
            logger.info(f"{status} {symbol}: Bitget ${analysis['bitget_price']:.2f} | "
                       f"Bybit ${analysis['bybit_price']:.2f} | "
                       f"价差 {analysis['spread_percentage']:.3f}%")
    
    def print_summary(self):
        """打印汇总信息"""
        runtime = datetime.now() - self.stats['start_time']
        
        print("\n" + "="*60)
        print("📊 监控汇总")
        print("="*60)
        print(f"⏱️ 运行时间: {runtime}")
        print(f"🔍 检查次数: {self.stats['total_checks']}")
        print(f"🎯 机会次数: {self.stats['opportunities']}")
        print(f"📈 最大价差: {self.stats['best_spread']:.3f}%")
        
        if self.stats['opportunities'] > 0:
            opportunity_rate = (self.stats['opportunities'] / (self.stats['total_checks'] * len(self.config['symbols']))) * 100
            print(f"📊 机会率: {opportunity_rate:.2f}%")
        
        print("="*60)
    
    def run(self):
        """运行监控"""
        logger.info("🎯 开始价格差监控...")
        logger.info("按 Ctrl+C 停止监控\n")
        
        try:
            while True:
                self.stats['total_checks'] += 1
                logger.info(f"🔍 第 {self.stats['total_checks']} 次检查...")
                
                for symbol in self.config['symbols']:
                    try:
                        analysis = self.analyze_spread(symbol)
                        self.log_analysis(analysis)
                        time.sleep(1)  # 避免API限制
                    except Exception as e:
                        logger.error(f"❌ 分析 {symbol} 时出错: {str(e)}")
                
                # 每5次显示汇总
                if self.stats['total_checks'] % 5 == 0:
                    self.print_summary()
                
                logger.info(f"😴 等待 {self.config['check_interval']} 秒...\n")
                time.sleep(self.config['check_interval'])
                
        except KeyboardInterrupt:
            logger.info("\n🛑 用户停止监控")
        except Exception as e:
            logger.error(f"❌ 监控出错: {str(e)}")
        finally:
            self.print_summary()
            logger.info("👋 监控已停止")

def main():
    """主函数"""
    try:
        monitor = PublicArbitrageMonitor()
        monitor.run()
    except Exception as e:
        logger.error(f"❌ 启动失败: {str(e)}")

if __name__ == "__main__":
    main()