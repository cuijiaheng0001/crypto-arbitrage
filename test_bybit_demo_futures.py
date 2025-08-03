#!/usr/bin/env python3
"""
Bybit Demo Futures Trading Test
测试 Bybit Demo API 的期货交易功能
"""

import time
import hmac
import hashlib
import requests
import json
from urllib.parse import urlencode

# Bybit Demo API 配置
API_KEY = ""  # 需要填入您的 Demo API Key
API_SECRET = ""  # 需要填入您的 Demo API Secret
BASE_URL = "https://api-demo.bybit.com"

def generate_signature(params, api_secret):
    """生成签名"""
    param_str = urlencode(sorted(params.items()))
    return hmac.new(
        api_secret.encode('utf-8'),
        param_str.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

def make_request(endpoint, method="GET", params=None):
    """发送 API 请求"""
    if params is None:
        params = {}
    
    # 添加时间戳
    timestamp = str(int(time.time() * 1000))
    params['api_key'] = API_KEY
    params['timestamp'] = timestamp
    params['recv_window'] = '5000'
    
    # 生成签名
    sign = generate_signature(params, API_SECRET)
    params['sign'] = sign
    
    # 发送请求
    url = f"{BASE_URL}{endpoint}"
    
    if method == "GET":
        response = requests.get(url, params=params)
    else:
        response = requests.post(url, json=params)
    
    return response.json()

def test_demo_futures():
    """测试 Demo 期货功能"""
    print("=== Bybit Demo Futures API Test ===\n")
    
    # 1. 获取账户余额
    print("1. 获取账户余额:")
    balance = make_request("/v5/account/wallet-balance", params={"accountType": "UNIFIED"})
    print(json.dumps(balance, indent=2))
    print()
    
    # 2. 获取市场价格
    print("2. 获取 BTCUSDT 期货价格:")
    ticker = make_request("/v5/market/tickers", params={
        "category": "linear",
        "symbol": "BTCUSDT"
    })
    print(json.dumps(ticker, indent=2))
    print()
    
    # 3. 下一个小额市价单测试
    print("3. 下一个测试订单 (0.001 BTC):")
    order_params = {
        "category": "linear",  # USDT 永续合约
        "symbol": "BTCUSDT",
        "side": "Buy",
        "orderType": "Market",
        "qty": "0.001",
        "timeInForce": "IOC"
    }
    
    order = make_request("/v5/order/create", method="POST", params=order_params)
    print(json.dumps(order, indent=2))
    print()
    
    # 4. 查询持仓
    print("4. 查询当前持仓:")
    positions = make_request("/v5/position/list", params={
        "category": "linear",
        "symbol": "BTCUSDT"
    })
    print(json.dumps(positions, indent=2))
    print()
    
    # 5. 获取订单历史
    print("5. 获取最近订单:")
    orders = make_request("/v5/order/history", params={
        "category": "linear",
        "limit": "5"
    })
    print(json.dumps(orders, indent=2))

def test_supported_products():
    """测试支持的产品类型"""
    print("\n=== 测试支持的产品类型 ===\n")
    
    categories = ["linear", "inverse", "spot", "option"]
    
    for category in categories:
        print(f"测试 {category} 产品:")
        try:
            symbols = make_request("/v5/market/instruments-info", params={
                "category": category,
                "limit": "3"
            })
            if symbols.get('retCode') == 0:
                print(f"✓ {category} 支持")
                if symbols.get('result', {}).get('list'):
                    for item in symbols['result']['list'][:3]:
                        print(f"  - {item.get('symbol', 'N/A')}")
            else:
                print(f"✗ {category} 不支持: {symbols.get('retMsg', 'Unknown error')}")
        except Exception as e:
            print(f"✗ {category} 请求失败: {str(e)}")
        print()

if __name__ == "__main__":
    if not API_KEY or not API_SECRET:
        print("请先设置 API_KEY 和 API_SECRET!")
        print("\n获取 Demo API Key 步骤:")
        print("1. 登录 Bybit 主网账户")
        print("2. 点击右上角头像 → Demo Trading")
        print("3. 进入 API 管理 → 创建 API Key")
        print("4. 选择 Demo 选项卡，只勾选 Read + Trade")
        print("5. 将生成的 Key 和 Secret 填入此脚本")
    else:
        # 测试基础功能
        test_demo_futures()
        
        # 测试支持的产品类型
        test_supported_products()