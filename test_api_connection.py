#!/usr/bin/env python3
"""测试 API 连接"""

import os
import ccxt
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_binance():
    """测试 Binance 连接"""
    print("测试 Binance 连接...")
    try:
        # 使用公共 API 测试（不需要密钥）
        exchange = ccxt.binance({
            'options': {
                'defaultType': 'spot',
            },
            'urls': {
                'api': {
                    'public': 'https://api.binance.com/api',
                    'private': 'https://api.binance.com/api',
                }
            }
        })
        
        # 获取 BTC/USDT 价格
        ticker = exchange.fetch_ticker('BTC/USDT')
        print(f"✅ Binance 公共 API 连接成功!")
        print(f"   BTC/USDT 价格: ${ticker['last']:,.2f}")
        
        # 测试带密钥的连接
        if os.getenv('BINANCE_API_KEY'):
            auth_exchange = ccxt.binance({
                'apiKey': os.getenv('BINANCE_API_KEY'),
                'secret': os.getenv('BINANCE_SECRET_KEY'),
                'enableRateLimit': True,
            })
            
            # 获取账户信息
            try:
                balance = auth_exchange.fetch_balance()
                print(f"✅ Binance API 密钥验证成功!")
                print(f"   USDT 余额: {balance['USDT']['free']:.2f}")
            except Exception as e:
                print(f"❌ Binance API 密钥验证失败: {str(e)}")
                
    except Exception as e:
        print(f"❌ Binance 连接失败: {e}")

def test_bybit():
    """测试 Bybit 连接"""
    print("\n测试 Bybit 连接...")
    try:
        # 使用公共 API 测试
        exchange = ccxt.bybit({
            'options': {
                'defaultType': 'spot',
            }
        })
        
        # 获取 BTC/USDT 价格
        ticker = exchange.fetch_ticker('BTC/USDT')
        print(f"✅ Bybit 公共 API 连接成功!")
        print(f"   BTC/USDT 价格: ${ticker['last']:,.2f}")
        
        # 测试带密钥的连接
        if os.getenv('BYBIT_API_KEY'):
            auth_exchange = ccxt.bybit({
                'apiKey': os.getenv('BYBIT_API_KEY'),
                'secret': os.getenv('BYBIT_SECRET_KEY'),
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'spot',
                }
            })
            
            # 如果是测试网
            if os.getenv('BYBIT_TESTNET', 'false').lower() == 'true':
                auth_exchange.set_sandbox_mode(True)
            
            try:
                balance = auth_exchange.fetch_balance()
                print(f"✅ Bybit API 密钥验证成功!")
                print(f"   USDT 余额: {balance['USDT']['free']:.2f}")
            except Exception as e:
                print(f"❌ Bybit API 密钥验证失败: {str(e)}")
                
    except Exception as e:
        print(f"❌ Bybit 连接失败: {e}")

if __name__ == "__main__":
    print("=" * 50)
    print("交易所 API 连接测试")
    print("=" * 50)
    
    test_binance()
    test_bybit()
    
    print("\n" + "=" * 50)
    print("建议：")
    print("1. 如果公共 API 可以连接但密钥验证失败，请检查：")
    print("   - API 密钥是否正确")
    print("   - API 密钥是否有交易权限")
    print("   - IP 白名单是否包含服务器 IP: 64.176.48.97")
    print("2. 对于测试网，需要使用测试网专用的 API 密钥")