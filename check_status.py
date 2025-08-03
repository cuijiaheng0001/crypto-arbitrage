#!/usr/bin/env python3
"""
快速检查套利机器人状态
"""

import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def check_bot_process():
    """检查机器人进程"""
    result = os.popen("pgrep -f telegram_arbitrage_bot.py").read()
    return bool(result.strip())

def get_latest_log():
    """获取最新日志"""
    try:
        logs = [f for f in os.listdir('logs') if f.endswith('.log')]
        if logs:
            latest = max(logs, key=lambda x: os.path.getctime(f'logs/{x}'))
            with open(f'logs/{latest}', 'r') as f:
                lines = f.readlines()
                return lines[-20:]  # 最后20行
    except:
        pass
    return []

def send_status_telegram():
    """发送状态到 Telegram"""
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not bot_token or not chat_id:
        return
    
    is_running = check_bot_process()
    status_emoji = "🟢" if is_running else "🔴"
    status_text = "运行中" if is_running else "已停止"
    
    # 分析日志获取统计
    log_lines = get_latest_log()
    opportunities = sum(1 for line in log_lines if "发现机会" in line)
    
    message = f"""
{status_emoji} <b>套利机器人状态</b>

📊 <b>运行状态</b>: {status_text}
⏰ <b>检查时间</b>: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🎯 <b>最近机会</b>: {opportunities} 个

<i>使用 ./start_bot.sh 管理机器人</i>
"""
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML'
    }
    
    requests.post(url, data=data)

def main():
    print("🔍 套利机器人状态检查")
    print("=" * 40)
    
    # 检查进程
    is_running = check_bot_process()
    if is_running:
        print("✅ 机器人状态: 运行中")
    else:
        print("❌ 机器人状态: 已停止")
    
    # 显示最新日志
    print("\n📄 最新日志:")
    print("-" * 40)
    
    log_lines = get_latest_log()
    if log_lines:
        for line in log_lines[-10:]:  # 显示最后10行
            print(line.strip())
    else:
        print("没有找到日志文件")
    
    # 发送 Telegram 通知
    if os.getenv('TELEGRAM_ENABLED', 'false').lower() == 'true':
        send_status_telegram()
        print("\n📱 状态已发送到 Telegram")

if __name__ == "__main__":
    main()