#!/usr/bin/env python3
"""
测试 Bitget 单交易所三角套利
"""

import ccxt
import sys
sys.path.append('/root/crypto-arbitrage')
from triangular_arbitrage import TriangularArbitrage
import logging

logging.basicConfig(level=logging.INFO)

# 初始化 Bitget
exchange = ccxt.bitget({
    'enableRateLimit': True,
    'timeout': 30000
})

# 创建三角套利引擎
arbitrage = TriangularArbitrage(exchange, min_profit_percentage=0.1)

print("获取 Bitget 市场数据...")
tickers = exchange.fetch_tickers()
print(f"获取到 {len(tickers)} 个交易对")

# 构建图
print("\n构建价格图...")
arbitrage.build_graph(tickers)

# 寻找套利机会
print("\n寻找三角套利机会...")
opportunities = arbitrage.find_arbitrage_cycles('USDT', max_length=4)

if opportunities:
    print(f"\n🎯 发现 {len(opportunities)} 个套利机会:")
    for i, opp in enumerate(opportunities[:10]):
        print(f"\n机会 {i+1}:")
        print(f"路径: {' → '.join(opp['path'])}")
        print(f"预期利润: {opp['profit_percentage']:.3f}%")
        print(f"预计手续费: {opp['fees_estimated']:.3f}%")
        print(f"净利润: {opp['profit_percentage'] - opp['fees_estimated']:.3f}%")
        
        print("交易步骤:")
        for step in opp['path_info']:
            print(f"  {step['action'].upper()} {step['symbol']} @ {step['price']}")
else:
    print("\n未发现套利机会")
    print("提示：三角套利机会通常很少且转瞬即逝")