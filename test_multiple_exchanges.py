#!/usr/bin/env python3
"""
多交易所 Demo/Testnet 环境测试
测试 Bybit Demo、Testnet、KuCoin Sandbox 等环境
"""

import requests
import time
import hmac
import hashlib
import json
from urllib.parse import urlencode

class ExchangeTester:
    def __init__(self):
        self.results = {}
    
    def test_bybit_demo(self):
        """测试 Bybit Demo API"""
        print("🔍 测试 Bybit Demo API...")
        
        try:
            # 测试公共端点（无需API密钥）
            url = "https://api-demo.bybit.com/v5/market/tickers"
            params = {"category": "linear", "symbol": "BTCUSDT"}
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('retCode') == 0:
                    price = data['result']['list'][0]['lastPrice']
                    self.results['bybit_demo'] = {
                        'status': '✅ 可用',
                        'btc_price': f"{price} USDT",
                        'note': '需要创建 Demo API Key 才能交易'
                    }
                else:
                    self.results['bybit_demo'] = {
                        'status': '❌ API 错误',
                        'error': data.get('retMsg', 'Unknown error')
                    }
            else:
                self.results['bybit_demo'] = {
                    'status': f'❌ HTTP {response.status_code}',
                    'error': response.text[:100]
                }
                
        except Exception as e:
            self.results['bybit_demo'] = {
                'status': '❌ 连接失败',
                'error': str(e)
            }
    
    def test_bybit_testnet(self):
        """测试 Bybit Testnet API"""
        print("🔍 测试 Bybit Testnet API...")
        
        try:
            url = "https://api-testnet.bybit.com/v5/market/tickers"
            params = {"category": "linear", "symbol": "BTCUSDT"}
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('retCode') == 0:
                    price = data['result']['list'][0]['lastPrice']
                    self.results['bybit_testnet'] = {
                        'status': '✅ 可用',
                        'btc_price': f"{price} USDT",
                        'note': '可以注册 Testnet 账户获取 API Key'
                    }
                else:
                    self.results['bybit_testnet'] = {
                        'status': '❌ API 错误',
                        'error': data.get('retMsg', 'Unknown error')
                    }
            else:
                self.results['bybit_testnet'] = {
                    'status': f'❌ HTTP {response.status_code}',
                    'error': response.text[:100]
                }
                
        except Exception as e:
            self.results['bybit_testnet'] = {
                'status': '❌ 连接失败',
                'error': str(e)
            }
    
    def test_kucoin_sandbox(self):
        """测试 KuCoin Sandbox API"""
        print("🔍 测试 KuCoin Sandbox API...")
        
        try:
            url = "https://api-sandbox.kucoin.com/api/v1/market/orderbook/level1"
            params = {"symbol": "BTC-USDT"}
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == '200000':
                    price = data['data']['price']
                    self.results['kucoin_sandbox'] = {
                        'status': '✅ 可用',
                        'btc_price': f"{price} USDT",
                        'note': '访问 https://sandbox.kucoin.com 注册'
                    }
                else:
                    self.results['kucoin_sandbox'] = {
                        'status': '❌ API 错误',
                        'error': data.get('msg', 'Unknown error')
                    }
            else:
                self.results['kucoin_sandbox'] = {
                    'status': f'❌ HTTP {response.status_code}',
                    'error': response.text[:100]
                }
                
        except Exception as e:
            self.results['kucoin_sandbox'] = {
                'status': '❌ 连接失败',
                'error': str(e)
            }
    
    def test_binance_testnet(self):
        """测试 Binance Spot Testnet API"""
        print("🔍 测试 Binance Spot Testnet API...")
        
        try:
            url = "https://testnet.binance.vision/api/v3/ticker/price"
            params = {"symbol": "BTCUSDT"}
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'price' in data:
                    price = data['price']
                    self.results['binance_testnet'] = {
                        'status': '✅ 可用',
                        'btc_price': f"{price} USDT",
                        'note': '访问 https://testnet.binance.vision 注册'
                    }
                else:
                    self.results['binance_testnet'] = {
                        'status': '❌ API 错误',
                        'error': str(data)
                    }
            else:
                self.results['binance_testnet'] = {
                    'status': f'❌ HTTP {response.status_code}',
                    'error': response.text[:100]
                }
                
        except Exception as e:
            self.results['binance_testnet'] = {
                'status': '❌ 连接失败',
                'error': str(e)
            }
    
    def test_binance_futures_testnet(self):
        """测试 Binance Futures Testnet API"""
        print("🔍 测试 Binance Futures Testnet API...")
        
        try:
            url = "https://testnet.binancefuture.com/fapi/v1/ticker/price"
            params = {"symbol": "BTCUSDT"}
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'price' in data:
                    price = data['price']
                    self.results['binance_futures_testnet'] = {
                        'status': '✅ 可用',
                        'btc_price': f"{price} USDT",
                        'note': '访问 https://testnet.binancefuture.com 注册'
                    }
                else:
                    self.results['binance_futures_testnet'] = {
                        'status': '❌ API 错误',
                        'error': str(data)
                    }
            else:
                self.results['binance_futures_testnet'] = {
                    'status': f'❌ HTTP {response.status_code}',
                    'error': response.text[:100]
                }
                
        except Exception as e:
            self.results['binance_futures_testnet'] = {
                'status': '❌ 连接失败',
                'error': str(e)
            }
    
    def run_all_tests(self):
        """运行所有测试"""
        print("=" * 60)
        print("🚀 多交易所 Demo/Testnet 环境测试")
        print("=" * 60)
        print()
        
        # 运行所有测试
        self.test_bybit_demo()
        self.test_bybit_testnet()
        self.test_kucoin_sandbox()
        self.test_binance_testnet()
        self.test_binance_futures_testnet()
        
        # 显示结果
        print("\n" + "=" * 60)
        print("📊 测试结果汇总")
        print("=" * 60)
        
        for exchange, result in self.results.items():
            print(f"\n📈 {exchange.upper().replace('_', ' ')}")
            print(f"   状态: {result['status']}")
            
            if 'btc_price' in result:
                print(f"   BTC价格: {result['btc_price']}")
            
            if 'note' in result:
                print(f"   说明: {result['note']}")
            
            if 'error' in result:
                print(f"   错误: {result['error']}")
        
        # 给出建议
        print(f"\n" + "=" * 60)
        print("💡 建议配置")
        print("=" * 60)
        
        available_exchanges = [k for k, v in self.results.items() if '✅' in v['status']]
        
        if available_exchanges:
            print(f"\n✅ 可用的测试环境: {len(available_exchanges)} 个")
            for exc in available_exchanges:
                print(f"   - {exc.replace('_', ' ').title()}")
            
            print(f"\n🎯 推荐配置:")
            if 'bybit_demo' in available_exchanges:
                print("   1. Bybit Demo (期货套利)")
                print("      需要在 https://www.bybit.com 开启 Demo Trading")
            elif 'bybit_testnet' in available_exchanges:
                print("   1. Bybit Testnet (期货套利)")
                print("      访问 https://testnet.bybit.com 注册")
            
            if 'binance_testnet' in available_exchanges:
                print("   2. Binance Spot Testnet (现货套利)")
                print("      访问 https://testnet.binance.vision 注册")
            
            if 'kucoin_sandbox' in available_exchanges:
                print("   3. KuCoin Sandbox (备用)")
                print("      访问 https://sandbox.kucoin.com 注册")
        else:
            print("\n❌ 所有测试环境都不可用")
            print("   建议检查网络连接或稍后重试")

def main():
    tester = ExchangeTester()
    tester.run_all_tests()
    
    print(f"\n" + "=" * 60)
    print("🔧 下一步操作")
    print("=" * 60)
    print("1. 选择一个可用的测试环境")
    print("2. 注册并获取 API Key")
    print("3. 更新 .env 配置文件")
    print("4. 运行套利机器人测试")
    print("\n更多帮助请查看: bybit_demo_guide.md")

if __name__ == "__main__":
    main()