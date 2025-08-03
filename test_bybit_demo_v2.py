#!/usr/bin/env python3
"""测试 Bybit Demo Trading API V2"""

import asyncio
import os
from dotenv import load_dotenv
from src.exchanges.bybit_demo import BybitDemoExchange

load_dotenv()

async def test():
    """测试 Bybit Demo Trading"""
    print("="*60)
    print("Bybit Demo Trading 测试")
    print("="*60)
    
    # 创建交易所实例
    exchange = BybitDemoExchange(
        api_key=os.getenv('BYBIT_API_KEY'),
        secret_key=os.getenv('BYBIT_SECRET_KEY')
    )
    
    try:
        # 1. 测试连接
        print("\n1. 测试连接...")
        await exchange.connect()
        print("   ✅ 连接成功!")
        
        # 2. 获取余额
        print("\n2. 获取 Demo 账户余额...")
        try:
            balances = await exchange.get_balance()
            print("   Demo 账户余额:")
            
            total_value = 0
            for asset, balance in balances.items():
                if balance['total'] > 0:
                    print(f"   {asset}: {balance['total']:,.4f}")
                    if asset == 'USDT':
                        total_value += balance['total']
                        
            if total_value == 0:
                print("   ⚠️  余额为0，可能需要：")
                print("      1. 登录 https://demo.bybit.com")
                print("      2. 点击 'Reset Demo Balance' 重置资金")
                
        except Exception as e:
            print(f"   ❌ 获取余额失败: {e}")
        
        # 3. 获取价格
        print("\n3. 获取市场价格...")
        symbols = ['BTC/USDT', 'ETH/USDT']
        
        for symbol in symbols:
            try:
                ticker = await exchange.get_ticker(symbol)
                print(f"\n   {symbol}:")
                print(f"   买价: ${ticker['bid']:,.2f}")
                print(f"   卖价: ${ticker['ask']:,.2f}")
                print(f"   最新: ${ticker['last']:,.2f}")
                print(f"   价差: ${ticker['ask'] - ticker['bid']:.2f} ({((ticker['ask'] - ticker['bid'])/ticker['bid']*100):.3f}%)")
            except Exception as e:
                print(f"   ❌ 获取 {symbol} 价格失败: {e}")
        
        # 4. 测试下单（小额）
        print("\n4. 测试下单功能...")
        try:
            # 获取 BTC 当前价格
            btc_ticker = await exchange.get_ticker('BTC/USDT')
            
            # 下一个远离市场价的买单（避免成交）
            test_price = btc_ticker['bid'] * 0.8  # 比当前价格低20%
            test_amount = 0.001  # 最小单位
            
            print(f"   测试买单: 0.001 BTC @ ${test_price:,.2f}")
            order = await exchange.place_order(
                symbol='BTC/USDT',
                side='buy',
                amount=test_amount,
                price=test_price
            )
            
            print(f"   ✅ 订单创建成功!")
            print(f"   订单ID: {order['orderId']}")
            
            # 查询订单状态
            await asyncio.sleep(1)
            status = await exchange.get_order_status(order['orderId'], 'BTC/USDT')
            if status:
                print(f"   订单状态: {status['status']}")
            
            # 取消订单
            print("\n   测试取消订单...")
            success = await exchange.cancel_order(order['orderId'], 'BTC/USDT')
            if success:
                print("   ✅ 订单已取消")
            
        except Exception as e:
            print(f"   ❌ 下单测试失败: {e}")
        
        print("\n" + "="*60)
        print("✅ 测试完成!")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        
    finally:
        await exchange.disconnect()

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════╗
║            Bybit Demo Trading 测试               ║
║                                                  ║
║  确保您已经：                                    ║
║  1. 在 https://demo.bybit.com 创建账户          ║
║  2. 创建 Demo API Key（不是主网 API）            ║
║  3. 激活 Demo 账户（至少登录一次）               ║
╚══════════════════════════════════════════════════╝
""")
    
    asyncio.run(test())