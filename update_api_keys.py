#!/usr/bin/env python3
"""
安全更新 API 密钥脚本
支持单独输入各个交易所的 API 密钥
"""

import os
import sys
from getpass import getpass

def update_env_file():
    """更新 .env 文件"""
    print("="*60)
    print("API 密钥更新工具")
    print("="*60)
    print("\n提示：")
    print("- 输入时密钥不会显示在屏幕上")
    print("- 直接按回车跳过不需要更新的项目")
    print("- 输入 'clear' 清除该项的密钥")
    print("\n")
    
    # 读取现有的 .env 文件
    env_vars = {}
    env_file_path = '/root/crypto-arbitrage/.env'
    
    if os.path.exists(env_file_path):
        with open(env_file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value
    
    # 更新 Binance 密钥
    print("1. Binance 配置")
    print("-" * 40)
    
    binance_api = getpass("Binance API Key (按回车跳过): ")
    if binance_api:
        if binance_api.lower() == 'clear':
            env_vars.pop('BINANCE_API_KEY', None)
            print("   ✓ 已清除 Binance API Key")
        else:
            env_vars['BINANCE_API_KEY'] = binance_api
            print("   ✓ 已更新 Binance API Key")
    
    binance_secret = getpass("Binance Secret Key (按回车跳过): ")
    if binance_secret:
        if binance_secret.lower() == 'clear':
            env_vars.pop('BINANCE_SECRET_KEY', None)
            print("   ✓ 已清除 Binance Secret Key")
        else:
            env_vars['BINANCE_SECRET_KEY'] = binance_secret
            print("   ✓ 已更新 Binance Secret Key")
    
    binance_testnet = input("使用 Binance 测试网? (true/false，按回车保持不变): ").strip()
    if binance_testnet:
        env_vars['BINANCE_TESTNET'] = binance_testnet
        print(f"   ✓ Binance 测试网设置为: {binance_testnet}")
    
    # 更新 Bybit 密钥
    print("\n2. Bybit 配置")
    print("-" * 40)
    
    bybit_api = getpass("Bybit API Key (按回车跳过): ")
    if bybit_api:
        if bybit_api.lower() == 'clear':
            env_vars.pop('BYBIT_API_KEY', None)
            print("   ✓ 已清除 Bybit API Key")
        else:
            env_vars['BYBIT_API_KEY'] = bybit_api
            print("   ✓ 已更新 Bybit API Key")
    
    bybit_secret = getpass("Bybit Secret Key (按回车跳过): ")
    if bybit_secret:
        if bybit_secret.lower() == 'clear':
            env_vars.pop('BYBIT_SECRET_KEY', None)
            print("   ✓ 已清除 Bybit Secret Key")
        else:
            env_vars['BYBIT_SECRET_KEY'] = bybit_secret
            print("   ✓ 已更新 Bybit Secret Key")
    
    bybit_testnet = input("使用 Bybit 测试网/Demo? (true/false，按回车保持不变): ").strip()
    if bybit_testnet:
        env_vars['BYBIT_TESTNET'] = bybit_testnet
        print(f"   ✓ Bybit 测试网设置为: {bybit_testnet}")
    
    # 保存到 .env 文件
    print("\n3. 保存配置")
    print("-" * 40)
    
    # 创建备份
    if os.path.exists(env_file_path):
        backup_path = env_file_path + '.backup'
        os.rename(env_file_path, backup_path)
        print(f"   ✓ 已备份原文件到: {backup_path}")
    
    # 写入新的 .env 文件
    with open(env_file_path, 'w') as f:
        # 写入头部注释
        f.write("# 交易所API配置\n")
        
        # Binance 配置
        f.write("# Binance\n")
        f.write(f"BINANCE_API_KEY={env_vars.get('BINANCE_API_KEY', '')}\n")
        f.write(f"BINANCE_SECRET_KEY={env_vars.get('BINANCE_SECRET_KEY', '')}\n")
        f.write(f"BINANCE_TESTNET={env_vars.get('BINANCE_TESTNET', 'true')}\n")
        f.write("\n")
        
        # Bybit 配置
        f.write("# Bybit\n")
        f.write(f"BYBIT_API_KEY={env_vars.get('BYBIT_API_KEY', '')}\n")
        f.write(f"BYBIT_SECRET_KEY={env_vars.get('BYBIT_SECRET_KEY', '')}\n")
        f.write(f"BYBIT_TESTNET={env_vars.get('BYBIT_TESTNET', 'true')}\n")
        f.write("\n")
        
        # 其他配置
        f.write("# 套利参数\n")
        f.write(f"MIN_PROFIT_PERCENTAGE={env_vars.get('MIN_PROFIT_PERCENTAGE', '0.3')}\n")
        f.write(f"MAX_TRADE_AMOUNT={env_vars.get('MAX_TRADE_AMOUNT', '100')}\n")
        f.write(f"PRICE_UPDATE_INTERVAL={env_vars.get('PRICE_UPDATE_INTERVAL', '1')}\n")
        f.write("\n")
        
        f.write("# 通知配置（可选）\n")
        f.write(f"TELEGRAM_BOT_TOKEN={env_vars.get('TELEGRAM_BOT_TOKEN', '')}\n")
        f.write(f"TELEGRAM_CHAT_ID={env_vars.get('TELEGRAM_CHAT_ID', '')}\n")
        f.write("\n")
        
        f.write("# 风险控制\n")
        f.write(f"DAILY_LOSS_LIMIT={env_vars.get('DAILY_LOSS_LIMIT', '50')}\n")
        f.write(f"MAX_OPEN_ORDERS={env_vars.get('MAX_OPEN_ORDERS', '5')}\n")
    
    # 设置权限
    os.chmod(env_file_path, 0o600)
    print(f"   ✓ 已保存到: {env_file_path}")
    print("   ✓ 文件权限已设置为 600 (仅所有者可读写)")
    
    print("\n" + "="*60)
    print("✅ 配置更新完成！")
    print("\n下一步：")
    print("1. 运行测试脚本验证 API 连接:")
    print("   python3 test_api_connection.py")
    print("\n2. 如果使用 Bybit Demo，测试:")
    print("   python3 test_bybit_demo_v2.py")
    print("\n3. 重启 Docker 容器:")
    print("   docker-compose restart")

if __name__ == "__main__":
    try:
        update_env_file()
    except KeyboardInterrupt:
        print("\n\n❌ 操作已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        sys.exit(1)