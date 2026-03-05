#!/bin/bash

# Ostium 价格监控脚本
# 监控 SPX/USD 和 XAU/USD 价格

WORKSPACE="/Users/pandaw/.openclaw/workspace"
LOG_FILE="$WORKSPACE/logs/ostium_monitor.log"
STATE_FILE="$WORKSPACE/logs/ostium_state.json"

# 创建日志目录
mkdir -p "$WORKSPACE/logs"

# 获取当前时间
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# 使用 curl 获取 Ostium API 数据
# 注意：这里需要找到 Ostium 的实际 API 端点
# 暂时使用模拟数据进行测试

SPX_PRICE=$(curl -s "https://api.ostium.com/v1/price/SPX/USD" 2>/dev/null | jq -r '.price // empty')
XAU_PRICE=$(curl -s "https://api.ostium.com/v1/price/XAU/USD" 2>/dev/null | jq -r '.price // empty')

# 如果 API 调用失败，记录日志
if [ -z "$SPX_PRICE" ] || [ -z "$XAU_PRICE" ]; then
    echo "[$TIMESTAMP] 错误：无法获取价格数据" >> "$LOG_FILE"
    exit 1
fi

# 读取上次状态
if [ -f "$STATE_FILE" ]; then
    LAST_SPX_ALERT=$(jq -r '.spx_last_alert // 0' "$STATE_FILE")
    LAST_XAU_ALERT=$(jq -r '.xau_last_alert // 0' "$STATE_FILE")
else
    LAST_SPX_ALERT=0
    LAST_XAU_ALERT=0
fi

CURRENT_TIME=$(date +%s)
ALERT_COOLDOWN=1800  # 30分钟冷却时间

# 检查 SPX/USD 价格
if (( $(echo "$SPX_PRICE < 6720" | bc -l) )); then
    if [ $((CURRENT_TIME - LAST_SPX_ALERT)) -gt $ALERT_COOLDOWN ]; then
        # 发送飞书通知
        echo "[$TIMESTAMP] SPX/USD 价格警报: $SPX_PRICE (低于 6720)" >> "$LOG_FILE"
        
        # 更新状态
        jq -n --arg time "$CURRENT_TIME" --arg price "$SPX_PRICE" \
            '{spx_last_alert: $time, spx_alert_price: $price}' > "$STATE_FILE.tmp"
        mv "$STATE_FILE.tmp" "$STATE_FILE"
        
        # TODO: 调用飞书 API 发送消息
    fi
fi

# 检查 XAU/USD 价格
if (( $(echo "$XAU_PRICE < 5050" | bc -l) )); then
    if [ $((CURRENT_TIME - LAST_XAU_ALERT)) -gt $ALERT_COOLDOWN ]; then
        # 发送飞书通知
        echo "[$TIMESTAMP] XAU/USD 价格警报: $XAU_PRICE (低于 5050)" >> "$LOG_FILE"
        
        # 更新状态
        jq -n --arg time "$CURRENT_TIME" --arg price "$XAU_PRICE" \
            '{xau_last_alert: $time, xau_alert_price: $price}' > "$STATE_FILE.tmp"
        mv "$STATE_FILE.tmp" "$STATE_FILE"
        
        # TODO: 调用飞书 API 发送消息
    fi
fi

echo "[$TIMESTAMP] 监控完成 - SPX: $SPX_PRICE, XAU: $XAU_PRICE" >> "$LOG_FILE"
