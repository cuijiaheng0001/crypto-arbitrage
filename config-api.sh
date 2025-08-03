#!/bin/bash

echo "📝 配置 API 密钥"
echo "请在文本编辑器中准备好您的 API 密钥，然后复制粘贴"
echo ""

# 创建新的 .env 文件
cat > .env << 'EOF'
# 交易所API配置
# Binance
EOF

echo -n "请粘贴 Binance API Key: "
read BINANCE_API_KEY
echo "BINANCE_API_KEY=$BINANCE_API_KEY" >> .env

echo -n "请粘贴 Binance Secret Key: "
read BINANCE_SECRET_KEY
echo "BINANCE_SECRET_KEY=$BINANCE_SECRET_KEY" >> .env

cat >> .env << 'EOF'
BINANCE_TESTNET=true  # 使用测试网

# Bybit (或其他第二个交易所)
EOF

echo -n "请粘贴 Bybit API Key (如果没有按回车跳过): "
read BYBIT_API_KEY
echo "BYBIT_API_KEY=$BYBIT_API_KEY" >> .env

echo -n "请粘贴 Bybit Secret Key (如果没有按回车跳过): "
read BYBIT_SECRET_KEY
echo "BYBIT_SECRET_KEY=$BYBIT_SECRET_KEY" >> .env

cat >> .env << 'EOF'
BYBIT_TESTNET=true  # 使用测试网

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

chmod 600 .env
echo ""
echo "✅ 配置完成！"
echo "📄 配置已保存到 .env 文件"