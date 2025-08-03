#!/usr/bin/env python3
"""测试 Binance 和 Bybit 测试网 API"""

import os
import ccxt
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_binance_testnet():
    """测试 Binance 测试网"""
    print("测试 Binance Spot 测试网...")
    
    try:
        # 配置测试网
        exchange = ccxt.binance({
            'apiKey': os.getenv('BINANCE_API_KEY'),
            'secret': os.getenv('BINANCE_SECRET_KEY'),
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot',
            },
            'urls': {
                'api': {
                    'public': 'https://testnet.binance.vision/api/v3',
                    'private': 'https://testnet.binance.vision/api/v3',
                }
            },
            'hostname': 'testnet.binance.vision'
        })
        
        # 测试公共 API
        ticker = exchange.fetch_ticker('BTC/USDT')
        print(f"✅ Binance 测试网公共 API 连接成功!")
        print(f"   BTC/USDT 价格: ${ticker['last']:,.2f}")
        
        # 测试私有 API
        try:
            balance = exchange.fetch_balance()
            print(f"✅ Binance 测试网 API 密钥验证成功!")
            
            # 显示余额
            print("\n💰 测试网余额:")
            for currency, bal in balance['total'].items():
                if bal > 0:
                    print(f"   {currency}: {bal:.4f}")
                    
        except Exception as e:
            print(f"❌ Binance 测试网 API 密钥验证失败: {str(e)}")
            
    except Exception as e:
        print(f"❌ Binance 测试网连接失败: {e}")

def test_bybit_testnet():
    """测试 Bybit 测试网"""
    print("\n测试 Bybit 测试网...")
    
    try:
        exchange = ccxt.bybit({
            'apiKey': os.getenv('BYBIT_API_KEY'),
            'secret': os.getenv('BYBIT_SECRET_KEY'),
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot',
            }
        })
        
        # 启用测试网模式
        exchange.set_sandbox_mode(True)
        
        # 测试公共 API
        ticker = exchange.fetch_ticker('BTC/USDT')
        print(f"✅ Bybit 测试网公共 API 连接成功!")
        print(f"   BTC/USDT 价格: ${ticker['last']:,.2f}")
        
        # 测试私有 API
        try:
            balance = exchange.fetch_balance()
            print(f"✅ Bybit 测试网 API 密钥验证成功!")
            
            # 显示余额
            print("\n💰 测试网余额:")
            for currency, bal in balance['total'].items():
                if bal > 0:
                    print(f"   {currency}: {bal:.4f}")
                    
        except Exception as e:
            print(f"❌ Bybit 测试网 API 密钥验证失败: {str(e)}")
            
    except Exception as e:
        print(f"❌ Bybit 测试网连接失败: {e}")

if __name__ == "__main__":
    print("="*50)
    print("测试网 API 连接测试")
    print("="*50)
    
    test_binance_testnet()
    test_bybit_testnet()
    
    print("\n" + "="*50)
    print("提示：")
    print("1. Binance 测试网: https://testnet.binance.vision")
    print("2. Bybit 测试网: https://testnet.bybit.com")
    print("3. 测试网的 API 密钥与主网不同")
    print("4. 测试网可以免费获取测试币进行交易测试")