# KuCoin API 设置指南（无需KYC）

## 为什么选择 KuCoin？
- 无需身份验证即可交易（每日限额 5 BTC）
- API 功能完整
- 支持现货交易
- 手续费低（0.1%）

## 设置步骤：

1. **注册 KuCoin 账号**
   - 访问：https://www.kucoin.com
   - 使用邮箱注册即可

2. **获取少量 USDT 用于测试**
   - 可以从其他交易所转入小额 USDT（如 $50-100）
   - 或使用 P2P 购买

3. **创建 API Key**
   - 登录后进入：账户 → API 管理
   - 创建新的 API Key
   - 权限设置：
     - ✅ General（通用）
     - ✅ Trade（交易）
     - ❌ Transfer（转账）- 不要开启
   - 设置交易密码（Passphrase）

4. **配置套利机器人**
   ```python
   exchanges = {
       'binance': {
           # Binance Testnet 配置
       },
       'kucoin': {
           'apiKey': 'your-kucoin-api-key',
           'secret': 'your-kucoin-secret',
           'password': 'your-passphrase',  # KuCoin 需要 passphrase
       }
   }
   ```

## 安全建议：
- 只放入测试所需的最小金额
- API 不开启提现权限
- 设置 IP 白名单（可选）