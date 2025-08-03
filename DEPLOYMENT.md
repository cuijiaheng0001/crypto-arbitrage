# 日本服务器部署指南

## 📋 部署步骤

### 1. 连接到日本服务器
```bash
ssh root@你的服务器IP
```

### 2. 运行初始化脚本
```bash
# 下载并运行初始化脚本
wget https://raw.githubusercontent.com/cuijiaheng0001/crypto-arbitrage/main/server-init.sh
chmod +x server-init.sh
./server-init.sh
```

### 3. 配置环境变量
```bash
cd ~/crypto-arbitrage
cp .env.example .env
nano .env  # 编辑并填入你的 API 密钥
```

### 4. 部署应用
```bash
./deploy.sh
```

## 🔧 维护命令

### 查看日志
```bash
# 实时查看日志
docker-compose logs -f

# 查看最近100行日志
docker-compose logs --tail=100

# 查看特定服务日志
docker-compose logs -f crypto-arbitrage
```

### 服务管理
```bash
# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 查看服务状态
docker-compose ps

# 更新并重新部署
git pull && ./deploy.sh
```

### 监控
```bash
# 查看监控日志
tail -f /var/log/crypto-arbitrage-monitor.log

# 手动运行监控脚本
./monitor.sh

# 查看 cron 任务
crontab -l
```

## 🔒 安全建议

1. **使用防火墙**
   - 只开放必要端口（SSH）
   - 使用 fail2ban 防止暴力破解

2. **API 密钥安全**
   - 只给 API 密钥交易权限，不要开启提现权限
   - 定期更换 API 密钥
   - 使用 IP 白名单（如果交易所支持）

3. **服务器安全**
   - 定期更新系统
   - 使用 SSH 密钥登录
   - 禁用 root 密码登录

## 🚨 故障排除

### 容器无法启动
```bash
# 查看详细错误
docker-compose logs crypto-arbitrage

# 检查环境变量
docker-compose config
```

### 网络连接问题
```bash
# 测试到交易所的连接
curl -I https://api.binance.com
curl -I https://api.bybit.com

# 检查 DNS
nslookup api.binance.com
```

### 性能问题
```bash
# 查看资源使用
docker stats

# 查看系统资源
htop

# 清理 Docker
docker system prune -a
```

## 📊 监控集成

### Telegram 通知设置
1. 创建 Telegram Bot（通过 @BotFather）
2. 获取 Bot Token
3. 获取你的 Chat ID
4. 编辑 `monitor.sh` 填入 Token 和 Chat ID

### 日志分析
```bash
# 查看错误日志
grep ERROR logs/*.log

# 统计套利机会
grep "套利机会" logs/*.log | wc -l

# 查看最近的套利机会
grep "套利机会" logs/*.log | tail -20
```

## 🔄 更新流程

1. 备份当前配置
```bash
cp .env .env.backup
```

2. 拉取最新代码
```bash
git pull origin main
```

3. 重新构建和部署
```bash
docker-compose build
docker-compose up -d
```

4. 验证服务正常
```bash
docker-compose ps
docker-compose logs --tail=50
```