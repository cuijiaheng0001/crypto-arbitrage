#!/usr/bin/env python3
import os
import requests
from dotenv import load_dotenv

load_dotenv()

bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
chat_id = os.getenv('TELEGRAM_CHAT_ID')

message = """
🚀 <b>套利机器人已切换到后台运行</b>

✅ <b>运行状态</b>: 正常
📊 <b>进程 ID</b>: 108713
⏰ <b>启动时间</b>: 2025-08-03 16:33:18

📈 <b>监控币种</b>: BTC, ETH, SOL, DOGE, XRP, ADA
🎯 <b>利润阈值</b>: 0.005%

<b>管理命令：</b>
📋 查看日志: <code>tail -f logs/bot_20250803_163318.log</code>
📊 检查状态: <code>python3 check_status.py</code>
🛑 停止机器人: <code>kill 108713</code>

<i>机器人将在后台持续监控，发现机会会立即通知您！</i>
"""

url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
data = {
    'chat_id': chat_id,
    'text': message,
    'parse_mode': 'HTML'
}

response = requests.post(url, data=data)
if response.status_code == 200:
    print("✅ 后台运行通知已发送!")
else:
    print("❌ 发送失败")