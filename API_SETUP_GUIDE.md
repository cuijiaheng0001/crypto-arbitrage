# API 密钥设置指南

## 当前错误诊断

### Binance: "Invalid Api-Key ID"
- 您提供的 API Key 格式可能不正确
- 请确保从 Binance 复制的是完整的 API Key

### Bybit: "API key is invalid"
- API Key 格式不正确或权限设置有误

## 正确设置 API 密钥的步骤

### 1. Binance API 设置

1. 登录 [Binance](https://www.binance.com)
2. 前往 **账户设置** → **API 管理**
3. 创建新 API:
   - 标签：Arbitrage Bot
   - 权限：
     - ✅ 启用读取
     - ✅ 启用现货交易
     - ❌ 不要启用提现
   - IP 限制：添加 `64.176.48.97`

4. 复制 API Key 和 Secret Key

### 2. Bybit API 设置

1. 登录 [Bybit](https://www.bybit.com)
2. 前往 **账户和安全** → **API 管理**
3. 创建新 API Key:
   - 名称：Arbitrage Bot
   - 权限：
     - ✅ 读取
     - ✅ 现货交易
     - ❌ 不要启用提现
   - IP 白名单：`64.176.48.97`

4. 复制 API Key 和 Secret

### 3. 验证 API 密钥

运行以下脚本验证您的密钥：

```bash
cd /root/crypto-arbitrage
python3 test_api_connection.py
```

### 4. 使用公共 API 测试

如果暂时无法获取有效的 API 密钥，可以先使用公共 API 监控套利机会：

```bash
# 运行公共 API 监控器
python3 simple_arbitrage_monitor.py
```

这将显示实时价格差异，帮助您了解套利机会。

### 5. 常见问题

**Q: 为什么显示 "Invalid Api-Key"？**
A: 可能原因：
- API Key 复制不完整
- 使用了测试网密钥但连接主网
- IP 白名单未设置

**Q: 如何获取测试网 API？**
A: 
- Binance 测试网已停用，建议使用主网小额测试
- Bybit 测试网：https://testnet.bybit.com

**Q: 套利机会多吗？**
A: 主流交易对的价差通常很小（< 0.1%），需要：
- 监控多个交易对
- 快速执行
- 考虑手续费（通常 0.1%）

## 下一步

1. 正确配置 API 密钥后，编辑 .env 文件：
   ```bash
   vim /root/crypto-arbitrage/.env
   ```

2. 重启服务：
   ```bash
   docker-compose restart
   ```

3. 查看日志：
   ```bash
   docker-compose logs -f
   ```