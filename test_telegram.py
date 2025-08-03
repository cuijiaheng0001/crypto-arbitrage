#!/usr/bin/env python3
"""
测试 Telegram 通知
"""

import os
import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
chat_id = os.getenv('TELEGRAM_CHAT_ID')

if bot_token and chat_id:
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    message = """
🎯 <b>测试通知</b>

📊 套利机器人监控中...
💰 当前阈值: 0.005%
🔍 监控币种: BTC, ETH, SOL, DOGE, XRP, ADA

<i>市场价差很小，说明市场效率高</i>

建议:
1. 继续监控，等待更大价差
2. 或者尝试监控其他小币种
3. 考虑在波动较大的时段运行
"""
    
    data = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML'
    }
    
    response = requests.post(url, data=data)
    
    if response.status_code == 200:
        print("✅ 测试消息发送成功！")
    else:
        print(f"❌ 发送失败: {response.text}")
else:
    print("❌ 未找到 Telegram 配置")