#!/bin/bash

# Bitget API 配置脚本
# 安全地设置您的 Bitget API 密钥

echo "🔐 Bitget API 配置脚本"
echo "======================="
echo ""

# 检查 .env 文件是否存在
if [ ! -f ".env" ]; then
    echo "❌ 错误：未找到 .env 文件"
    echo "请确保您在 /root/crypto-arbitrage 目录下运行此脚本"
    exit 1
fi

echo "请输入您的 Bitget API 信息："
echo "（可以从 Bitget 网站的 API 管理页面获取）"
echo ""

# 获取 API Key
read -p "API Key: " api_key
if [ -z "$api_key" ]; then
    echo "❌ API Key 不能为空"
    exit 1
fi

# 获取 Secret Key (允许粘贴)
read -p "Secret Key: " api_secret
if [ -z "$api_secret" ]; then
    echo "❌ Secret Key 不能为空"
    exit 1
fi

# 获取 Passphrase (允许粘贴)
read -p "Passphrase: " passphrase
if [ -z "$passphrase" ]; then
    echo "❌ Passphrase 不能为空"
    exit 1
fi

echo ""
echo "📝 正在更新配置文件..."

# 备份原文件
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)

# 更新 Bitget 配置
sed -i "s/^BITGET_API_KEY=.*/BITGET_API_KEY=$api_key/" .env
sed -i "s/^BITGET_API_SECRET=.*/BITGET_API_SECRET=$api_secret/" .env
sed -i "s/^BITGET_PASSPHRASE=.*/BITGET_PASSPHRASE=$passphrase/" .env

echo "✅ Bitget API 配置已更新！"
echo ""

# 验证配置
echo "📋 验证配置（隐藏敏感信息）："
echo "-------------------------------"

# 显示配置状态（隐藏敏感部分）
api_key_masked="***${api_key: -4}"
secret_masked="***${api_secret: -4}"

echo "✅ API Key: $api_key_masked"
echo "✅ Secret Key: $secret_masked"
echo "✅ Passphrase: 已设置"
echo ""

# 询问是否测试 API
echo "🔧 下一步操作："
echo "1. 测试 API 连接：python3 test_bitget_api.py"
echo "2. 查看完整配置：cat .env"
echo "3. 开始套利测试"
echo ""

read -p "是否现在测试 Bitget API 连接？(y/n): " test_api

if [[ $test_api =~ ^[Yy]$ ]]; then
    echo ""
    echo "🚀 测试 Bitget API..."
    python3 test_bitget_api.py
else
    echo ""
    echo "💡 稍后可以运行以下命令测试："
    echo "   python3 test_bitget_api.py"
fi

echo ""
echo "🎉 配置完成！"