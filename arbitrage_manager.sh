#!/bin/bash

# 套利系统管理器

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🚀 高级套利系统管理器${NC}"
echo "================================"
echo ""

show_menu() {
    echo "1) 启动监控仪表板"
    echo "2) 启动超高速WebSocket套利"
    echo "3) 启动三角套利"
    echo "4) 启动资金费率套利"
    echo "5) 启动所有策略"
    echo "6) 查看运行状态"
    echo "7) 查看性能报告"
    echo "8) 停止所有策略"
    echo "9) 退出"
    echo ""
}

start_dashboard() {
    echo -e "${GREEN}启动监控仪表板...${NC}"
    python3 dashboard.py
}

start_websocket() {
    echo -e "${GREEN}启动超高速WebSocket套利...${NC}"
    nohup python3 ultra_fast_arbitrage.py > logs/ultra_fast.log 2>&1 &
    echo -e "${GREEN}✓ WebSocket套利已启动 (PID: $!)${NC}"
}

start_triangular() {
    echo -e "${GREEN}启动三角套利...${NC}"
    nohup python3 enhanced_triangular_arbitrage.py > logs/triangular.log 2>&1 &
    echo -e "${GREEN}✓ 三角套利已启动 (PID: $!)${NC}"
}

start_funding() {
    echo -e "${GREEN}启动资金费率套利...${NC}"
    nohup python3 funding_rate_arbitrage.py > logs/funding.log 2>&1 &
    echo -e "${GREEN}✓ 资金费率套利已启动 (PID: $!)${NC}"
}

start_all() {
    echo -e "${GREEN}启动所有策略...${NC}"
    start_websocket
    sleep 1
    start_triangular
    sleep 1
    start_funding
    echo -e "${GREEN}✓ 所有策略已启动${NC}"
}

show_status() {
    echo -e "${YELLOW}运行中的套利策略:${NC}"
    echo "================================"
    ps aux | grep -E "(arbitrage|bot)" | grep -v grep | grep -v manager
}

show_performance() {
    echo -e "${YELLOW}性能报告:${NC}"
    echo "================================"
    
    # 显示最新的日志条目
    echo -e "\n${GREEN}最近的套利机会:${NC}"
    grep -h "发现.*机会" logs/*.log 2>/dev/null | tail -5
    
    echo -e "\n${GREEN}最近的执行:${NC}"
    grep -h "执行.*成功" logs/*.log 2>/dev/null | tail -5
    
    # 统计今日数据
    TODAY=$(date +%Y-%m-%d)
    echo -e "\n${GREEN}今日统计:${NC}"
    echo -n "机会总数: "
    grep -h "$TODAY.*发现.*机会" logs/*.log 2>/dev/null | wc -l
    echo -n "执行总数: "
    grep -h "$TODAY.*执行.*成功" logs/*.log 2>/dev/null | wc -l
}

stop_all() {
    echo -e "${RED}停止所有策略...${NC}"
    pkill -f "arbitrage"
    pkill -f "bot.py"
    echo -e "${GREEN}✓ 所有策略已停止${NC}"
}

# 主循环
while true; do
    show_menu
    read -p "请选择操作 (1-9): " choice
    
    case $choice in
        1) start_dashboard ;;
        2) start_websocket ;;
        3) start_triangular ;;
        4) start_funding ;;
        5) start_all ;;
        6) show_status ;;
        7) show_performance ;;
        8) stop_all ;;
        9) echo "退出管理器"; exit 0 ;;
        *) echo -e "${RED}无效选项${NC}" ;;
    esac
    
    echo ""
    read -p "按回车继续..."
    clear
done