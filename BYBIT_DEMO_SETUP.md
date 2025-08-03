# Bybit Demo Trading 设置指南

## 问题诊断

您当前的 Bybit API 密钥显示 "Invalid ApiKey"，这通常意味着：
1. 使用的是主网 API 密钥而不是 Demo API 密钥
2. Demo 账户未激活
3. API 密钥权限设置不正确

## 正确设置步骤

### 1. 创建 Bybit Demo 账户

1. 访问 **https://demo.bybit.com**（注意是 demo 子域名）
2. 注册或登录 Demo 账户
3. **重要**：至少登录一次 Demo Trading UI 来激活账户

### 2. 创建 Demo API 密钥

1. 在 Demo 账户中，前往 **API Management**
2. 创建新的 API Key，注意：
   - ✅ 勾选 **Unified Trading Account**
   - ✅ 勾选 **Spot Trading**
   - ✅ 勾选 **Read** 权限
   - ❌ 不要勾选 Withdrawal（提现）
   - IP 限制：可选（建议添加服务器 IP: 64.176.48.97）

### 3. 测试 Demo API

创建密钥后，使用以下脚本测试：

```python
import ccxt

# 配置 Bybit Demo
exchange = ccxt.bybit({
    'apiKey': 'YOUR_DEMO_API_KEY',
    'secret': 'YOUR_DEMO_SECRET',
    'options': {
        'defaultType': 'spot',
    },
    'urls': {
        'api': 'https://api-demo.bybit.com'
    }
})

# 测试
try:
    balance = exchange.fetch_balance()
    print("✅ Demo API 连接成功!")
    print(f"USDT 余额: {balance['USDT']['total']}")
except Exception as e:
    print(f"❌ 错误: {e}")
```

## Demo vs 主网的区别

| 特性 | Demo Trading | 主网 |
|------|-------------|------|
| API 域名 | api-demo.bybit.com | api.bybit.com |
| API 密钥 | Demo 专用 | 主网专用 |
| 资金 | 虚拟资金（100,000 USDT） | 真实资金 |
| 交易对 | 有限（主流币种） | 全部 |
| 费率 | 0% | 真实费率 |

## 常见错误和解决方案

### 错误: "Invalid ApiKey"
- **原因**：使用了主网密钥
- **解决**：在 demo.bybit.com 创建新的 Demo API

### 错误: "Permission Denied"
- **原因**：Demo 账户未激活或权限不足
- **解决**：登录 Demo UI 并确保 API 有 Unified Trading 权限

### 错误: "Timestamp error"
- **原因**：服务器时间不同步
- **解决**：同步服务器时间或增加 recvWindow

## 测试 Demo 余额

Demo 账户默认有 100,000 USDT 虚拟资金。如果余额为 0：
1. 登录 https://demo.bybit.com
2. 在资产页面点击 "Reset Demo Balance"
3. 系统会重置为初始资金

## 下一步

1. 获取正确的 Demo API 密钥
2. 更新 .env 文件中的 BYBIT_API_KEY 和 BYBIT_SECRET_KEY
3. 运行测试脚本验证连接
4. 开始测试套利策略

记住：Demo Trading 是完全免费的，可以无限测试，非常适合验证套利策略！