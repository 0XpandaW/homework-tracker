# OpenClaw 安全状态
# 由 Agent 自动更新

## 部署状态
- [x] 安全指南已加载 (SECURITY_GUIDE.md)
- [x] 红线/黄线规则已激活
- [x] Skill 审计协议已启用
- [x] 夜间审计脚本已部署
- [x] 脑 Git 备份已初始化
- [ ] 夜间审计 Cron Job（需用户手动配置）

## 配置说明

### 启用夜间自动审计
运行以下命令添加定时任务：
```bash
crontab -e
# 添加以下行（每天凌晨 3 点执行）：
0 3 * * * cd ~/.openclaw/workspace && bash scripts/security/nightly-audit.sh
```

### 查看审计日志
```bash
ls -la ~/.openclaw/workspace/logs/security-audit-*.log
cat ~/.openclaw/workspace/logs/security-audit-$(date +%Y%m%d).log
```

### 手动执行审计
```bash
bash ~/.openclaw/workspace/scripts/security/nightly-audit.sh
```

## 最后更新
2026-03-05
