#!/bin/bash

# 套利机器人启动脚本
# 支持后台运行和日志记录

echo "🚀 套利机器人启动器"
echo "===================="
echo ""
echo "选择运行模式："
echo "1. 前台运行（可以看到实时日志）"
echo "2. 后台运行（使用 nohup）"
echo "3. 后台运行（使用 screen）"
echo "4. 查看运行状态"
echo "5. 停止机器人"
echo ""

read -p "请选择 (1-5): " choice

case $choice in
    1)
        echo "🎯 前台运行模式"
        cd /root/crypto-arbitrage
        python3 telegram_arbitrage_bot.py
        ;;
    
    2)
        echo "🎯 后台运行模式 (nohup)"
        cd /root/crypto-arbitrage
        nohup python3 telegram_arbitrage_bot.py > logs/bot_$(date +%Y%m%d_%H%M%S).log 2>&1 &
        echo "✅ 机器人已在后台启动"
        echo "📋 进程 ID: $!"
        echo "📄 查看日志: tail -f logs/bot_*.log"
        ;;
    
    3)
        echo "🎯 后台运行模式 (screen)"
        # 检查是否安装了 screen
        if ! command -v screen &> /dev/null; then
            echo "📦 安装 screen..."
            apt-get update && apt-get install -y screen
        fi
        
        cd /root/crypto-arbitrage
        screen -dmS arbitrage_bot python3 telegram_arbitrage_bot.py
        echo "✅ 机器人已在 screen 会话中启动"
        echo "📋 查看会话: screen -r arbitrage_bot"
        echo "📋 退出会话: Ctrl+A 然后按 D"
        ;;
    
    4)
        echo "📊 检查运行状态"
        echo ""
        
        # 检查进程
        if pgrep -f "telegram_arbitrage_bot.py" > /dev/null; then
            echo "✅ 机器人正在运行"
            echo ""
            echo "进程信息："
            ps aux | grep -E "telegram_arbitrage_bot|PID" | grep -v grep
        else
            echo "❌ 机器人未运行"
        fi
        
        # 检查 screen 会话
        if command -v screen &> /dev/null; then
            echo ""
            echo "Screen 会话："
            screen -ls | grep arbitrage_bot || echo "没有找到 screen 会话"
        fi
        
        # 显示最新日志
        echo ""
        echo "最新日志："
        if ls logs/*.log 2>/dev/null | tail -1 | xargs -I {} tail -n 10 {}; then
            :
        else
            echo "没有找到日志文件"
        fi
        ;;
    
    5)
        echo "🛑 停止机器人"
        
        # 停止进程
        if pgrep -f "telegram_arbitrage_bot.py" > /dev/null; then
            pkill -f "telegram_arbitrage_bot.py"
            echo "✅ 机器人已停止"
        else
            echo "ℹ️ 机器人未在运行"
        fi
        
        # 停止 screen 会话
        if command -v screen &> /dev/null && screen -ls | grep -q arbitrage_bot; then
            screen -S arbitrage_bot -X quit
            echo "✅ Screen 会话已关闭"
        fi
        ;;
    
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac

echo ""
echo "🎯 完成！"