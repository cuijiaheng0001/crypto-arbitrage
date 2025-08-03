#!/bin/bash

# 服务器初始化脚本 - 在新的日本服务器上运行

echo "🔧 初始化日本服务器环境..."

# 更新系统
echo "📦 更新系统包..."
sudo apt-get update && sudo apt-get upgrade -y

# 安装基础工具
echo "🛠️  安装基础工具..."
sudo apt-get install -y \
    git \
    curl \
    wget \
    htop \
    vim \
    tmux \
    build-essential \
    software-properties-common

# 安装 Docker
echo "🐳 安装 Docker..."
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# 安装 Docker Compose
echo "🐳 安装 Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 配置防火墙
echo "🔥 配置防火墙..."
sudo ufw allow 22/tcp  # SSH
sudo ufw allow 8080/tcp  # 监控端口（如果需要）
sudo ufw --force enable

# 设置时区
echo "🕐 设置时区为东京..."
sudo timedatectl set-timezone Asia/Tokyo

# 克隆项目
echo "📂 克隆项目..."
cd ~
git clone https://github.com/cuijiaheng0001/crypto-arbitrage.git
cd crypto-arbitrage

# 创建必要的目录
echo "📁 创建目录..."
mkdir -p logs data

# 设置 cron 任务
echo "⏰ 设置监控定时任务..."
chmod +x monitor.sh
chmod +x deploy.sh

# 添加 cron 任务（每5分钟检查一次）
(crontab -l 2>/dev/null; echo "*/5 * * * * /root/crypto-arbitrage/monitor.sh") | crontab -

# 配置日志轮转
echo "📝 配置日志轮转..."
sudo cat > /etc/logrotate.d/crypto-arbitrage << EOF
/root/crypto-arbitrage/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 root root
}
EOF

echo "✅ 服务器初始化完成！"
echo ""
echo "下一步："
echo "1. 编辑 .env 文件，添加你的 API 密钥"
echo "2. 运行 ./deploy.sh 部署应用"
echo "3. 使用 docker-compose logs -f 查看日志"