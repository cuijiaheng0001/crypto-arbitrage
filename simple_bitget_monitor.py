#!/usr/bin/env python3
"""
简单的 Bitget 价格监控器
"""

import ccxt
import time
import os
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 初始化 Bitget
exchange = ccxt.bitget({
    'apiKey': os.getenv('BITGET_API_KEY'),
    'secret': os.getenv('BITGET_API_SECRET'),  
    'password': os.getenv('BITGET_PASSPHRASE'),
    'enableRateLimit': True
})

symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT']

print("🚀 开始监控 Bitget 价格...")
print("按 Ctrl+C 停止\n")

try:
    while True:
        print(f"\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 50)
        
        for symbol in symbols:
            try:
                ticker = exchange.fetch_ticker(symbol)
                print(f"{symbol}: ${ticker['last']:.2f} "
                      f"(买: ${ticker['bid']:.2f}, 卖: ${ticker['ask']:.2f})")
            except Exception as e:
                print(f"{symbol}: 获取失败 - {str(e)[:50]}")
        
        time.sleep(5)
        
except KeyboardInterrupt:
    print("\n✅ 监控已停止")