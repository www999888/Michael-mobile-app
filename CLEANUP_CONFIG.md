# Context Cleanup Configuration - 上下文清理配置

## 📅 清理频率
- **执行周期**: 每 3 天执行一次
- **下次执行**: 当前时间 + 72 小时

## 📝 清理任务说明
- **脚本位置**: `C:\Users\admin\.openclaw\workspace\cleanup-context.ps1`
- **清理对象**: AI Stock Monitor 项目日志文件
- **保留时间**: 3 天
- **清理内容**:
  - 超过 3 天的日志文件
  - 标记超过 500KB 的大日志文件

## ⚙️ 配置参数
```powershell
$keepDays = 3                    # 保留 3 天
$maxSizeKB = 500                 # 超过 500KB 标记警告
```

## 🔄 执行方式
1. **自动执行**: 通过 cron 任务每 3 天自动触发
2. **手动执行**: `powershell -File cleanup-context.ps1`

## 📊 日志清理范围
- 目录：`C:\Users\admin\.openclaw\workspace\ai-stock-monitor\`
- 文件类型：`.log` 文件
- 不删除 memory/目录文件（保留完整历史）

## ✅ 注意事项
- 不会删除 AI Stock Monitor 项目核心文件
- 只清理日志文件，保留项目完整结构
- 大文件会标记但不会自动删除，需手动处理
- 清理前会输出统计信息

## 📝 执行记录
- 每次执行会输出：
  - 删除的文件数
  - 保留的文件数
  - 大文件警告

---
**最后更新**: 2026-03-25 18:40
**版本**: 2.0 (每三天执行)
