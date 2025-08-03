#!/usr/bin/env python3
"""
三角套利策略模块
在单个交易所内寻找三角套利机会
例如: BTC -> ETH -> USDT -> BTC
"""

import networkx as nx
import numpy as np
import logging
from typing import List, Dict, Tuple
import math

logger = logging.getLogger(__name__)

class TriangularArbitrage:
    def __init__(self, exchange, min_profit_percentage=0.1):
        """
        初始化三角套利引擎
        
        Args:
            exchange: ccxt 交易所实例
            min_profit_percentage: 最小利润率阈值
        """
        self.exchange = exchange
        self.min_profit_percentage = min_profit_percentage
        self.graph = nx.DiGraph()
        self.symbols_data = {}
        
    def build_graph(self, tickers: Dict):
        """
        构建市场价格图
        
        Args:
            tickers: 交易所的所有ticker数据
        """
        self.graph.clear()
        self.symbols_data.clear()
        
        for symbol, ticker in tickers.items():
            if '/' not in symbol:
                continue
                
            base, quote = symbol.split('/')
            
            # 过滤掉价格为0或None的数据
            if not ticker['bid'] or not ticker['ask'] or ticker['bid'] <= 0 or ticker['ask'] <= 0:
                continue
            
            # 存储symbol数据
            self.symbols_data[symbol] = ticker
            
            # 添加边：从quote到base（买入base）
            # 权重使用负对数，这样可以用最短路径算法找到最大收益路径
            weight_buy = -math.log(1 / ticker['ask'])  # 买入价格的倒数
            self.graph.add_edge(quote, base, weight=weight_buy, price=ticker['ask'], 
                              action='buy', symbol=symbol)
            
            # 添加边：从base到quote（卖出base）
            weight_sell = -math.log(ticker['bid'])  # 卖出价格
            self.graph.add_edge(base, quote, weight=weight_sell, price=ticker['bid'], 
                              action='sell', symbol=symbol)
    
    def find_arbitrage_cycles(self, start_currency='USDT', max_length=4):
        """
        寻找套利循环
        
        Args:
            start_currency: 起始货币
            max_length: 最大路径长度
            
        Returns:
            List of arbitrage opportunities
        """
        opportunities = []
        
        if start_currency not in self.graph:
            logger.warning(f"起始货币 {start_currency} 不在图中")
            return opportunities
        
        # 寻找从start_currency出发又回到start_currency的简单循环
        try:
            # 使用 Bellman-Ford 算法的变体来检测负环
            for cycle_length in range(3, max_length + 1):
                cycles = self._find_cycles_of_length(start_currency, cycle_length)
                
                for cycle in cycles:
                    profit = self._calculate_cycle_profit(cycle)
                    
                    if profit > self.min_profit_percentage:
                        path_info = self._get_path_info(cycle)
                        opportunities.append({
                            'path': cycle,
                            'profit_percentage': profit,
                            'path_info': path_info,
                            'fees_estimated': len(cycle) * 0.1  # 假设每步0.1%手续费
                        })
        
        except Exception as e:
            logger.error(f"寻找套利循环时出错: {e}")
        
        # 按利润率排序
        opportunities.sort(key=lambda x: x['profit_percentage'], reverse=True)
        
        return opportunities
    
    def _find_cycles_of_length(self, start, length):
        """
        寻找特定长度的循环
        """
        cycles = []
        
        def dfs(node, path, visited):
            if len(path) == length:
                if node == start and len(set(path[:-1])) == len(path) - 1:
                    cycles.append(path[:])
                return
            
            if node in self.graph:
                for neighbor in self.graph[node]:
                    if neighbor not in visited or (neighbor == start and len(path) == length - 1):
                        visited.add(neighbor)
                        path.append(neighbor)
                        dfs(neighbor, path, visited)
                        path.pop()
                        if neighbor != start:
                            visited.remove(neighbor)
        
        visited = {start}
        dfs(start, [start], visited)
        
        return cycles
    
    def _calculate_cycle_profit(self, cycle):
        """
        计算循环的利润率
        """
        total_ratio = 1.0
        
        for i in range(len(cycle) - 1):
            edge_data = self.graph.get_edge_data(cycle[i], cycle[i + 1])
            if edge_data:
                # 使用实际价格计算
                price = edge_data['price']
                if edge_data['action'] == 'buy':
                    total_ratio *= (1 / price)
                else:
                    total_ratio *= price
        
        # 转换为百分比利润
        profit_percentage = (total_ratio - 1) * 100
        
        return profit_percentage
    
    def _get_path_info(self, cycle):
        """
        获取路径详细信息
        """
        path_info = []
        
        for i in range(len(cycle) - 1):
            edge_data = self.graph.get_edge_data(cycle[i], cycle[i + 1])
            if edge_data:
                path_info.append({
                    'from': cycle[i],
                    'to': cycle[i + 1],
                    'action': edge_data['action'],
                    'symbol': edge_data['symbol'],
                    'price': edge_data['price']
                })
        
        return path_info
    
    def execute_arbitrage(self, opportunity, amount):
        """
        执行套利交易（模拟）
        
        Args:
            opportunity: 套利机会
            amount: 初始金额
            
        Returns:
            执行结果
        """
        logger.info(f"执行三角套利: {' -> '.join(opportunity['path'])}")
        
        current_amount = amount
        executed_trades = []
        
        for step in opportunity['path_info']:
            try:
                symbol = step['symbol']
                action = step['action']
                price = step['price']
                
                if action == 'buy':
                    # 买入
                    trade_amount = current_amount / price
                    fee = trade_amount * 0.001  # 0.1% 手续费
                    current_amount = trade_amount - fee
                    
                    executed_trades.append({
                        'symbol': symbol,
                        'side': 'buy',
                        'price': price,
                        'amount': trade_amount,
                        'cost': current_amount * price,
                        'fee': fee
                    })
                    
                else:
                    # 卖出
                    trade_value = current_amount * price
                    fee = trade_value * 0.001
                    current_amount = trade_value - fee
                    
                    executed_trades.append({
                        'symbol': symbol,
                        'side': 'sell',
                        'price': price,
                        'amount': current_amount,
                        'value': trade_value,
                        'fee': fee
                    })
                
                logger.info(f"{action.upper()} {symbol} @ {price}, "
                          f"当前持有: {current_amount:.6f} {step['to']}")
            
            except Exception as e:
                logger.error(f"执行交易 {symbol} 时出错: {e}")
                return None
        
        final_profit = current_amount - amount
        profit_percentage = (final_profit / amount) * 100
        
        result = {
            'initial_amount': amount,
            'final_amount': current_amount,
            'profit': final_profit,
            'profit_percentage': profit_percentage,
            'executed_trades': executed_trades,
            'path': opportunity['path']
        }
        
        logger.info(f"三角套利完成: 利润 {profit_percentage:.3f}%")
        
        return result


class MultiExchangeTriangularArbitrage:
    """
    跨交易所三角套利
    在多个交易所之间寻找三角套利机会
    """
    
    def __init__(self, exchanges: Dict, min_profit_percentage=0.2):
        """
        Args:
            exchanges: {'exchange_name': ccxt_instance} 字典
            min_profit_percentage: 最小利润率
        """
        self.exchanges = exchanges
        self.min_profit_percentage = min_profit_percentage
        self.combined_graph = nx.DiGraph()
        
    def build_combined_graph(self, all_tickers: Dict[str, Dict]):
        """
        构建跨交易所的组合图
        
        Args:
            all_tickers: {'exchange_name': {symbol: ticker_data}}
        """
        self.combined_graph.clear()
        
        for exchange_name, tickers in all_tickers.items():
            for symbol, ticker in tickers.items():
                if '/' not in symbol or not ticker['bid'] or not ticker['ask']:
                    continue
                
                base, quote = symbol.split('/')
                
                # 为节点添加交易所前缀以区分不同交易所的同一货币
                base_node = f"{base}@{exchange_name}"
                quote_node = f"{quote}@{exchange_name}"
                
                # 添加交易边
                self.combined_graph.add_edge(
                    quote_node, base_node,
                    weight=-math.log(1 / ticker['ask']),
                    price=ticker['ask'],
                    action='buy',
                    symbol=symbol,
                    exchange=exchange_name
                )
                
                self.combined_graph.add_edge(
                    base_node, quote_node,
                    weight=-math.log(ticker['bid']),
                    price=ticker['bid'],
                    action='sell',
                    symbol=symbol,
                    exchange=exchange_name
                )
        
        # 添加跨交易所转账边（假设可以免费转账）
        self._add_transfer_edges()
    
    def _add_transfer_edges(self):
        """
        添加跨交易所转账边
        """
        currencies = set()
        exchange_currencies = {}
        
        # 收集所有货币和它们所在的交易所
        for node in self.combined_graph.nodes():
            currency, exchange = node.split('@')
            currencies.add(currency)
            
            if currency not in exchange_currencies:
                exchange_currencies[currency] = []
            exchange_currencies[currency].append(exchange)
        
        # 为每种货币添加跨交易所转账边
        for currency, exchanges in exchange_currencies.items():
            for i, ex1 in enumerate(exchanges):
                for ex2 in exchanges[i+1:]:
                    # 双向转账，权重为0（假设无成本）
                    node1 = f"{currency}@{ex1}"
                    node2 = f"{currency}@{ex2}"
                    
                    self.combined_graph.add_edge(
                        node1, node2,
                        weight=0,
                        action='transfer',
                        currency=currency,
                        from_exchange=ex1,
                        to_exchange=ex2
                    )
                    
                    self.combined_graph.add_edge(
                        node2, node1,
                        weight=0,
                        action='transfer',
                        currency=currency,
                        from_exchange=ex2,
                        to_exchange=ex1
                    )


# 使用示例
if __name__ == "__main__":
    import ccxt
    
    # 初始化交易所
    exchange = ccxt.binance({
        'enableRateLimit': True
    })
    
    # 创建三角套利引擎
    arbitrage = TriangularArbitrage(exchange, min_profit_percentage=0.1)
    
    # 获取所有ticker数据
    print("获取市场数据...")
    tickers = exchange.fetch_tickers()
    
    # 构建图
    print("构建价格图...")
    arbitrage.build_graph(tickers)
    
    # 寻找套利机会
    print("寻找三角套利机会...")
    opportunities = arbitrage.find_arbitrage_cycles('USDT', max_length=4)
    
    # 显示结果
    if opportunities:
        print(f"\n发现 {len(opportunities)} 个套利机会:")
        for i, opp in enumerate(opportunities[:5]):  # 只显示前5个
            print(f"\n机会 {i+1}:")
            print(f"路径: {' -> '.join(opp['path'])}")
            print(f"预期利润: {opp['profit_percentage']:.3f}%")
            print(f"预计手续费: {opp['fees_estimated']:.3f}%")
            print(f"净利润: {opp['profit_percentage'] - opp['fees_estimated']:.3f}%")
            
            print("交易步骤:")
            for step in opp['path_info']:
                print(f"  {step['action'].upper()} {step['symbol']} @ {step['price']}")
    else:
        print("未发现套利机会")