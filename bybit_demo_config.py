#!/usr/bin/env python3
"""
Bybit Demo Trading API Configuration
使用最新的 v5 API 端点
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# Bybit Demo API 端点
BYBIT_DEMO_REST_URL = "https://api-demo.bybit.com"
BYBIT_DEMO_WS_URL = "wss://stream-demo.bybit.com"

# API 认证信息（从环境变量读取）
API_KEY = os.getenv("BYBIT_DEMO_API_KEY", "")
API_SECRET = os.getenv("BYBIT_DEMO_API_SECRET", "")

# 交易参数
DEFAULT_SYMBOL = "BTCUSDT"
DEFAULT_CATEGORY = "linear"  # linear, inverse, spot, option

# API 请求超时设置
REQUEST_TIMEOUT = 10

# WebSocket 参数
WS_PING_INTERVAL = 30
WS_PING_TIMEOUT = 10

# 风险管理参数
MAX_POSITION_SIZE = 0.1  # BTC
MAX_ORDER_SIZE = 0.01    # BTC
STOP_LOSS_PERCENTAGE = 0.02  # 2%

# 日志配置
LOG_LEVEL = "INFO"
LOG_FILE = "logs/bybit_demo.log"

# Demo 账户特殊配置
DEMO_FUNDS_REQUEST_AMOUNT = 100000  # USDT

def get_headers():
    """获取 API 请求头"""
    return {
        "Content-Type": "application/json",
        "X-BAPI-API-KEY": API_KEY,
    }

def print_config():
    """打印当前配置（隐藏敏感信息）"""
    print(f"Bybit Demo Configuration:")
    print(f"- REST URL: {BYBIT_DEMO_REST_URL}")
    print(f"- WebSocket URL: {BYBIT_DEMO_WS_URL}")
    print(f"- API Key: {'*' * 10 + API_KEY[-4:] if API_KEY else 'Not Set'}")
    print(f"- Default Symbol: {DEFAULT_SYMBOL}")
    print(f"- Default Category: {DEFAULT_CATEGORY}")

if __name__ == "__main__":
    print_config()