#!/bin/bash
# 服务器初始化脚本

# 更新系统
apt update && apt upgrade -y

# 安装基础软件
apt install -y python3 python3-pip python3-venv git curl wget htop

# 安装常用Python库
pip3 install requests pandas numpy ccxt python-dotenv

# 创建项目目录
mkdir -p /root/crypto-arbitrage
cd /root/crypto-arbitrage

# 设置防火墙
ufw allow ssh
ufw --force enable

echo "服务器初始化完成！"