#!/usr/bin/env python3
"""
Ostium 价格监控脚本
监控 SPX/USD 和 XAU/USD 价格，当低于阈值时发送飞书通知
"""

import json
import time
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

# 配置
SPX_THRESHOLD = 6720
XAU_THRESHOLD = 5050
CHECK_INTERVAL = 1800  # 30分钟
STATE_FILE = Path(__file__).parent.parent / "state" / "monitor_state.json"
LOG_FILE = Path(__file__).parent.parent / "logs" / "monitor.log"

# 确保目录存在
STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

def log(message):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] {message}"
    print(log_msg)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_msg + "\n")

def load_state():
    """加载状态文件"""
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {
        "spx_last_alert": 0,
        "xau_last_alert": 0,
        "last_check": 0
    }

def save_state(state):
    """保存状态文件"""
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

def get_ostium_price(from_token, to_token):
    """
    从 Ostium 获取价格
    注意：这里需要根据实际 API 调整
    """
    try:
        import urllib.request
        import ssl
        
        # 创建 SSL 上下文（忽略证书验证）
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        # 尝试获取 Ostium 页面并解析价格
        url = f"https://app.ostium.com/trade?from={from_token}&to={to_token}"
        
        # 这里需要根据实际情况调整
        # 暂时返回模拟数据用于测试
        log(f"正在获取 {from_token}/{to_token} 价格...")
        
        # TODO: 实现实际的价格获取逻辑
        # 可能需要使用浏览器自动化或找到 API 端点
        
        return None
        
    except Exception as e:
        log(f"获取价格失败: {e}")
        return None

def send_feishu_notification(message):
    """发送飞书通知"""
    try:
        # 使用 OpenClaw 的 message 工具发送飞书消息
        # 这里需要配置飞书 webhook 或 API
        log(f"发送飞书通知: {message}")
        
        # TODO: 实现实际的发送逻辑
        # 可以通过调用 OpenClaw 的 API 或直接调用飞书 webhook
        
        return True
    except Exception as e:
        log(f"发送通知失败: {e}")
        return False

def is_monitoring_time():
    """
    检查当前是否在监控时间段内
    工作日：北京时间 17:00-23:00
    周末：全天
    """
    # 获取北京时间
    beijing_tz = timezone(timedelta(hours=8))
    now = datetime.now(beijing_tz)
    
    weekday = now.weekday()  # 0=周一, 6=周日
    hour = now.hour
    
    # 周末全天监控
    if weekday >= 5:  # 周六或周日
        return True
    
    # 工作日 17:00-23:00
    if 17 <= hour < 23:
        return True
    
    return False

def check_prices(force=False):
    """
    检查价格
    force=True 时无视时间段限制
    """
    if not force and not is_monitoring_time():
        log("当前不在监控时间段内，跳过检查")
        return
    
    state = load_state()
    current_time = int(time.time())
    
    # 获取价格
    spx_price = get_ostium_price("SPX", "USD")
    xau_price = get_ostium_price("XAU", "USD")
    
    if spx_price is None or xau_price is None:
        log("无法获取价格，跳过本次检查")
        return
    
    log(f"当前价格 - SPX/USD: {spx_price}, XAU/USD: {xau_price}")
    
    # 检查 SPX 价格
    if spx_price < SPX_THRESHOLD:
        if current_time - state.get("spx_last_alert", 0) > CHECK_INTERVAL:
            message = f"🚨 Ostium 价格警报\n\nSPX/USD 当前价格: {spx_price}\n低于阈值: {SPX_THRESHOLD}\n\n时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            if send_feishu_notification(message):
                state["spx_last_alert"] = current_time
                state["spx_alert_price"] = spx_price
                log(f"SPX 价格警报已发送: {spx_price}")
    
    # 检查 XAU 价格
    if xau_price < XAU_THRESHOLD:
        if current_time - state.get("xau_last_alert", 0) > CHECK_INTERVAL:
            message = f"🚨 Ostium 价格警报\n\nXAU/USD 当前价格: {xau_price}\n低于阈值: {XAU_THRESHOLD}\n\n时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            if send_feishu_notification(message):
                state["xau_last_alert"] = current_time
                state["xau_alert_price"] = xau_price
                log(f"XAU 价格警报已发送: {xau_price}")
    
    state["last_check"] = current_time
    state["last_spx_price"] = spx_price
    state["last_xau_price"] = xau_price
    save_state(state)

def get_current_prices():
    """获取当前价格并返回（用于手动查询）"""
    spx_price = get_ostium_price("SPX", "USD")
    xau_price = get_ostium_price("XAU", "USD")
    
    if spx_price and xau_price:
        message = f"📊 Ostium 当前价格\n\nSPX/USD: {spx_price}\nXAU/USD: {xau_price}\n\n时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        send_feishu_notification(message)
        log(f"当前价格已推送: SPX={spx_price}, XAU={xau_price}")
    else:
        log("无法获取当前价格")

def main():
    """主函数"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "--current" or sys.argv[1] == "-c":
            # 手动查询当前价格
            get_current_prices()
            return
        elif sys.argv[1] == "--check" or sys.argv[1] == "-k":
            # 强制检查一次（无视时间段）
            check_prices(force=True)
            return
    
    # 默认：按时间段监控
    check_prices()

if __name__ == "__main__":
    main()
