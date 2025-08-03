#!/usr/bin/env python3
"""
Telegram Bot 配置助手
帮助您设置 Telegram 通知功能
"""

import os
import sys
import time
from dotenv import load_dotenv, set_key

# 加载环境变量
load_dotenv()

def print_guide():
    """打印配置指南"""
    print("📱 Telegram Bot 配置指南")
    print("="*60)
    print()
    print("🔧 获取 Telegram Bot Token 步骤：")
    print("1. 在 Telegram 中搜索 @BotFather")
    print("2. 发送 /newbot 创建新机器人")
    print("3. 给机器人起个名字（如：My Arbitrage Bot）")
    print("4. 给机器人设置用户名（如：myarbitragebot，必须以bot结尾）")
    print("5. BotFather 会返回一个 Token，格式如：")
    print("   1234567890:ABCdefGHIjklMNOpqrsTUVwxyz")
    print()
    print("🔍 获取 Chat ID 步骤：")
    print("1. 向您的机器人发送任意消息")
    print("2. 访问：https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates")
    print("3. 在返回的 JSON 中找到 'chat' -> 'id' 字段")
    print("4. 或者使用 @userinfobot 机器人获取您的 Chat ID")
    print()
    print("="*60)

def validate_token(token):
    """验证 Token 格式"""
    if not token:
        return False
    parts = token.split(':')
    if len(parts) != 2:
        return False
    if not parts[0].isdigit():
        return False
    if len(parts[1]) < 20:
        return False
    return True

def validate_chat_id(chat_id):
    """验证 Chat ID"""
    try:
        int(chat_id)
        return True
    except:
        return False

def test_telegram_connection(token, chat_id):
    """测试 Telegram 连接"""
    try:
        import requests
        
        print("\n🔍 测试 Telegram 连接...")
        
        # 测试 Bot 信息
        url = f"https://api.telegram.org/bot{token}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                bot_info = data.get('result', {})
                print(f"✅ Bot 连接成功!")
                print(f"🤖 Bot 名称: {bot_info.get('first_name', 'Unknown')}")
                print(f"📱 Bot 用户名: @{bot_info.get('username', 'Unknown')}")
                
                # 发送测试消息
                print("\n📤 发送测试消息...")
                message = "🎉 Telegram 通知配置成功！\n\n🚀 您的套利机器人现在可以发送通知了。"
                
                send_url = f"https://api.telegram.org/bot{token}/sendMessage"
                send_data = {
                    'chat_id': chat_id,
                    'text': message,
                    'parse_mode': 'HTML'
                }
                
                send_response = requests.post(send_url, data=send_data, timeout=10)
                
                if send_response.status_code == 200 and send_response.json().get('ok'):
                    print("✅ 测试消息发送成功！")
                    print("📱 请检查您的 Telegram")
                    return True
                else:
                    error = send_response.json().get('description', 'Unknown error')
                    print(f"❌ 消息发送失败: {error}")
                    if 'chat not found' in error.lower():
                        print("💡 提示：请先向您的 Bot 发送一条消息")
                    return False
            else:
                print(f"❌ Bot Token 无效: {data.get('description', 'Unknown error')}")
                return False
        else:
            print(f"❌ 连接失败: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False

def configure_telegram():
    """配置 Telegram"""
    print_guide()
    
    # 获取当前配置
    current_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
    current_chat_id = os.getenv('TELEGRAM_CHAT_ID', '')
    
    if current_token and current_chat_id:
        print(f"\n📋 当前配置：")
        print(f"Token: ***{current_token[-10:]}")
        print(f"Chat ID: {current_chat_id}")
        
        choice = input("\n是否要重新配置？(y/n): ").lower().strip()
        if choice not in ['y', 'yes', '是']:
            print("配置未更改。")
            return
    
    print("\n请输入您的 Telegram 配置信息：")
    
    # 获取 Bot Token
    while True:
        bot_token = input("Bot Token: ").strip()
        if validate_token(bot_token):
            break
        else:
            print("❌ Token 格式不正确，请重新输入")
            print("正确格式: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz")
    
    # 获取 Chat ID
    while True:
        chat_id = input("Chat ID: ").strip()
        if validate_chat_id(chat_id):
            break
        else:
            print("❌ Chat ID 格式不正确，应该是一个数字")
    
    # 测试连接
    if test_telegram_connection(bot_token, chat_id):
        # 保存配置
        env_file = '/root/crypto-arbitrage/.env'
        
        print("\n💾 保存配置...")
        set_key(env_file, 'TELEGRAM_BOT_TOKEN', bot_token)
        set_key(env_file, 'TELEGRAM_CHAT_ID', chat_id)
        set_key(env_file, 'TELEGRAM_ENABLED', 'true')
        
        print("✅ Telegram 配置已保存！")
        print("\n🎯 下一步：")
        print("1. 重启套利机器人")
        print("2. 机器人将自动发送通知")
        print("   - 发现套利机会时")
        print("   - 执行交易时")
        print("   - 达到盈利目标时")
        
    else:
        print("\n❌ 配置失败，请检查您的 Token 和 Chat ID")
        print("💡 常见问题：")
        print("1. 确保已向 Bot 发送过消息")
        print("2. 检查 Token 是否完整复制")
        print("3. 确认 Chat ID 是否正确")

def main():
    """主函数"""
    try:
        # 检查是否安装了 requests
        try:
            import requests
        except ImportError:
            print("📦 安装必要的依赖...")
            os.system("pip install requests python-dotenv")
            import requests
        
        configure_telegram()
        
    except KeyboardInterrupt:
        print("\n\n👋 配置已取消")
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")

if __name__ == "__main__":
    main()