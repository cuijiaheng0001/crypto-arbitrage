#!/bin/bash

# 安全配置环境变量脚本
echo "🔐 安全配置 API 密钥..."

# 读取敏感信息（不会显示在屏幕上）
read -sp "请输入 Binance API Key: " BINANCE_API_KEY
echo
read -sp "请输入 Binance Secret Key: " BINANCE_SECRET_KEY
echo
read -sp "请输入第二个交易所 API Key: " EXCHANGE2_API_KEY
echo
read -sp "请输入第二个交易所 Secret Key: " EXCHANGE2_SECRET_KEY
echo

# 创建 .env 文件
cat > .env << EOF
# 交易所API配置
# Binance
BINANCE_API_KEY=$BINANCE_API_KEY
BINANCE_SECRET_KEY=$BINANCE_SECRET_KEY
BINANCE_TESTNET=true  # 使用测试网

# KuCoin (或其他第二个交易所)
KUCOIN_API_KEY=$EXCHANGE2_API_KEY
KUCOIN_SECRET_KEY=$EXCHANGE2_SECRET_KEY
KUCOIN_PASSPHRASE=your_passphrase_here

# 套利参数
MIN_PROFIT_PERCENTAGE=0.3  # 最小利润率 0.3%
MAX_TRADE_AMOUNT=100       # 单次最大交易金额(USDT)
PRICE_UPDATE_INTERVAL=1    # 价格更新间隔(秒)

# 通知配置（可选）
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=

# 风险控制
DAILY_LOSS_LIMIT=50        # 日亏损限额(USDT)
MAX_OPEN_ORDERS=5          # 最大未完成订单数
EOF

# 设置安全权限
chmod 600 .env

echo "✅ 配置完成！.env 文件已创建并设置了安全权限。"