#!/usr/bin/env python3
"""
Bitget API 配置助手
安全地设置您的 Bitget API 密钥
"""

import os
import getpass

def setup_bitget_api():
    print("🔐 Bitget API 配置助手")
    print("=" * 40)
    print()
    
    print("请输入您的 Bitget API 信息：")
    print("(输入时密钥不会显示，这是正常的安全措施)")
    print()
    
    # 获取 API 信息
    api_key = getpass.getpass("API Key: ").strip()
    api_secret = getpass.getpass("Secret Key: ").strip()
    passphrase = getpass.getpass("Passphrase: ").strip()
    
    if not all([api_key, api_secret, passphrase]):
        print("❌ 错误：所有字段都必须填写")
        return False
    
    # 读取现有的 .env 文件
    env_file = "/root/crypto-arbitrage/.env"
    
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print("❌ 错误：找不到 .env 文件")
        return False
    
    # 更新 Bitget 配置
    updated_lines = []
    for line in lines:
        if line.startswith('BITGET_API_KEY='):
            updated_lines.append(f'BITGET_API_KEY={api_key}\n')
        elif line.startswith('BITGET_API_SECRET='):
            updated_lines.append(f'BITGET_API_SECRET={api_secret}\n')
        elif line.startswith('BITGET_PASSPHRASE='):
            updated_lines.append(f'BITGET_PASSPHRASE={passphrase}\n')
        else:
            updated_lines.append(line)
    
    # 写回文件
    try:
        with open(env_file, 'w', encoding='utf-8') as f:
            f.writelines(updated_lines)
        
        print("\n✅ Bitget API 配置成功！")
        print()
        print("🔧 下一步：")
        print("1. 运行测试：python3 test_bitget_api.py")
        print("2. 开始套利测试")
        
        return True
    
    except Exception as e:
        print(f"❌ 错误：无法写入配置文件 - {str(e)}")
        return False

def show_current_config():
    """显示当前配置状态（隐藏敏感信息）"""
    env_file = "/root/crypto-arbitrage/.env"
    
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("📋 当前 Bitget 配置状态：")
        print("-" * 30)
        
        if 'BITGET_API_KEY=' in content:
            key_line = [line for line in content.split('\n') if line.startswith('BITGET_API_KEY=')][0]
            key_value = key_line.split('=', 1)[1]
            if key_value.strip():
                print(f"✅ API Key: ***{key_value[-4:]}")
            else:
                print("❌ API Key: 未设置")
        
        if 'BITGET_API_SECRET=' in content:
            secret_line = [line for line in content.split('\n') if line.startswith('BITGET_API_SECRET=')][0]
            secret_value = secret_line.split('=', 1)[1]
            if secret_value.strip():
                print(f"✅ Secret Key: ***{secret_value[-4:]}")
            else:
                print("❌ Secret Key: 未设置")
        
        if 'BITGET_PASSPHRASE=' in content:
            pass_line = [line for line in content.split('\n') if line.startswith('BITGET_PASSPHRASE=')][0]
            pass_value = pass_line.split('=', 1)[1]
            if pass_value.strip():
                print("✅ Passphrase: 已设置")
            else:
                print("❌ Passphrase: 未设置")
        
        print()
        
    except FileNotFoundError:
        print("❌ 错误：找不到 .env 文件")

if __name__ == "__main__":
    print("🚀 Bitget API 配置工具")
    print("=" * 50)
    print()
    
    # 显示当前配置
    show_current_config()
    
    choice = input("是否要重新配置 Bitget API？(y/n): ").lower().strip()
    
    if choice in ['y', 'yes', '是']:
        setup_bitget_api()
    else:
        print("配置未更改。")
        print("\n💡 如需配置，运行：python3 setup_bitget_api.py")