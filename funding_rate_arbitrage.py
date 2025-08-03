#!/usr/bin/env python3
"""
资金费率套利机器人
利用永续合约与现货之间的资金费率差异进行套利
"""

import ccxt
import time
import os
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
import requests
import pandas as pd

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/funding_rate_arbitrage.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FundingRateArbitrage:
    def __init__(self):
        """初始化资金费率套利机器人"""
        
        # 初始化交易所（需要支持合约交易）
        self.spot_exchange = ccxt.bitget({
            'apiKey': os.getenv('BITGET_API_KEY'),
            'secret': os.getenv('BITGET_API_SECRET'),
            'password': os.getenv('BITGET_PASSPHRASE'),
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot'  # 现货市场
            }
        })
        
        self.futures_exchange = ccxt.bitget({
            'apiKey': os.getenv('BITGET_API_KEY'),
            'secret': os.getenv('BITGET_API_SECRET'),
            'password': os.getenv('BITGET_PASSPHRASE'),
            'enableRateLimit': True,
            'options': {
                'defaultType': 'swap'  # 永续合约
            }
        })
        
        # 配置
        self.config = {
            'symbols': ['BTC/USDT', 'ETH/USDT', 'SOL/USDT'],
            'min_funding_rate': 0.01,  # 最小资金费率 0.01% (年化 10.95%)
            'max_position_size': 1000,  # 最大持仓 1000 USDT
            'check_interval': 300,  # 5分钟检查一次
            'auto_close_threshold': -0.005,  # 资金费率低于 -0.005% 时平仓
        }
        
        # 当前持仓
        self.positions = {}
        
        # 统计
        self.stats = {
            'total_funding_collected': 0.0,
            'active_positions': 0,
            'total_positions_opened': 0,
            'start_time': datetime.now()
        }
        
        # Telegram 通知
        self.telegram_enabled = os.getenv('TELEGRAM_ENABLED', 'false').lower() == 'true'
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID', '')
        
        logger.info("🚀 资金费率套利机器人启动")
        self._send_telegram("🚀 资金费率套利机器人已启动\n\n监控币种: " + ", ".join(self.config['symbols']))
    
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
    
    def get_funding_rates(self):
        """获取所有币种的资金费率"""
        funding_rates = {}
        
        try:
            for symbol in self.config['symbols']:
                # 获取永续合约的资金费率
                futures_symbol = symbol.replace('/', '')  # BTC/USDT -> BTCUSDT
                
                # Bitget API 获取资金费率
                funding_info = self.futures_exchange.fetch_funding_rate(symbol)
                
                funding_rates[symbol] = {
                    'rate': funding_info['fundingRate'],
                    'timestamp': funding_info['timestamp'],
                    'next_funding_time': funding_info['fundingDatetime'],
                    'annualized_rate': funding_info['fundingRate'] * 3 * 365 * 100  # 年化百分比
                }
                
                logger.info(f"{symbol} 资金费率: {funding_info['fundingRate']*100:.4f}% "
                          f"(年化: {funding_rates[symbol]['annualized_rate']:.2f}%)")
                
        except Exception as e:
            logger.error(f"获取资金费率失败: {e}")
        
        return funding_rates
    
    def check_arbitrage_opportunities(self, funding_rates):
        """检查套利机会"""
        opportunities = []
        
        for symbol, rate_info in funding_rates.items():
            rate = rate_info['rate']
            
            # 正资金费率：做空永续合约 + 做多现货
            if rate > self.config['min_funding_rate'] / 100:
                opportunities.append({
                    'symbol': symbol,
                    'type': 'positive_funding',
                    'rate': rate,
                    'annualized': rate_info['annualized_rate'],
                    'action': 'short_futures_long_spot'
                })
                
                logger.info(f"💰 发现正资金费率套利机会: {symbol} "
                          f"费率: {rate*100:.4f}% (年化: {rate_info['annualized_rate']:.2f}%)")
            
            # 负资金费率：做多永续合约 + 做空现货（或不持有）
            elif rate < -self.config['min_funding_rate'] / 100:
                opportunities.append({
                    'symbol': symbol,
                    'type': 'negative_funding',
                    'rate': rate,
                    'annualized': rate_info['annualized_rate'],
                    'action': 'long_futures_short_spot'
                })
                
                logger.info(f"💰 发现负资金费率套利机会: {symbol} "
                          f"费率: {rate*100:.4f}% (年化: {rate_info['annualized_rate']:.2f}%)")
        
        return opportunities
    
    def open_funding_position(self, opportunity):
        """开仓套利仓位"""
        symbol = opportunity['symbol']
        
        try:
            # 检查是否已有仓位
            if symbol in self.positions:
                logger.warning(f"{symbol} 已有仓位，跳过")
                return False
            
            # 获取当前价格
            spot_ticker = self.spot_exchange.fetch_ticker(symbol)
            futures_ticker = self.futures_exchange.fetch_ticker(symbol)
            
            spot_price = spot_ticker['last']
            futures_price = futures_ticker['last']
            
            # 计算仓位大小
            position_size = min(
                self.config['max_position_size'] / spot_price,
                self.config['max_position_size'] / futures_price
            )
            
            logger.info(f"开仓 {symbol}:")
            logger.info(f"  现货价格: ${spot_price:.2f}")
            logger.info(f"  合约价格: ${futures_price:.2f}")
            logger.info(f"  仓位大小: {position_size:.4f}")
            
            # 记录仓位（模拟交易）
            self.positions[symbol] = {
                'type': opportunity['type'],
                'size': position_size,
                'spot_entry_price': spot_price,
                'futures_entry_price': futures_price,
                'funding_rate': opportunity['rate'],
                'entry_time': datetime.now(),
                'funding_collected': 0.0
            }
            
            self.stats['active_positions'] += 1
            self.stats['total_positions_opened'] += 1
            
            # 发送通知
            message = f"""
💎 <b>资金费率套利开仓!</b>

📍 币种: {symbol}
💰 资金费率: {opportunity['rate']*100:.4f}% (年化: {opportunity['annualized']:.2f}%)
📊 策略: {'做空合约+做多现货' if opportunity['type'] == 'positive_funding' else '做多合约+做空现货'}
💵 仓位价值: ${position_size * spot_price:.2f}
"""
            self._send_telegram(message)
            
            return True
            
        except Exception as e:
            logger.error(f"开仓失败 {symbol}: {e}")
            return False
    
    def update_positions(self, funding_rates):
        """更新持仓状态"""
        for symbol, position in list(self.positions.items()):
            try:
                current_rate = funding_rates.get(symbol, {}).get('rate', 0)
                
                # 计算已收取的资金费
                hours_held = (datetime.now() - position['entry_time']).total_seconds() / 3600
                funding_periods = int(hours_held / 8)  # 每8小时结算一次
                
                if funding_periods > 0:
                    funding_collected = position['size'] * position['futures_entry_price'] * position['funding_rate'] * funding_periods
                    position['funding_collected'] = funding_collected
                    self.stats['total_funding_collected'] += funding_collected
                
                # 检查是否需要平仓
                if position['type'] == 'positive_funding' and current_rate < self.config['auto_close_threshold']:
                    self.close_position(symbol, "资金费率转负")
                elif position['type'] == 'negative_funding' and current_rate > -self.config['auto_close_threshold']:
                    self.close_position(symbol, "资金费率转正")
                    
            except Exception as e:
                logger.error(f"更新仓位失败 {symbol}: {e}")
    
    def close_position(self, symbol, reason):
        """平仓"""
        if symbol not in self.positions:
            return
        
        position = self.positions[symbol]
        
        logger.info(f"平仓 {symbol}: {reason}")
        logger.info(f"  已收取资金费: ${position['funding_collected']:.4f}")
        
        # 发送通知
        message = f"""
🔻 <b>资金费率套利平仓</b>

📍 币种: {symbol}
❌ 原因: {reason}
💰 已收资金费: ${position['funding_collected']:.4f}
⏱️ 持仓时长: {datetime.now() - position['entry_time']}
"""
        self._send_telegram(message)
        
        # 移除仓位
        del self.positions[symbol]
        self.stats['active_positions'] -= 1
    
    def print_dashboard(self):
        """打印仪表板"""
        runtime = datetime.now() - self.stats['start_time']
        
        print("\n" + "="*70)
        print("📊 资金费率套利仪表板")
        print("="*70)
        print(f"⏱️ 运行时间: {runtime}")
        print(f"💰 已收资金费: ${self.stats['total_funding_collected']:.4f}")
        print(f"📈 活跃仓位: {self.stats['active_positions']}")
        print(f"📊 累计开仓: {self.stats['total_positions_opened']}")
        
        if self.positions:
            print("\n当前持仓:")
            for symbol, pos in self.positions.items():
                print(f"  {symbol}: {pos['type']} | 资金费: {pos['funding_rate']*100:.4f}% | "
                      f"已收: ${pos['funding_collected']:.4f}")
        
        print("="*70)
    
    def run(self):
        """运行资金费率套利机器人"""
        logger.info("开始监控资金费率...")
        logger.info("按 Ctrl+C 停止")
        
        check_count = 0
        
        try:
            while True:
                check_count += 1
                logger.info(f"\n🔄 第 {check_count} 次检查...")
                
                # 获取资金费率
                funding_rates = self.get_funding_rates()
                
                if funding_rates:
                    # 检查套利机会
                    opportunities = self.check_arbitrage_opportunities(funding_rates)
                    
                    # 开仓新机会
                    for opp in opportunities:
                        self.open_funding_position(opp)
                    
                    # 更新现有仓位
                    self.update_positions(funding_rates)
                
                # 定期显示仪表板
                if check_count % 6 == 0:  # 每30分钟
                    self.print_dashboard()
                
                # 等待下次检查
                time.sleep(self.config['check_interval'])
                
        except KeyboardInterrupt:
            logger.info("\n🛑 用户停止机器人")
            self.print_dashboard()
            self._send_telegram("🛑 资金费率套利机器人已停止")
        except Exception as e:
            logger.error(f"运行错误: {e}")
            self._send_telegram(f"❌ 资金费率套利机器人异常: {str(e)}")

def main():
    """主函数"""
    bot = FundingRateArbitrage()
    bot.run()

if __name__ == "__main__":
    main()