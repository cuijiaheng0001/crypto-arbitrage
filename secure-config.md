# 安全配置指南

## 1. 权限设置（已完成）
- `.env` 文件权限已设置为 600（仅 root 可读写）

## 2. 最佳实践

### 使用 API 密钥时的安全建议：
1. **创建专用 API 密钥**
   - 仅授予必要的权限（交易、读取）
   - 不要授予提现权限
   - 设置 IP 白名单（添加服务器 IP）

2. **使用测试网**
   - 先在测试网验证功能
   - 确认一切正常后再切换到主网

3. **定期轮换密钥**
   - 每 30-60 天更换一次 API 密钥
   - 保留密钥更换记录

## 3. 交易所 API 设置

### Binance:
1. 登录 Binance
2. 前往 API Management
3. 创建新 API
4. 设置 IP 限制为服务器 IP
5. 仅勾选 "Enable Reading" 和 "Enable Spot Trading"

### Bybit:
1. 登录 Bybit
2. 前往 API 管理
3. 创建新 API 密钥
4. 设置 IP 白名单
5. 仅启用现货交易权限

## 4. 额外安全措施

### 使用 Docker Secrets（可选）
```bash
# 创建 secrets
echo "your_api_key" | docker secret create binance_api_key -
echo "your_secret_key" | docker secret create binance_secret_key -
```

### 使用系统环境变量（可选）
```bash
# 在 /etc/environment 中设置
export BINANCE_API_KEY="your_key"
export BINANCE_SECRET_KEY="your_secret"
```

## 5. 监控和告警
- 定期检查 API 使用情况
- 设置异常交易告警
- 监控服务器访问日志