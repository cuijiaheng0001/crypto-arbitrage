#!/usr/bin/env python3
"""测试 Bybit Demo Trading API"""

import os
import ccxt
import time
import hmac
import hashlib
import requests
import json
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_bybit_demo_ccxt():
    """使用 ccxt 测试 Bybit Demo"""
    print("="*50)
    print("测试 Bybit Demo Trading (ccxt)")
    print("="*50)
    
    try:
        # 配置 Bybit Demo
        exchange = ccxt.bybit({
            'apiKey': os.getenv('BYBIT_API_KEY'),
            'secret': os.getenv('BYBIT_SECRET_KEY'),
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot',
                'recvWindow': 10000,
            },
            'urls': {
                'api': {
                    'public': 'https://api-demo.bybit.com',
                    'private': 'https://api-demo.bybit.com',
                }
            },
            'hostname': 'api-demo.bybit.com'
        })
        
        # 1. 测试公共端点
        print("\n1. 测试公共端点...")
        server_time = exchange.fetch_time()
        print(f"   ✅ 服务器时间: {server_time}")
        
        # 2. 测试价格
        print("\n2. 获取 BTC/USDT 价格...")
        ticker = exchange.fetch_ticker('BTC/USDT')
        print(f"   ✅ BTC 价格: ${ticker['last']:,.2f}")
        
        # 3. 测试私有端点 - 获取余额
        print("\n3. 测试账户余额...")
        try:
            balance = exchange.fetch_balance()
            print("   ✅ Demo 账户余额:")
            for currency, bal in balance['total'].items():
                if bal > 0:
                    print(f"      {currency}: {bal:.4f}")
        except Exception as e:
            print(f"   ❌ 获取余额失败: {e}")
            
    except Exception as e:
        print(f"❌ 错误: {e}")

def test_bybit_demo_raw():
    """使用原始 API 测试 Bybit Demo"""
    print("\n" + "="*50)
    print("测试 Bybit Demo Trading (原始 API)")
    print("="*50)
    
    api_key = os.getenv('BYBIT_API_KEY')
    api_secret = os.getenv('BYBIT_SECRET_KEY')
    
    if not api_key or not api_secret:
        print("❌ 未找到 Bybit API 密钥")
        return
    
    base_url = 'https://api-demo.bybit.com'
    
    # 1. 测试公共端点
    print("\n1. 测试服务器时间...")
    try:
        response = requests.get(f'{base_url}/v5/market/time')
        data = response.json()
        if data['retCode'] == 0:
            server_time = data['result']['timeSecond']
            print(f"   ✅ 服务器时间: {server_time}")
        else:
            print(f"   ❌ 错误: {data}")
    except Exception as e:
        print(f"   ❌ 连接错误: {e}")
    
    # 2. 测试私有端点
    print("\n2. 测试账户信息...")
    try:
        # 准备签名
        timestamp = str(int(time.time() * 1000))
        recv_window = '5000'
        
        # 对于 GET 请求，参数在 query string 中
        params = f"accountType=UNIFIED&timestamp={timestamp}&recvWindow={recv_window}"
        
        # 签名字符串：timestamp + api_key + recv_window + query_string
        sign_str = timestamp + api_key + recv_window + params
        signature = hmac.new(
            api_secret.encode('utf-8'),
            sign_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        # 构建请求
        headers = {
            'X-BAPI-KEY': api_key,
            'X-BAPI-SIGN': signature,
            'X-BAPI-TIMESTAMP': timestamp,
            'X-BAPI-RECV-WINDOW': recv_window
        }
        
        url = f"{base_url}/v5/account/wallet-balance?{params}"
        response = requests.get(url, headers=headers)
        data = response.json()
        
        if data['retCode'] == 0:
            print("   ✅ API 密钥验证成功!")
            if 'result' in data and 'list' in data['result']:
                for account in data['result']['list']:
                    print(f"   账户类型: {account['accountType']}")
                    print(f"   总权益: ${float(account.get('totalEquity', 0)):,.2f}")
        else:
            print(f"   ❌ 错误: {data}")
            
    except Exception as e:
        print(f"   ❌ 错误: {e}")

def check_bybit_demo_requirements():
    """检查 Bybit Demo 配置要求"""
    print("\n" + "="*50)
    print("Bybit Demo Trading 配置检查")
    print("="*50)
    
    print("\n✅ 正确的配置要求：")
    print("1. API 域名: https://api-demo.bybit.com")
    print("2. 需要先在网页登录 Bybit Demo Trading 激活账户")
    print("3. API Key 需要开启 'Unified Trading' 权限")
    print("4. 最小下单量: BTC/USDT = 0.001 BTC")
    print("5. 签名算法: HMAC-SHA256")
    print("6. 时间戳容差: 30秒")
    
    api_key = os.getenv('BYBIT_API_KEY')
    if api_key:
        print(f"\n当前 API Key 前4位: {api_key[:4]}...")
        print(f"当前 API Key 后4位: ...{api_key[-4:]}")

if __name__ == "__main__":
    # 运行测试
    test_bybit_demo_ccxt()
    test_bybit_demo_raw()
    check_bybit_demo_requirements()
    
    print("\n" + "="*50)
    print("提示：")
    print("1. 如果看到 'Invalid ApiKey'，请确认使用的是 Demo Trading 的 API")
    print("2. 访问 https://demo.bybit.com 创建 Demo 账户")
    print("3. 在 API Management 中创建新的 Demo API Key")