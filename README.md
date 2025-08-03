# Crypto Arbitrage Bot 🚀

高性能加密货币套利交易系统，支持多种套利策略和实时监控。

## 功能特性

### 套利策略
- **跨交易所套利**: 利用不同交易所之间的价差
- **三角套利**: 单交易所内多币种循环套利
- **资金费率套利**: 现货与合约之间的资金费率套利
- **WebSocket 高速套利**: 毫秒级延迟的实时套利

### 技术特性
- ⚡ **超低延迟**: WebSocket 实时数据流，毫秒级响应
- 🛡️ **风险管理**: 完整的风控系统，自动止损止盈
- 📊 **数据分析**: 智能分析最佳交易时段和盈利模式
- 📱 **实时通知**: Telegram 机器人推送交易信号
- 📈 **监控仪表板**: 实时查看所有策略运行状态

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API

```bash
# 配置 Bitget API
./config-bitget.sh

# 配置 Telegram 通知
./config-telegram.sh
```

### 3. 启动套利系统

```bash
# 使用管理器启动
./arbitrage_manager.sh

# 或单独启动某个策略
python3 telegram_arbitrage_bot.py  # 跨交易所套利
python3 enhanced_triangular_arbitrage.py  # 三角套利
python3 funding_rate_arbitrage.py  # 资金费率套利
```

### 4. 监控运行状态

```bash
# 启动实时监控仪表板
python3 dashboard.py
```

## 配置说明

### 环境变量 (.env)

```env
# Bitget API 配置
BITGET_API_KEY=your_api_key
BITGET_API_SECRET=your_api_secret
BITGET_PASSPHRASE=your_passphrase

# Telegram 配置
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
TELEGRAM_ENABLED=true

# 交易参数
MIN_PROFIT_PERCENTAGE=0.1
MAX_TRADE_AMOUNT=100
PRICE_UPDATE_INTERVAL=5
```

## 项目结构

```
crypto-arbitrage/
├── arbitrage_manager.sh      # 统一管理脚本
├── dashboard.py              # 监控仪表板
├── telegram_arbitrage_bot.py # 跨交易所套利
├── enhanced_triangular_arbitrage.py  # 三角套利
├── funding_rate_arbitrage.py # 资金费率套利
├── ultra_fast_arbitrage.py   # 超高速执行系统
├── websocket_arbitrage_bot.py # WebSocket 套利
├── config/                   # 配置脚本
├── logs/                     # 日志文件
├── data/                     # 数据存储
└── src/                      # 核心模块
```

## 风险提示

⚠️ **重要提示**：
- 加密货币交易具有高风险，可能导致资金损失
- 请先在模拟环境测试，确认稳定后再使用真实资金
- 建议从小额开始，逐步增加交易规模
- 定期检查和更新风控参数

## 性能优化

- 使用 WebSocket 替代 REST API 降低延迟
- 异步并发处理多个数据流
- 内存优化的数据结构
- 智能参数自动优化

## 开发计划

- [ ] 支持更多交易所 (Binance, OKX)
- [ ] 机器学习价格预测
- [ ] 动态仓位管理 (Kelly 公式)
- [ ] Web UI 界面
- [ ] 回测系统

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License