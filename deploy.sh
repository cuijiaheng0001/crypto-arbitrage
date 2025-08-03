#!/bin/bash

# 部署脚本 - 在日本服务器上运行

echo "🚀 开始部署 Crypto Arbitrage Bot..."

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检查是否安装了必要的工具
check_requirements() {
    echo "📋 检查系统要求..."
    
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker 未安装${NC}"
        echo "请先安装 Docker: curl -fsSL https://get.docker.com | sh"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}❌ Docker Compose 未安装${NC}"
        echo "请先安装 Docker Compose"
        exit 1
    fi
    
    echo -e "${GREEN}✓ 系统要求检查通过${NC}"
}

# 拉取最新代码
update_code() {
    echo "📦 更新代码..."
    git pull origin main
    echo -e "${GREEN}✓ 代码更新完成${NC}"
}

# 检查环境变量
check_env() {
    echo "🔐 检查环境变量..."
    if [ ! -f .env ]; then
        echo -e "${RED}❌ .env 文件不存在${NC}"
        echo "请创建 .env 文件并配置 API 密钥"
        exit 1
    fi
    echo -e "${GREEN}✓ 环境变量检查通过${NC}"
}

# 构建并启动容器
deploy() {
    echo "🏗️  构建 Docker 镜像..."
    docker-compose build
    
    echo "🚀 启动服务..."
    docker-compose up -d
    
    echo -e "${GREEN}✓ 部署完成！${NC}"
}

# 显示服务状态
show_status() {
    echo "📊 服务状态："
    docker-compose ps
    
    echo -e "\n📝 查看日志："
    echo "docker-compose logs -f crypto-arbitrage"
}

# 主流程
main() {
    check_requirements
    update_code
    check_env
    deploy
    show_status
    
    echo -e "\n${GREEN}🎉 部署成功完成！${NC}"
    echo "常用命令："
    echo "  查看日志: docker-compose logs -f"
    echo "  停止服务: docker-compose down"
    echo "  重启服务: docker-compose restart"
    echo "  查看状态: docker-compose ps"
}

# 运行主流程
main