---
name: ostium-bot
description: "Monitor Ostium trading platform prices for SPX/USD and XAU/USD, send Feishu notifications when prices drop below thresholds. Use when: (1) User asks to start monitoring Ostium prices, (2) User wants to check current SPX/USD or XAU/USD prices on Ostium, (3) User needs price alerts for trading pairs on Ostium platform. Monitors Monday-Friday 5PM-11PM Beijing time, and all day on weekends."
---

# Ostium Bot

Monitor SPX/USD and XAU/USD prices on Ostium trading platform with automatic Feishu notifications.

## Features

- 📊 Monitor SPX/USD price (alert when below 6720)
- 📊 Monitor XAU/USD price (alert when below 5050)
- 🔔 Send Feishu notifications when thresholds are breached
- ⏰ Smart scheduling: Weekdays 17:00-23:00, Weekends all day (Beijing time)
- 📱 Manual price query on demand

## Usage

### Start Monitoring

When user says "开始监控价格" or "start monitoring prices":

```bash
python3 scripts/monitor.py --check
```

This will immediately check current prices and push them to Feishu, regardless of the scheduled monitoring time.

### Get Current Prices

When user asks for current prices:

```bash
python3 scripts/monitor.py --current
```

### Scheduled Monitoring

For automatic monitoring (run every 30 minutes via cron):

```bash
python3 scripts/monitor.py
```

This only checks prices during the configured monitoring window:
- Weekdays (Mon-Fri): 17:00-23:00 Beijing time
- Weekends (Sat-Sun): All day

## Configuration

Edit `scripts/monitor.py` to adjust:

- `SPX_THRESHOLD = 6720` - SPX/USD alert threshold
- `XAU_THRESHOLD = 5050` - XAU/USD alert threshold
- `CHECK_INTERVAL = 1800` - Alert cooldown (30 minutes)

## State Files

- `state/monitor_state.json` - Stores last alert times and prices
- `logs/monitor.log` - Activity logs

## Setup Cron Job

To run monitoring every 30 minutes:

```bash
# Edit crontab
crontab -e

# Add line:
*/30 * * * * cd /Users/pandaw/.openclaw/workspace/skills/ostium-bot && python3 scripts/monitor.py
```

## Implementation Notes

**Important**: The price fetching logic in `get_ostium_price()` needs to be implemented based on Ostium's actual API or page structure. Currently it's a placeholder that needs:

1. Either: Find Ostium's public API endpoint for price data
2. Or: Use browser automation to scrape the trading page
3. Or: Use WebSocket if Ostium provides real-time data

See `references/api_reference.md` for potential approaches.

## Price Alert Logic

- Alerts are sent only once per 30-minute window for each trading pair
- This prevents spam while ensuring user is notified of significant drops
- Manual queries (`--current`, `--check`) bypass the cooldown
