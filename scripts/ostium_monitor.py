#!/usr/bin/env python3
"""
Ostium 价格监控脚本
监控 SPX/USD 和 XAU/USD 价格，当价格低于阈值时发送飞书通知
"""

import json
import time
import os
import sys
from datetime import datetime
from pathlib import Path

# 配置
SPX_THRESHOLD = 6720
XAU_THRESHOLD = 5050
CHECK_INTERVAL = 1800  # 30分钟
ALERT_COOLDOWN = 1800  # 30分钟冷却

# 文件路径
WORKSPACE = Path("/Users/pandaw/.openclaw/workspace")
LOG_FILE = WORKSPACE / "logs" / "ostium_monitor.log"
STATE_FILE = WORKSPACE / "logs" / "ostium_state.json"

# 创建目录
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

def log(message):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    print(log_entry)
    with open(LOG_FILE, "a") as f:
        f.write(log_entry + "\n")

def load_state():
    """加载状态文件"""
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {
        "spx_last_alert": 0,
        "xau_last_alert": 0,
        "spx_last_price": None,
        "xau_last_price": None
    }

def save_state(state):
    """保存状态文件"""
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def get_prices_from_ostium():
    """
    从 Ostium 获取价格
    由于 Ostium 是 Web3 应用，我们需要通过其智能合约或 API 获取价格
    这里使用模拟数据，实际使用时需要替换为真实数据源
    """
    try:
        # 尝试从 Ostium 的 API 获取数据
        # 注意：这里需要替换为实际的 API 端点
        import urllib.request
        import ssl
        
        # 创建 SSL 上下文（忽略证书验证）
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        # 尝试获取 Ostium 的价格数据
        # 这里使用 CoinGecko 作为替代数据源
        urls = [
            "https://api.coingecko.com/api/v3/simple/price?ids=spx6900&vs_currencies=usd",
            "https://api.coingecko.com/api/v3/simple/price?ids=pax-gold&vs_currencies=usd"
        ]
        
        spx_price = None
        xau_price = None
        
        # 注意：这些可能不是 Ostium 上的实际价格
        # 需要找到 Ostium 的实际价格源
        
        return spx_price, xau_price
        
    except Exception as e:
        log(f"获取价格失败: {e}")
        return None, None

def send_feishu_alert(asset, price, threshold):
    """发送飞书通知"""
    try:
        # 这里需要实现飞书消息发送
        # 使用飞书的 webhook 或 API
        log(f"发送飞书通知: {asset} 价格 {price} 低于阈值 {threshold}")
        
        # TODO: 实现实际的飞书消息发送
        # 可以使用 feishu_doc 或其他飞书工具
        
    except Exception as e:
        log(f"发送飞书通知失败: {e}")

def check_prices():
    """检查价格并发送警报"""
    state = load_state()
    current_time = time.time()
    
    # 获取当前价格
    spx_price, xau_price = get_prices_from_ostium()
    
    if spx_price is None or xau_price is None:
        log("无法获取价格数据，跳过本次检查")
        return
    
    log(f"当前价格 - SPX/USD: {spx_price}, XAU/USD: {xau_price}")
    
    # 更新状态
    state["spx_last_price"] = spx_price
    state["xau_last_price"] = xau_price
    
    # 检查 SPX/USD
    if spx_price < SPX_THRESHOLD:
        if current_time - state.get("spx_last_alert", 0) > ALERT_COOLDOWN:
            send_feishu_alert("SPX/USD", spx_price, SPX_THRESHOLD)
            state["spx_last_alert"] = current_time
            state["spx_alert_price"] = spx_price
            log(f"SPX/USD 警报触发: {spx_price} < {SPX_THRESHOLD}")
    
    # 检查 XAU/USD
    if xau_price < XAU_THRESHOLD:
        if current_time - state.get("xau_last_alert", 0) > ALERT_COOLDOWN:
            send_feishu_alert("XAU/USD", xau_price, XAU_THRESHOLD)
            state["xau_last_alert"] = current_time
            state["xau_alert_price"] = xau_price
            log(f"XAU/USD 警报触发: {xau_price} < {XAU_THRESHOLD}")
    
    save_state(state)

if __name__ == "__main__":
    log("=" * 50)
    log("Ostium 价格监控启动")
    log(f"SPX/USD 阈值: {SPX_THRESHOLD}")
    log(f"XAU/USD 阈值: {XAU_THRESHOLD}")
    log("=" * 50)
    
    check_prices()
