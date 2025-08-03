#!/usr/bin/env python3
"""直接测试 API 调用"""

import os
import time
import requests
import hmac
import hashlib
from urllib.parse import urlencode
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_binance_raw():
    """直接测试 Binance API"""
    print("测试 Binance 原始 API 调用...")
    
    api_key = os.getenv('BINANCE_API_KEY')
    secret_key = os.getenv('BINANCE_SECRET_KEY')
    
    if not api_key or not secret_key:
        print("❌ 未找到 Binance API 密钥")
        return
    
    # 测试公共端点
    print("\n1. 测试公共端点...")
    try:
        response = requests.get('https://testnet.binance.vision/api/v3/ping')
        print(f"   Ping 响应: {response.status_code} - {response.text}")
        
        response = requests.get('https://testnet.binance.vision/api/v3/ticker/price?symbol=BTCUSDT')
        print(f"   价格响应: {response.status_code} - {response.text[:100]}")
    except Exception as e:
        print(f"   错误: {e}")
    
    # 测试需要签名的端点
    print("\n2. 测试账户端点（需要签名）...")
    try:
        timestamp = int(time.time() * 1000)
        params = {
            'timestamp': timestamp,
            'recvWindow': 5000
        }
        
        # 创建签名
        query_string = urlencode(params)
        signature = hmac.new(
            secret_key.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        params['signature'] = signature
        
        headers = {
            'X-MBX-APIKEY': api_key
        }
        
        # 发送请求
        response = requests.get(
            'https://testnet.binance.vision/api/v3/account',
            params=params,
            headers=headers
        )
        
        print(f"   账户响应: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ API 密钥有效!")
            data = response.json()
            print(f"   可以交易: {data.get('canTrade', False)}")
        else:
            print(f"   ❌ 错误: {response.text}")
            
    except Exception as e:
        print(f"   错误: {e}")

def test_api_key_format():
    """检查 API 密钥格式"""
    print("\n检查 API 密钥格式...")
    
    api_key = os.getenv('BINANCE_API_KEY')
    secret_key = os.getenv('BINANCE_SECRET_KEY')
    
    print(f"API Key 长度: {len(api_key) if api_key else 'None'}")
    print(f"Secret Key 长度: {len(secret_key) if secret_key else 'None'}")
    
    if api_key:
        print(f"API Key 前4位: {api_key[:4]}...")
        print(f"API Key 后4位: ...{api_key[-4:]}")
        
    if secret_key:
        print(f"Secret Key 前4位: {secret_key[:4]}...")
        print(f"Secret Key 后4位: ...{secret_key[-4:]}")

if __name__ == "__main__":
    test_api_key_format()
    print("\n" + "="*50)
    test_binance_raw()
    
    print("\n" + "="*50)
    print("注意事项：")
    print("1. 确保 API 密钥是从 Binance Spot Test Network 生成的")
    print("2. 确保已勾选 TRADE 和 USER_DATA 权限")
    print("3. API 密钥应该是64个字符")
    print("4. Secret Key 也应该是64个字符")