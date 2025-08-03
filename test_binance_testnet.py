#!/usr/bin/env python3
"""测试 Binance 测试网实现"""

import asyncio
import os
from dotenv import load_dotenv
from src.exchanges.binance_testnet import BinanceTestnetExchange

load_dotenv()

async def test():
    """测试 Binance 测试网"""
    print("="*50)
    print("测试 Binance Testnet 实现")
    print("="*50)
    
    # 创建交易所实例
    exchange = BinanceTestnetExchange(
        api_key=os.getenv('BINANCE_API_KEY'),
        secret_key=os.getenv('BINANCE_SECRET_KEY')
    )
    
    try:
        # 测试连接
        print("\n1. 测试连接...")
        await exchange.connect()
        print("   ✅ 连接成功!")
        
        # 获取余额
        print("\n2. 获取余额...")
        balances = await exchange.get_balance()
        print("   测试网余额:")
        for asset, balance in balances.items():
            if balance['total'] > 0:
                print(f"   {asset}: {balance['total']:.4f} (可用: {balance['free']:.4f})")
        
        # 获取价格
        print("\n3. 获取 BTC/USDT 价格...")
        ticker = await exchange.get_ticker('BTC/USDT')
        print(f"   买价: ${ticker['bid']:,.2f}")
        print(f"   卖价: ${ticker['ask']:,.2f}")
        print(f"   价差: ${ticker['ask'] - ticker['bid']:.2f}")
        
        # 获取 ETH/USDT 价格
        print("\n4. 获取 ETH/USDT 价格...")
        ticker = await exchange.get_ticker('ETH/USDT')
        print(f"   买价: ${ticker['bid']:,.2f}")
        print(f"   卖价: ${ticker['ask']:,.2f}")
        
        print("\n✅ 所有测试通过!")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        
    finally:
        await exchange.disconnect()

if __name__ == "__main__":
    asyncio.run(test())
    
    print("\n" + "="*50)
    print("提示：")
    print("1. 如果余额为0，可以在测试网申请测试币")
    print("2. 访问: https://testnet.binance.vision")
    print("3. 登录后在 Faucet 页面申请测试币")