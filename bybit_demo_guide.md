# Bybit Demo Trading API 配置指南

## 方法 1: 直接访问 Demo Trading (推荐)

### 步骤：
1. **访问 Demo Trading 页面**
   - 直接访问：https://demo.bybit.com/
   - 或在主站右上角找到 "Demo" 或 "Demo Trading" 入口

2. **登录后查找 API 管理**
   - 登录后，查找个人资料/头像区域
   - 点击 "API" 或 "API Management" 
   - 可能位置：头像菜单、设置页面、或导航栏

3. **创建 API Key**
   - 点击 "Create API Key" 或 "新建 API"
   - 选择权限：只勾选 Read + Trade
   - 添加 IP 白名单（您的 VPS IP）

## 方法 2: 使用现有的 Testnet 环境

如果 Demo Trading API 暂时无法访问，我们可以使用 Bybit Testnet：

### Testnet 配置：
```python
# Testnet URL (替代方案)
BYBIT_TESTNET_URL = "https://api-testnet.bybit.com"
BYBIT_TESTNET_WS = "wss://stream-testnet.bybit.com"
```

## 方法 3: 其他交易所 Demo 环境

### KuCoin Sandbox (免 KYC)
- 注册：https://sandbox.kucoin.com
- API URL: https://api-sandbox.kucoin.com
- 特点：邮箱注册即可，无需护照

### Binance Spot Testnet
- API URL: https://testnet.binance.vision
- 特点：免 KYC，支持现货交易测试

## 快速测试脚本

我已为您准备了一个测试脚本，可以测试多个环境：
```bash
cd /root/crypto-arbitrage
python3 test_multiple_exchanges.py
```

## 如果仍找不到 Demo API 入口

1. **联系 Bybit 客服**
   - 询问如何开启 Demo Trading API 权限
   
2. **使用小额真实交易**
   - 在主网用最小金额（5-10 USDT）测试
   - 确保策略可行后再增加资金

3. **等待界面更新**
   - Bybit 可能正在更新 Demo 界面
   - 稍后再试

## 当前推荐配置

基于实际情况，建议先用以下组合测试：

1. **Binance Spot Testnet** (现货套利)
2. **Bybit Testnet** (期货套利) 
3. **KuCoin Sandbox** (备用)

这样可以完整测试跨交易所套利策略。