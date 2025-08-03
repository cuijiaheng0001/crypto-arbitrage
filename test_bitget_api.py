#!/usr/bin/env python3
"""
Bitget API 测试脚本
测试 Bitget 主网和模拟交易环境
"""

import time
import hmac
import hashlib
import base64
import requests
import json
import os
from urllib.parse import urlencode
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class BitgetAPITester:
    def __init__(self):
        # Bitget API 端点
        self.base_url = "https://api.bitget.com"
        self.results = {}
        
        # API 认证信息（从环境变量读取）
        self.api_key = os.getenv("BITGET_API_KEY", "")
        self.api_secret = os.getenv("BITGET_API_SECRET", "")
        self.passphrase = os.getenv("BITGET_PASSPHRASE", "")
    
    def generate_signature(self, timestamp, method, request_path, body=""):
        """生成 Bitget API 签名"""
        if body:
            body = json.dumps(body)
        
        message = timestamp + method.upper() + request_path + body
        signature = base64.b64encode(
            hmac.new(
                self.api_secret.encode('utf-8'),
                message.encode('utf-8'),
                hashlib.sha256
            ).digest()
        ).decode('utf-8')
        
        return signature
    
    def get_headers(self, timestamp, method, request_path, body=""):
        """获取请求头"""
        signature = self.generate_signature(timestamp, method, request_path, body)
        
        return {
            "Content-Type": "application/json",
            "ACCESS-KEY": self.api_key,
            "ACCESS-SIGN": signature,
            "ACCESS-TIMESTAMP": timestamp,
            "ACCESS-PASSPHRASE": self.passphrase,
            "locale": "en-US"
        }
    
    def test_public_endpoints(self):
        """测试公共端点（无需API密钥）"""
        print("🔍 测试 Bitget 公共 API...")
        
        # 测试现货市场数据
        try:
            url = f"{self.base_url}/api/spot/v1/market/tickers"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == '00000':
                    # 查找 BTCUSDT
                    btc_data = None
                    for ticker in data.get('data', []):
                        if ticker.get('symbol') == 'BTCUSDT':
                            btc_data = ticker
                            break
                    
                    if btc_data:
                        self.results['spot_public'] = {
                            'status': '✅ 可用',
                            'btc_price': f"{btc_data.get('close', 'N/A')} USDT",
                            'product': 'Spot 现货'
                        }
                    else:
                        self.results['spot_public'] = {
                            'status': '✅ API 可用',
                            'note': '未找到 BTCUSDT 交易对'
                        }
                else:
                    self.results['spot_public'] = {
                        'status': '❌ API 错误',
                        'error': data.get('msg', 'Unknown error')
                    }
            else:
                self.results['spot_public'] = {
                    'status': f'❌ HTTP {response.status_code}',
                    'error': response.text[:100]
                }
        except Exception as e:
            self.results['spot_public'] = {
                'status': '❌ 连接失败',
                'error': str(e)
            }
        
        # 测试合约市场数据
        try:
            url = f"{self.base_url}/api/mix/v1/market/tickers"
            params = {"productType": "umcbl"}  # USDT合约
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == '00000':
                    # 查找 BTCUSDT
                    btc_data = None
                    for ticker in data.get('data', []):
                        if ticker.get('symbol') == 'BTCUSDT_UMCBL':
                            btc_data = ticker
                            break
                    
                    if btc_data:
                        self.results['futures_public'] = {
                            'status': '✅ 可用',
                            'btc_price': f"{btc_data.get('last', 'N/A')} USDT",
                            'product': 'USDT Futures 合约'
                        }
                    else:
                        self.results['futures_public'] = {
                            'status': '✅ API 可用',
                            'note': '未找到 BTCUSDT 合约'
                        }
                else:
                    self.results['futures_public'] = {
                        'status': '❌ API 错误',
                        'error': data.get('msg', 'Unknown error')
                    }
            else:
                self.results['futures_public'] = {
                    'status': f'❌ HTTP {response.status_code}',
                    'error': response.text[:100]
                }
        except Exception as e:
            self.results['futures_public'] = {
                'status': '❌ 连接失败',
                'error': str(e)
            }
    
    def test_demo_trading(self):
        """测试模拟交易功能"""
        print("🔍 测试 Bitget 模拟交易...")
        
        if not self.api_key:
            self.results['demo_trading'] = {
                'status': '⚠️ 未配置',
                'note': '需要 API Key 才能测试模拟交易'
            }
            return
        
        try:
            # 测试模拟交易账户信息
            timestamp = str(int(time.time() * 1000))
            request_path = "/api/spot/v1/account/assets"
            
            # 添加模拟交易参数
            params = {"coin": "USDT"}
            if params:
                request_path += "?" + urlencode(params)
            
            headers = self.get_headers(timestamp, "GET", request_path)
            
            response = requests.get(
                f"{self.base_url}{request_path}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == '00000':
                    self.results['demo_trading'] = {
                        'status': '✅ 可用',
                        'note': 'API 认证成功，可以进行模拟交易'
                    }
                else:
                    self.results['demo_trading'] = {
                        'status': '❌ 认证失败',
                        'error': data.get('msg', 'Unknown error')
                    }
            else:
                self.results['demo_trading'] = {
                    'status': f'❌ HTTP {response.status_code}',
                    'error': response.text[:100]
                }
        except Exception as e:
            self.results['demo_trading'] = {
                'status': '❌ 连接失败',
                'error': str(e)
            }
    
    def run_tests(self):
        """运行所有测试"""
        print("=" * 60)
        print("🚀 Bitget API 环境测试")
        print("=" * 60)
        print()
        
        # 测试公共端点
        self.test_public_endpoints()
        
        # 测试模拟交易
        self.test_demo_trading()
        
        # 显示结果
        print("\n" + "=" * 60)
        print("📊 测试结果汇总")
        print("=" * 60)
        
        for endpoint, result in self.results.items():
            print(f"\n📈 {endpoint.upper().replace('_', ' ')}")
            print(f"   状态: {result['status']}")
            
            if 'btc_price' in result:
                print(f"   BTC价格: {result['btc_price']}")
            
            if 'product' in result:
                print(f"   产品类型: {result['product']}")
            
            if 'note' in result:
                print(f"   说明: {result['note']}")
            
            if 'error' in result:
                print(f"   错误: {result['error']}")
        
        # 配置建议
        print(f"\n" + "=" * 60)
        print("💡 配置建议")
        print("=" * 60)
        
        if any('✅' in v['status'] for v in self.results.values()):
            print("\n✅ Bitget API 基础功能正常")
            
            print(f"\n🔑 获取 API Key 步骤:")
            print("1. 登录 https://www.bitget.com")
            print("2. 进入 API 管理页面")
            print("3. 创建新的 API Key")
            print("4. 权限设置：Read + Trade")
            print("5. 启用模拟交易（如果有此选项）")
            
            print(f"\n🎯 支持的交易类型:")
            if 'spot_public' in self.results and '✅' in self.results['spot_public']['status']:
                print("   ✅ 现货交易")
            if 'futures_public' in self.results and '✅' in self.results['futures_public']['status']:
                print("   ✅ USDT 合约交易")
            
            print(f"\n📝 .env 配置示例:")
            print("BITGET_API_KEY=your_api_key")
            print("BITGET_API_SECRET=your_api_secret")
            print("BITGET_PASSPHRASE=your_passphrase")
            
        else:
            print("\n❌ Bitget API 连接异常，请检查网络或稍后重试")

def main():
    tester = BitgetAPITester()
    
    # 如果有配置，可以在这里设置
    # tester.api_key = "your_api_key"
    # tester.api_secret = "your_api_secret"
    # tester.passphrase = "your_passphrase"
    
    tester.run_tests()
    
    print(f"\n" + "=" * 60)
    print("🔧 下一步操作")
    print("=" * 60)
    print("1. 在 Bitget 网站创建 API Key")
    print("2. 将 API 信息填入 .env 文件")
    print("3. 重新运行此脚本验证认证")
    print("4. 开始套利策略开发")

if __name__ == "__main__":
    main()