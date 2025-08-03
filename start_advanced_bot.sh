#!/bin/bash

echo "🚀 高级套利机器人启动器"
echo "========================"
echo ""
echo "请选择要启动的套利策略："
echo ""
echo "1) 跨交易所价差套利 (当前运行中)"
echo "2) 三角套利 (单交易所内)"
echo "3) 资金费率套利 (现货+合约)"
echo "4) 查看所有运行中的机器人"
echo "5) 停止所有机器人"
echo ""

read -p "请输入选项 (1-5): " choice

case $choice in
    1)
        echo "✅ 跨交易所套利已在运行 (PID: $(pgrep -f telegram_arbitrage_bot.py))"
        ;;
    2)
        echo "🔺 启动三角套利机器人..."
        nohup python3 enhanced_triangular_arbitrage.py > logs/triangular.log 2>&1 &
        echo "✅ 三角套利机器人已启动 (PID: $!)"
        ;;
    3)
        echo "💰 启动资金费率套利机器人..."
        nohup python3 funding_rate_arbitrage.py > logs/funding.log 2>&1 &
        echo "✅ 资金费率套利机器人已启动 (PID: $!)"
        ;;
    4)
        echo "📊 运行中的机器人："
        echo ""
        ps aux | grep -E "(arbitrage|bot)" | grep -v grep
        ;;
    5)
        echo "🛑 停止所有机器人..."
        pkill -f "arbitrage"
        pkill -f "bot.py"
        echo "✅ 所有机器人已停止"
        ;;
    *)
        echo "❌ 无效选项"
        ;;
esac