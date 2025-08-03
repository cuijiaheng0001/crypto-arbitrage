#!/usr/bin/env python3
"""
实时监控仪表板
整合所有套利策略的监控和分析
"""

import os
import time
import json
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from collections import defaultdict
import glob

class ArbitrageDashboard:
    def __init__(self):
        """初始化仪表板"""
        self.strategies = {
            'cross_exchange': {'name': '跨交易所套利', 'status': 'unknown', 'pnl': 0},
            'triangular': {'name': '三角套利', 'status': 'unknown', 'pnl': 0},
            'funding_rate': {'name': '资金费率套利', 'status': 'unknown', 'pnl': 0},
            'websocket': {'name': 'WebSocket高速套利', 'status': 'unknown', 'pnl': 0},
        }
        
        self.log_files = {
            'cross_exchange': 'logs/telegram_arbitrage.log',
            'triangular': 'logs/triangular_arbitrage.log',
            'funding_rate': 'logs/funding_rate_arbitrage.log',
            'websocket': 'logs/websocket_arbitrage.log',
        }
        
        self.performance_data = defaultdict(list)
        
    def check_process_status(self):
        """检查各策略进程状态"""
        import subprocess
        
        process_patterns = {
            'cross_exchange': 'telegram_arbitrage_bot.py',
            'triangular': 'triangular_arbitrage.py',
            'funding_rate': 'funding_rate_arbitrage.py',
            'websocket': 'websocket_arbitrage_bot.py',
        }
        
        for strategy, pattern in process_patterns.items():
            try:
                result = subprocess.run(['pgrep', '-f', pattern], capture_output=True, text=True)
                if result.returncode == 0:
                    self.strategies[strategy]['status'] = 'running'
                    self.strategies[strategy]['pid'] = result.stdout.strip()
                else:
                    self.strategies[strategy]['status'] = 'stopped'
            except:
                self.strategies[strategy]['status'] = 'unknown'
    
    def analyze_logs(self):
        """分析日志文件获取性能数据"""
        for strategy, log_file in self.log_files.items():
            if os.path.exists(log_file):
                try:
                    # 读取最后1000行
                    with open(log_file, 'r') as f:
                        lines = f.readlines()[-1000:]
                    
                    # 分析机会和执行
                    opportunities = 0
                    executions = 0
                    profits = 0
                    
                    for line in lines:
                        if '发现套利机会' in line or '发现机会' in line:
                            opportunities += 1
                        if '执行成功' in line or '交易执行成功' in line:
                            executions += 1
                        # 提取利润
                        if '利润:' in line:
                            try:
                                profit_str = line.split('利润:')[1].split()[0]
                                profit = float(profit_str.replace('$', '').replace(',', ''))
                                profits += profit
                            except:
                                pass
                    
                    self.strategies[strategy]['opportunities'] = opportunities
                    self.strategies[strategy]['executions'] = executions
                    self.strategies[strategy]['pnl'] = profits
                    
                except Exception as e:
                    print(f"分析 {strategy} 日志失败: {e}")
    
    def calculate_statistics(self):
        """计算综合统计数据"""
        total_pnl = sum(s['pnl'] for s in self.strategies.values())
        active_strategies = sum(1 for s in self.strategies.values() if s['status'] == 'running')
        total_opportunities = sum(s.get('opportunities', 0) for s in self.strategies.values())
        total_executions = sum(s.get('executions', 0) for s in self.strategies.values())
        
        return {
            'total_pnl': total_pnl,
            'active_strategies': active_strategies,
            'total_opportunities': total_opportunities,
            'total_executions': total_executions,
            'success_rate': (total_executions / total_opportunities * 100) if total_opportunities > 0 else 0
        }
    
    def analyze_best_hours(self):
        """分析最佳交易时段"""
        hourly_data = defaultdict(lambda: {'opportunities': 0, 'profits': 0})
        
        # 分析所有日志文件
        for log_file in self.log_files.values():
            if os.path.exists(log_file):
                try:
                    with open(log_file, 'r') as f:
                        for line in f:
                            # 提取时间戳
                            if line.startswith('20'):  # 假设日志以日期开始
                                try:
                                    timestamp_str = line.split(' - ')[0]
                                    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')
                                    hour = timestamp.hour
                                    
                                    if '发现' in line and '机会' in line:
                                        hourly_data[hour]['opportunities'] += 1
                                    
                                    if '利润:' in line:
                                        try:
                                            profit = float(line.split('利润:')[1].split()[0].replace('$', ''))
                                            hourly_data[hour]['profits'] += profit
                                        except:
                                            pass
                                except:
                                    pass
                except:
                    pass
        
        # 找出最佳时段
        best_hours = sorted(hourly_data.items(), 
                          key=lambda x: x[1]['profits'], 
                          reverse=True)[:5]
        
        return best_hours
    
    def print_dashboard(self):
        """打印仪表板"""
        os.system('clear' if os.name == 'posix' else 'cls')
        
        print("=" * 80)
        print("                     🚀 加密货币套利监控仪表板")
        print("=" * 80)
        print(f"⏰ 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # 策略状态
        print("📊 策略运行状态:")
        print("-" * 80)
        print(f"{'策略名称':<20} {'状态':<10} {'PID':<10} {'机会':<10} {'执行':<10} {'盈亏':<15}")
        print("-" * 80)
        
        for key, strategy in self.strategies.items():
            status_emoji = "🟢" if strategy['status'] == 'running' else "🔴"
            pid = strategy.get('pid', '-')
            opportunities = strategy.get('opportunities', 0)
            executions = strategy.get('executions', 0)
            pnl = strategy.get('pnl', 0)
            
            print(f"{strategy['name']:<20} {status_emoji} {strategy['status']:<8} "
                  f"{pid:<10} {opportunities:<10} {executions:<10} ${pnl:>12.2f}")
        
        # 综合统计
        stats = self.calculate_statistics()
        print("\n" + "=" * 80)
        print("💰 综合统计:")
        print("-" * 80)
        print(f"活跃策略数: {stats['active_strategies']}")
        print(f"总发现机会: {stats['total_opportunities']}")
        print(f"总执行次数: {stats['total_executions']}")
        print(f"执行成功率: {stats['success_rate']:.1f}%")
        print(f"总盈亏: ${stats['total_pnl']:.2f}")
        
        # 最佳交易时段
        best_hours = self.analyze_best_hours()
        if best_hours:
            print("\n" + "=" * 80)
            print("🕐 最佳交易时段:")
            print("-" * 80)
            for hour, data in best_hours[:3]:
                print(f"{hour:02d}:00-{hour+1:02d}:00 | "
                      f"机会: {data['opportunities']} | "
                      f"利润: ${data['profits']:.2f}")
        
        # 风险警告
        print("\n" + "=" * 80)
        print("⚠️  风险监控:")
        print("-" * 80)
        
        # 检查是否有策略停止
        stopped_strategies = [s['name'] for s in self.strategies.values() 
                            if s['status'] == 'stopped']
        if stopped_strategies:
            print(f"❌ 已停止策略: {', '.join(stopped_strategies)}")
        else:
            print("✅ 所有策略运行正常")
        
        # 建议
        print("\n" + "=" * 80)
        print("💡 优化建议:")
        print("-" * 80)
        
        if stats['success_rate'] < 50:
            print("• 执行成功率较低，建议调整参数或检查网络延迟")
        
        if stats['active_strategies'] < 3:
            print("• 建议启动更多策略以增加套利机会")
        
        if best_hours and best_hours[0][0] not in [datetime.now().hour - 1, datetime.now().hour, datetime.now().hour + 1]:
            print(f"• 当前非最佳交易时段，最佳时段为 {best_hours[0][0]}:00")
        
        print("=" * 80)
    
    def save_performance_data(self):
        """保存性能数据"""
        timestamp = datetime.now()
        stats = self.calculate_statistics()
        
        performance_record = {
            'timestamp': timestamp.isoformat(),
            'total_pnl': stats['total_pnl'],
            'active_strategies': stats['active_strategies'],
            'opportunities': stats['total_opportunities'],
            'executions': stats['total_executions'],
            'success_rate': stats['success_rate'],
            'strategies': dict(self.strategies)
        }
        
        # 保存到JSON文件
        filename = f"data/performance_{timestamp.strftime('%Y%m%d')}.json"
        os.makedirs('data', exist_ok=True)
        
        try:
            # 读取现有数据
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    data = json.load(f)
            else:
                data = []
            
            # 添加新记录
            data.append(performance_record)
            
            # 保存
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
        except:
            pass
    
    def run(self, refresh_interval=10):
        """运行仪表板"""
        print("启动套利监控仪表板...")
        print("按 Ctrl+C 退出")
        
        try:
            while True:
                # 更新数据
                self.check_process_status()
                self.analyze_logs()
                
                # 显示仪表板
                self.print_dashboard()
                
                # 保存性能数据
                self.save_performance_data()
                
                # 等待刷新
                time.sleep(refresh_interval)
                
        except KeyboardInterrupt:
            print("\n仪表板已关闭")

def main():
    """主函数"""
    dashboard = ArbitrageDashboard()
    dashboard.run()

if __name__ == "__main__":
    main()