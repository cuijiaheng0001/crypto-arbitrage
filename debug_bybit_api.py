#!/usr/bin/env python3
"""调试 Bybit API 响应"""

import os
import requests
import time
import hmac
import hashlib
from dotenv import load_dotenv

load_dotenv()

def test_public_endpoint():
    """测试公共端点"""
    print("1. 测试公共端点...")
    
    # Demo Trading 端点
    urls = [
        "https://api-demo.bybit.com/v5/market/time",
        "https://api-demo.bybit.com/v5/market/tickers?category=spot&symbol=BTCUSDT",
    ]
    
    for url in urls:
        print(f"\n测试: {url}")
        try:
            response = requests.get(url)
            print(f"状态码: {response.status_code}")
            print(f"Headers: {dict(response.headers)}")
            print(f"内容: {response.text[:500]}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"JSON: {data}")
                except:
                    print("无法解析为 JSON")
                    
        except Exception as e:
            print(f"错误: {e}")

def test_private_endpoint():
    """测试私有端点"""
    print("\n\n2. 测试私有端点...")
    
    api_key = os.getenv('BYBIT_API_KEY')
    api_secret = os.getenv('BYBIT_SECRET_KEY')
    
    if not api_key:
        print("未找到 API 密钥")
        return
    
    # 准备请求
    timestamp = str(int(time.time() * 1000))
    recv_window = '5000'
    
    # 测试钱包余额端点
    endpoint = '/v5/account/wallet-balance'
    params = 'accountType=UNIFIED'
    
    # 生成签名
    sign_str = timestamp + api_key + recv_window + params
    signature = hmac.new(
        api_secret.encode('utf-8'),
        sign_str.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    headers = {
        'X-BAPI-KEY': api_key,
        'X-BAPI-SIGN': signature,
        'X-BAPI-TIMESTAMP': timestamp,
        'X-BAPI-RECV-WINDOW': recv_window
    }
    
    url = f"https://api-demo.bybit.com{endpoint}?{params}"
    
    print(f"\n测试: {url}")
    print(f"Headers: {headers}")
    
    try:
        response = requests.get(url, headers=headers)
        print(f"状态码: {response.status_code}")
        print(f"内容: {response.text[:1000]}")
        
    except Exception as e:
        print(f"错误: {e}")

def check_api_key_format():
    """检查 API 密钥格式"""
    print("\n\n3. 检查 API 密钥...")
    
    api_key = os.getenv('BYBIT_API_KEY')
    api_secret = os.getenv('BYBIT_SECRET_KEY')
    
    if api_key:
        print(f"API Key 长度: {len(api_key)}")
        print(f"API Key 示例: {api_key[:8]}...{api_key[-4:]}")
        
    if api_secret:
        print(f"Secret 长度: {len(api_secret)}")
        print(f"Secret 示例: {api_secret[:8]}...{api_secret[-4:]}")

if __name__ == "__main__":
    print("="*60)
    print("Bybit API 调试")
    print("="*60)
    
    test_public_endpoint()
    test_private_endpoint()
    check_api_key_format()
    
    print("\n" + "="*60)
    print("提示：")
    print("1. 如果公共端点返回 HTML，可能是域名错误")
    print("2. 如果返回 'Invalid ApiKey'，需要 Demo API")
    print("3. Demo API 在 https://demo.bybit.com 创建")