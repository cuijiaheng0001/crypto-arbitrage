# Crypto Arbitrage Bot 🚀

虚拟货币跨交易所套利机器人项目

## 项目概述

本项目旨在实现自动化的虚拟货币套利交易，通过监控不同交易所之间的价格差异，自动执行买卖操作获取利润。

## 技术栈

- **语言**: Python 3.8+
- **框架**: CCXT (统一的加密货币交易所API)
- **交易所**: Binance, Bybit/KuCoin
- **服务器**: Vultr VPS (日本大阪)

## 项目结构

```
crypto-arbitrage/
├── barbotine-arbitrage-bot/    # 开源套利机器人框架
├── src/                        # 自定义代码
├── logs/                       # 日志文件
├── data/                       # 数据存储
├── requirements.txt            # Python依赖
├── .env.example               # 环境变量示例
└── README.md                  # 本文件
```

## 快速开始

1. **克隆项目**
   ```bash
   git clone [your-repo-url]
   cd crypto-arbitrage
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **配置环境变量**
   ```bash
   cp .env.example .env
   # 编辑 .env 文件，填入你的API密钥
   ```

4. **运行测试**
   ```bash
   python simple-arbitrage-test.py
   ```

## 安全提醒

- 🔐 永远不要将API密钥提交到Git
- 🔐 使用只有交易权限的API密钥，不要开启提现权限
- 🔐 从小额资金开始测试

## 开发进度

- [x] 项目初始化
- [x] 服务器配置 (Vultr日本)
- [x] 获取交易所API (Binance Testnet + 第二交易所)
- [x] 集成开源套利框架
- [ ] 配置和测试套利逻辑
- [ ] 实盘小额测试
- [ ] 策略优化

## 贡献

本项目仅供学习和研究使用。请谨慎使用，风险自负。

## 许可证

MIT License