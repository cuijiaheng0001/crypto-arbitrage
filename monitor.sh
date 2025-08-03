#!/bin/bash

# 监控脚本 - 使用 cron 定时运行

CONTAINER_NAME="crypto-arbitrage-bot"
LOG_FILE="/var/log/crypto-arbitrage-monitor.log"
TELEGRAM_BOT_TOKEN="YOUR_TELEGRAM_BOT_TOKEN"
TELEGRAM_CHAT_ID="YOUR_TELEGRAM_CHAT_ID"

# 发送Telegram通知（可选）
send_telegram_notification() {
    local message=$1
    if [ ! -z "$TELEGRAM_BOT_TOKEN" ] && [ "$TELEGRAM_BOT_TOKEN" != "YOUR_TELEGRAM_BOT_TOKEN" ]; then
        curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
            -d chat_id="$TELEGRAM_CHAT_ID" \
            -d text="🤖 Crypto Bot Alert: $message" > /dev/null
    fi
}

# 记录日志
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> $LOG_FILE
}

# 检查容器状态
check_container() {
    if ! docker ps | grep -q $CONTAINER_NAME; then
        log_message "ERROR: Container $CONTAINER_NAME is not running!"
        send_telegram_notification "Container $CONTAINER_NAME is down! Attempting restart..."
        
        # 尝试重启容器
        cd /root/crypto-arbitrage
        docker-compose restart crypto-arbitrage
        
        sleep 30
        
        # 再次检查
        if docker ps | grep -q $CONTAINER_NAME; then
            log_message "SUCCESS: Container restarted successfully"
            send_telegram_notification "Container $CONTAINER_NAME restarted successfully ✅"
        else
            log_message "CRITICAL: Failed to restart container"
            send_telegram_notification "CRITICAL: Failed to restart $CONTAINER_NAME ❌"
        fi
    else
        log_message "INFO: Container $CONTAINER_NAME is running normally"
    fi
}

# 检查磁盘空间
check_disk_space() {
    DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ $DISK_USAGE -gt 90 ]; then
        log_message "WARNING: Disk usage is at $DISK_USAGE%"
        send_telegram_notification "WARNING: Server disk usage is at $DISK_USAGE% ⚠️"
    fi
}

# 检查内存使用
check_memory() {
    MEMORY_USAGE=$(free | grep Mem | awk '{print int($3/$2 * 100)}')
    if [ $MEMORY_USAGE -gt 90 ]; then
        log_message "WARNING: Memory usage is at $MEMORY_USAGE%"
        send_telegram_notification "WARNING: Server memory usage is at $MEMORY_USAGE% ⚠️"
    fi
}

# 主函数
main() {
    log_message "Starting monitoring check..."
    check_container
    check_disk_space
    check_memory
    log_message "Monitoring check completed"
}

# 运行主函数
main