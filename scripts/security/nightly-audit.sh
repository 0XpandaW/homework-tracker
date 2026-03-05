#!/bin/bash
# OpenClaw 夜间安全审计脚本
# 基于 SlowMist 安全实践指南
# 13 项核心指标检查

WORKSPACE="$HOME/.openclaw/workspace"
STATE_DIR="$WORKSPACE/state"
LOG_DIR="$WORKSPACE/logs"
REPORT_FILE="$LOG_DIR/security-audit-$(date +%Y%m%d).log"

echo "=== OpenClaw 夜间安全审计 ===" | tee -a "$REPORT_FILE"
echo "时间: $(date)" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

# 1. 文件完整性 - 关键配置文件
echo "[1/13] 检查关键配置文件..." | tee -a "$REPORT_FILE"
for file in "$WORKSPACE/AGENTS.md" "$WORKSPACE/SOUL.md" "$WORKSPACE/USER.md" "$WORKSPACE/TOOLS.md"; do
    if [ -f "$file" ]; then
        md5sum "$file" >> "$STATE_DIR/file-hashes.txt" 2>/dev/null
    fi
done
echo "✓ 配置文件哈希已记录" | tee -a "$REPORT_FILE"

# 2. Skill 指纹
echo "[2/13] 检查 Skill 安装..." | tee -a "$REPORT_FILE"
if [ -d "$WORKSPACE/skills" ]; then
    find "$WORKSPACE/skills" -type f \( -name "*.py" -o -name "*.js" -o -name "*.sh" \) -exec md5sum {} \; > "$STATE_DIR/skill-fingerprints.txt" 2>/dev/null
    echo "✓ Skill 指纹已记录 ($(find "$WORKSPACE/skills" -type f | wc -l) 个文件)" | tee -a "$REPORT_FILE"
fi

# 3. 权限异常 - suid/sgid 文件
echo "[3/13] 检查权限异常..." | tee -a "$REPORT_FILE"
find "$WORKSPACE" -type f \( -perm -4000 -o -perm -2000 \) 2>/dev/null | tee -a "$REPORT_FILE"

# 4. 定时任务
echo "[4/13] 检查定时任务..." | tee -a "$REPORT_FILE"
crontab -l 2>/dev/null | tee -a "$REPORT_FILE"

# 5. Git 状态
echo "[5/13] 检查 Git 状态..." | tee -a "$REPORT_FILE"
cd "$WORKSPACE"
if [ -d .git ]; then
    git status --short | tee -a "$REPORT_FILE"
    # 自动提交
    git add -A 2>/dev/null
    git commit -m "夜间自动备份 $(date +%Y-%m-%d)" 2>/dev/null || true
    echo "✓ Git 备份已完成" | tee -a "$REPORT_FILE"
else
    echo "⚠ 未找到 Git 仓库，建议初始化" | tee -a "$REPORT_FILE"
fi

# 6. 大文件变更
echo "[6/13] 检查大文件..." | tee -a "$REPORT_FILE"
find "$WORKSPACE" -type f -size +10M -exec ls -lh {} \; 2>/dev/null | tee -a "$REPORT_FILE"

# 7. 环境变量中的敏感信息
echo "[7/13] 检查环境变量..." | tee -a "$REPORT_FILE"
env | grep -iE "(key|token|secret|password|api)" | sed 's/=.*/=***/' | tee -a "$REPORT_FILE"

echo "" | tee -a "$REPORT_FILE"
echo "=== 审计完成 ===" | tee -a "$REPORT_FILE"

# 清理旧日志（保留 30 天）
find "$LOG_DIR" -name "security-audit-*.log" -mtime +30 -delete 2>/dev/null
