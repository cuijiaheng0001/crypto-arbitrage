#!/bin/bash

# Telegram Bot 配置脚本

echo "📱 Telegram Bot 配置"
echo "===================="
echo ""
echo "🔧 获取 Bot Token 步骤："
echo "1. 在 Telegram 搜索 @BotFather"
echo "2. 发送 /newbot 创建机器人"
echo "3. 复制返回的 Token"
echo ""
echo "🔍 获取 Chat ID 步骤："
echo "1. 向您的 Bot 发送消息"
echo "2. 访问 https://api.telegram.org/bot<TOKEN>/getUpdates"
echo "3. 找到 chat.id 字段"
echo ""

# 获取 Bot Token
read -p "Bot Token: " bot_token
if [ -z "$bot_token" ]; then
    echo "❌ Token 不能为空"
    exit 1
fi

# 获取 Chat ID
read -p "Chat ID: " chat_id
if [ -z "$chat_id" ]; then
    echo "❌ Chat ID 不能为空"
    exit 1
fi

echo ""
echo "📝 更新配置文件..."

# 更新 .env 文件
sed -i "s/^TELEGRAM_BOT_TOKEN=.*/TELEGRAM_BOT_TOKEN=$bot_token/" .env
sed -i "s/^TELEGRAM_CHAT_ID=.*/TELEGRAM_CHAT_ID=$chat_id/" .env
sed -i "s/^TELEGRAM_ENABLED=.*/TELEGRAM_ENABLED=true/" .env

echo "✅ Telegram 配置已更新！"
echo ""

# 测试发送消息
echo "🔍 测试 Telegram 连接..."

# 发送测试消息
curl -s -X POST "https://api.telegram.org/bot$bot_token/sendMessage" \
    -d "chat_id=$chat_id" \
    -d "text=🎉 套利机器人 Telegram 通知已配置成功！" > /dev/null

if [ $? -eq 0 ]; then
    echo "✅ 测试消息已发送！"
    echo "📱 请检查您的 Telegram"
else
    echo "❌ 消息发送失败"
    echo "请检查 Token 和 Chat ID 是否正确"
fi

echo ""
echo "🎯 配置完成！重启机器人即可使用通知功能。"