#!/usr/bin/env python3
"""
Bitget 价格监控器
使用 REST API 监控价格变化
"""

import ccxt
import time
import os
import logging
from datetime import datetime
from dotenv import load_dotenv
import requests

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BitgetPriceMonitor:
    def __init__(self):
        """初始化价格监控器"""
        
        # 初始化 Bitget
        self.exchange = ccxt.bitget({
            'apiKey': os.getenv('BITGET_API_KEY'),
            'secret': os.getenv('BITGET_API_SECRET'),
            'password': os.getenv('BITGET_PASSPHRASE'),
            'enableRateLimit': True,
            'timeout': 30000
        })
        
        # 监控的交易对
        self.symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'DOGE/USDT', 'XRP/USDT']
        
        # 价格历史
        self.price_history = {symbol: [] for symbol in self.symbols}
        self.max_history = 100  # 保留最近100个价格
        
        # Telegram 通知
        self.telegram_enabled = os.getenv('TELEGRAM_ENABLED', 'false').lower() == 'true'
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID', '')
        
        # 价格变化阈值
        self.alert_threshold = 0.5  # 0.5% 价格变化触发通知
        
        logger.info("🚀 Bitget 价格监控器启动")
        self._send_telegram("🚀 Bitget 价格监控器已启动\n\n监控币种: " + ", ".join(self.symbols))
    
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
    
    def fetch_prices(self):
        """获取当前价格"""
        prices = {}
        
        try:
            # 批量获取所有ticker
            tickers = self.exchange.fetch_tickers(self.symbols)
            
            for symbol in self.symbols:
                if symbol in tickers:
                    ticker = tickers[symbol]
                    prices[symbol] = {
                        'bid': ticker['bid'],
                        'ask': ticker['ask'],
                        'last': ticker['last'],
                        'volume': ticker['volume'],
                        'percentage': ticker['percentage'],
                        'timestamp': datetime.now()
                    }
                    
                    # 添加到历史记录
                    self.price_history[symbol].append(prices[symbol])
                    if len(self.price_history[symbol]) > self.max_history:
                        self.price_history[symbol].pop(0)
            
            return prices
            
        except Exception as e:
            logger.error(f"获取价格失败: {e}")
            return None
    
    def analyze_price_changes(self, current_prices):
        """分析价格变化"""
        alerts = []
        
        for symbol, price_data in current_prices.items():
            history = self.price_history[symbol]
            
            if len(history) >= 2:
                # 计算价格变化
                prev_price = history[-2]['last']
                curr_price = price_data['last']
                
                if prev_price and curr_price:
                    change_percent = ((curr_price - prev_price) / prev_price) * 100
                    
                    # 检查是否超过阈值
                    if abs(change_percent) >= self.alert_threshold:
                        alerts.append({
                            'symbol': symbol,
                            'prev_price': prev_price,
                            'curr_price': curr_price,
                            'change_percent': change_percent,
                            'volume': price_data['volume']
                        })
                        
                        # 发送通知
                        emoji = "📈" if change_percent > 0 else "📉"
                        message = f"""
{emoji} <b>价格异动提醒</b>

💎 币种: {symbol}
💰 价格: ${curr_price:.2f}
📊 变化: {change_percent:+.2f}%
📊 成交量: {price_data['volume']:.2f}
"""
                        self._send_telegram(message)
        
        return alerts
    
    def calculate_spread(self, price_data):
        """计算买卖价差"""
        if price_data['bid'] and price_data['ask']:
            spread = price_data['ask'] - price_data['bid']
            spread_percent = (spread / price_data['ask']) * 100
            return spread_percent
        return None
    
    def print_dashboard(self, prices):
        """打印价格仪表板"""
        print("\n" + "="*70)
        print(f"📊 Bitget 价格监控 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        print(f"{'币种':<10} {'买价':<10} {'卖价':<10} {'最新价':<10} {'价差%':<8} {'24h涨幅':<10}")
        print("-"*70)
        
        for symbol, data in prices.items():
            spread = self.calculate_spread(data)
            print(f"{symbol:<10} "
                  f"${data['bid']:<9.2f} "
                  f"${data['ask']:<9.2f} "
                  f"${data['last']:<9.2f} "
                  f"{spread:<7.3f}% "
                  f"{data['percentage']:+9.2f}%")
        
        print("="*70)
    
    def check_arbitrage_opportunities(self, prices):
        """检查潜在的套利机会（同一交易所内）"""
        # 这里可以添加三角套利检测逻辑
        pass
    
    def run(self):
        """运行监控器"""
        logger.info("开始监控价格...")
        logger.info("按 Ctrl+C 停止")
        
        try:
            while True:
                # 获取价格
                prices = self.fetch_prices()
                
                if prices:
                    # 分析价格变化
                    alerts = self.analyze_price_changes(prices)
                    
                    # 打印仪表板
                    self.print_dashboard(prices)
                    
                    # 检查套利机会
                    self.check_arbitrage_opportunities(prices)
                
                # 等待下次更新
                time.sleep(5)
                
        except KeyboardInterrupt:
            logger.info("\n🛑 用户停止监控")
            self._send_telegram("🛑 价格监控已停止")
        except Exception as e:
            logger.error(f"运行错误: {e}")
            self._send_telegram(f"❌ 监控异常: {str(e)}")

def main():
    """主函数"""
    monitor = BitgetPriceMonitor()
    monitor.run()

if __name__ == "__main__":
    main()