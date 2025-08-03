#!/usr/bin/env python3
"""
WebSocket 实时套利机器人 v4.0
使用 WebSocket 实现超低延迟价格监控
"""

import asyncio
import websockets
import json
import time
import os
import logging
import aiohttp
from datetime import datetime
from dotenv import load_dotenv
import requests
from collections import defaultdict
import orjson  # 高性能 JSON 解析

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/websocket_arbitrage.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WebSocketArbitrageBot:
    def __init__(self):
        """初始化 WebSocket 套利机器人"""
        
        # 交易配置
        self.config = {
            'symbols': ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'DOGE/USDT', 'XRP/USDT'],
            'min_profit_percentage': 0.005,
            'max_trade_amount': 50.0,
            'slippage_tolerance': 0.02,
            'fees': {
                'bitget': {'maker': 0.001, 'taker': 0.001},
                'bybit': {'maker': 0.001, 'taker': 0.001}
            }
        }
        
        # WebSocket URLs
        self.ws_urls = {
            'bitget': 'wss://ws.bitget.com/spot/v1/stream',
            'bybit': 'wss://stream.bybit.com/v5/public/spot'
        }
        
        # 价格数据存储
        self.orderbooks = defaultdict(lambda: defaultdict(dict))
        self.last_update = defaultdict(lambda: defaultdict(float))
        
        # 统计信息
        self.stats = {
            'ws_messages_received': 0,
            'opportunities_found': 0,
            'trades_executed': 0,
            'start_time': datetime.now(),
            'latency': defaultdict(list)
        }
        
        # Telegram 通知
        self.telegram_enabled = os.getenv('TELEGRAM_ENABLED', 'false').lower() == 'true'
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID', '')
        
        logger.info("🚀 WebSocket 套利机器人启动")
        self._send_telegram("🚀 WebSocket 套利机器人已启动\n\n⚡ 实时数据流监控中...")
    
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
    
    async def connect_bitget_ws(self):
        """连接 Bitget WebSocket"""
        try:
            async with websockets.connect(self.ws_urls['bitget']) as ws:
                logger.info("✅ Bitget WebSocket 已连接")
                
                # 订阅所需的交易对
                subscribe_msg = {
                    "op": "subscribe",
                    "args": []
                }
                
                for symbol in self.config['symbols']:
                    base, quote = symbol.split('/')
                    bitget_symbol = f"{base}{quote}"
                    subscribe_msg["args"].append({
                        "instType": "sp",
                        "channel": "books5",
                        "instId": bitget_symbol
                    })
                
                await ws.send(json.dumps(subscribe_msg))
                
                # 接收数据
                while True:
                    try:
                        message = await asyncio.wait_for(ws.recv(), timeout=30)
                        await self.process_bitget_message(orjson.loads(message))
                    except asyncio.TimeoutError:
                        # 发送 ping 保持连接
                        await ws.send('ping')
                    except Exception as e:
                        logger.error(f"Bitget 消息处理错误: {e}")
                        
        except Exception as e:
            logger.error(f"Bitget WebSocket 连接错误: {e}")
            await asyncio.sleep(5)  # 重连延迟
            asyncio.create_task(self.connect_bitget_ws())  # 重新连接
    
    async def connect_bybit_ws(self):
        """连接 Bybit WebSocket"""
        try:
            async with websockets.connect(self.ws_urls['bybit']) as ws:
                logger.info("✅ Bybit WebSocket 已连接")
                
                # 订阅所需的交易对
                for symbol in self.config['symbols']:
                    base, quote = symbol.split('/')
                    bybit_symbol = f"{base}{quote}"
                    
                    subscribe_msg = {
                        "op": "subscribe",
                        "args": [f"orderbook.50.{bybit_symbol}"]
                    }
                    
                    await ws.send(json.dumps(subscribe_msg))
                
                # 接收数据
                while True:
                    try:
                        message = await asyncio.wait_for(ws.recv(), timeout=30)
                        await self.process_bybit_message(orjson.loads(message))
                    except asyncio.TimeoutError:
                        # 发送 ping 保持连接
                        await ws.send('{"op": "ping"}')
                    except Exception as e:
                        logger.error(f"Bybit 消息处理错误: {e}")
                        
        except Exception as e:
            logger.error(f"Bybit WebSocket 连接错误: {e}")
            await asyncio.sleep(5)
            asyncio.create_task(self.connect_bybit_ws())
    
    async def process_bitget_message(self, data):
        """处理 Bitget WebSocket 消息"""
        if data.get('action') == 'snapshot' or data.get('action') == 'update':
            if 'data' in data:
                for item in data['data']:
                    symbol = item['instId']
                    # 转换为标准格式
                    if 'USDT' in symbol:
                        base = symbol.replace('USDT', '')
                        std_symbol = f"{base}/USDT"
                        
                        # 更新订单簿
                        self.orderbooks['bitget'][std_symbol] = {
                            'bids': [[float(bid[0]), float(bid[1])] for bid in item.get('bids', [])[:5]],
                            'asks': [[float(ask[0]), float(ask[1])] for ask in item.get('asks', [])[:5]],
                            'timestamp': time.time()
                        }
                        
                        self.last_update['bitget'][std_symbol] = time.time()
                        self.stats['ws_messages_received'] += 1
                        
                        # 检查套利机会
                        await self.check_arbitrage_opportunity(std_symbol)
    
    async def process_bybit_message(self, data):
        """处理 Bybit WebSocket 消息"""
        if data.get('topic') and data.get('topic').startswith('orderbook'):
            if 'data' in data:
                symbol_raw = data['topic'].split('.')[-1]
                # 转换为标准格式
                if 'USDT' in symbol_raw:
                    base = symbol_raw.replace('USDT', '')
                    std_symbol = f"{base}/USDT"
                    
                    # 更新订单簿
                    orderbook_data = data['data']
                    self.orderbooks['bybit'][std_symbol] = {
                        'bids': [[float(bid[0]), float(bid[1])] for bid in orderbook_data.get('b', [])[:5]],
                        'asks': [[float(ask[0]), float(ask[1])] for ask in orderbook_data.get('a', [])[:5]],
                        'timestamp': time.time()
                    }
                    
                    self.last_update['bybit'][std_symbol] = time.time()
                    self.stats['ws_messages_received'] += 1
                    
                    # 检查套利机会
                    await self.check_arbitrage_opportunity(std_symbol)
    
    async def check_arbitrage_opportunity(self, symbol):
        """检查套利机会（超快速版本）"""
        
        # 确保两个交易所都有数据
        if symbol not in self.orderbooks['bitget'] or symbol not in self.orderbooks['bybit']:
            return
        
        # 检查数据新鲜度（1秒内）
        current_time = time.time()
        if (current_time - self.orderbooks['bitget'][symbol]['timestamp'] > 1 or 
            current_time - self.orderbooks['bybit'][symbol]['timestamp'] > 1):
            return
        
        bitget_book = self.orderbooks['bitget'][symbol]
        bybit_book = self.orderbooks['bybit'][symbol]
        
        if not bitget_book['bids'] or not bitget_book['asks'] or not bybit_book['bids'] or not bybit_book['asks']:
            return
        
        # 计算套利机会
        opportunities = []
        
        # 场景1: Bitget买入 -> Bybit卖出
        bitget_ask = bitget_book['asks'][0][0]  # Bitget 卖价
        bybit_bid = bybit_book['bids'][0][0]    # Bybit 买价
        
        profit_percentage = ((bybit_bid - bitget_ask) / bitget_ask - 
                           self.config['fees']['bitget']['taker'] - 
                           self.config['fees']['bybit']['taker']) * 100
        
        if profit_percentage > self.config['min_profit_percentage']:
            opportunities.append({
                'direction': 'Bitget → Bybit',
                'buy_price': bitget_ask,
                'sell_price': bybit_bid,
                'profit_percentage': profit_percentage,
                'symbol': symbol
            })
        
        # 场景2: Bybit买入 -> Bitget卖出
        bybit_ask = bybit_book['asks'][0][0]    # Bybit 卖价
        bitget_bid = bitget_book['bids'][0][0]  # Bitget 买价
        
        profit_percentage = ((bitget_bid - bybit_ask) / bybit_ask - 
                           self.config['fees']['bybit']['taker'] - 
                           self.config['fees']['bitget']['taker']) * 100
        
        if profit_percentage > self.config['min_profit_percentage']:
            opportunities.append({
                'direction': 'Bybit → Bitget',
                'buy_price': bybit_ask,
                'sell_price': bitget_bid,
                'profit_percentage': profit_percentage,
                'symbol': symbol
            })
        
        # 发现机会时的处理
        for opp in opportunities:
            self.stats['opportunities_found'] += 1
            
            logger.info(f"🎯 发现套利机会! {symbol} {opp['direction']} "
                       f"利润率: {opp['profit_percentage']:.3f}%")
            
            # 发送通知
            if self.stats['opportunities_found'] % 10 == 1:  # 每10个机会通知一次
                message = f"""
⚡ <b>WebSocket 实时套利机会!</b>

💎 <b>币种</b>: {symbol}
📊 <b>方向</b>: {opp['direction']}
💰 <b>利润率</b>: {opp['profit_percentage']:.3f}%
📈 <b>买入</b>: ${opp['buy_price']:.2f}
📉 <b>卖出</b>: ${opp['sell_price']:.2f}

⏱️ <b>延迟</b>: <0.1秒
🎯 <b>累计发现</b>: {self.stats['opportunities_found']}个机会
"""
                self._send_telegram(message)
    
    async def print_statistics(self):
        """定期打印统计信息"""
        while True:
            await asyncio.sleep(60)  # 每分钟打印一次
            
            runtime = datetime.now() - self.stats['start_time']
            
            logger.info("="*50)
            logger.info(f"⚡ WebSocket 实时监控统计")
            logger.info(f"⏱️ 运行时间: {runtime}")
            logger.info(f"📨 接收消息: {self.stats['ws_messages_received']}")
            logger.info(f"🎯 发现机会: {self.stats['opportunities_found']}")
            logger.info(f"📊 消息速率: {self.stats['ws_messages_received'] / runtime.total_seconds():.1f}/秒")
            logger.info("="*50)
    
    async def run(self):
        """运行 WebSocket 套利机器人"""
        logger.info("🎯 启动 WebSocket 连接...")
        
        # 创建并发任务
        tasks = [
            asyncio.create_task(self.connect_bitget_ws()),
            asyncio.create_task(self.connect_bybit_ws()),
            asyncio.create_task(self.print_statistics())
        ]
        
        # 等待所有任务
        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            logger.info("🛑 用户停止机器人")
            self._send_telegram("🛑 WebSocket 套利机器人已停止")
        except Exception as e:
            logger.error(f"❌ 运行错误: {e}")
            self._send_telegram(f"❌ WebSocket 机器人异常: {str(e)}")

async def main():
    """主函数"""
    
    # 安装必要的包
    try:
        import orjson
    except ImportError:
        logger.info("📦 安装 orjson...")
        os.system("pip install orjson")
        import orjson
    
    try:
        import aiohttp
    except ImportError:
        logger.info("📦 安装 aiohttp...")
        os.system("pip install aiohttp")
        import aiohttp
    
    # 创建日志目录
    os.makedirs('logs', exist_ok=True)
    
    # 启动机器人
    bot = WebSocketArbitrageBot()
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())