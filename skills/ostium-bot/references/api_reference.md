# Ostium API 参考

## 获取价格数据的方法

### 方法 1：浏览器自动化（推荐）

由于 Ostium 是 React 应用，价格数据通过 WebSocket 或 API 动态加载。可以使用 Playwright 或 Selenium：

```python
from playwright.sync_api import sync_playwright

def get_ostium_price(from_token, to_token):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(f"https://app.ostium.com/trade?from={from_token}&to={to_token}")
        
        # 等待价格元素加载
        page.wait_for_selector("[data-testid='price-display']", timeout=10000)
        
        # 提取价格
        price_text = page.inner_text("[data-testid='price-display']")
        price = float(price_text.replace(',', ''))
        
        browser.close()
        return price
```

### 方法 2：监控网络请求

打开浏览器开发者工具，观察 Network 标签：
1. 访问 https://app.ostium.com/trade?from=SPX&to=USD
2. 查看 WebSocket 连接或 XHR 请求
3. 找到价格数据的 API 端点

### 方法 3：GraphQL API

许多 DeFi 平台使用 GraphQL。尝试：

```bash
# 查找 GraphQL 端点
curl -X POST https://api.ostium.com/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ pair(from: \"SPX\", to: \"USD\") { price } }"}'
```

### 方法 4：区块链直接查询

如果 Ostium 是链上协议，可以直接从区块链读取：
- 找到合约地址
- 使用 web3.py 或 ethers.js 调用价格预言机

## 飞书通知实现

### 方式 1：使用 OpenClaw 内置工具

```python
# 调用 OpenClaw 的 message 工具
import subprocess
import json

def send_feishu(message):
    cmd = [
        "openclaw", "message", "send",
        "--channel", "feishu",
        "--text", message
    ]
    subprocess.run(cmd)
```

### 方式 2：Webhook

如果你有飞书机器人的 webhook URL：

```python
import requests

def send_feishu_webhook(message):
    webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxx"
    payload = {
        "msg_type": "text",
        "content": {"text": message}
    }
    requests.post(webhook_url, json=payload)
```

## 下一步

1. 访问 Ostium 网站，打开浏览器开发者工具
2. 找到实际的价格数据 API
3. 更新 monitor.py 中的 `get_ostium_price()` 函数
4. 配置飞书通知方式

## 临时解决方案

如果暂时无法获取 API，可以先用模拟数据测试整个流程：

```python
def get_ostium_price(from_token, to_token):
    # 临时模拟数据
    import random
    if from_token == "SPX":
        return random.uniform(6500, 6800)
    elif from_token == "XAU":
        return random.uniform(4900, 5100)
    return None
```
