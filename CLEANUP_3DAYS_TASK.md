# AI Stock Monitor Context Cleanup - 每三天自动清理任务

## 📅 任务配置

### 基本信息
- **任务名称**: `context-cleanup-3days`
- **执行脚本**: `cleanup-context.ps1`
- **执行频率**: 每 3 天（259,200,000 毫秒）
- **状态**: ✅ 已启用

### 清理参数
```powershell
$keepDays = 3                    # 保留 3 天
$maxSizeKB = 500                 # 超过 500KB 警告
```

### 清理范围
- **目标目录**: `C:\Users\admin\.openclaw\workspace\ai-stock-monitor\`
- **清理文件**: `.log` 日志文件
- **保留时间**: 3 天
- **大文件警告**: 超过 500KB

## 🔄 执行方式

### 自动定时任务 (推荐)
通过 cron 系统每 3 天自动触发：
```
任务 ID: 2abc2dec-3216-4e1d-a82b-eac09103f77f
频率：每 3 天
状态：运行中
```

### 手动执行
```powershell
cd C:\Users\admin\.openclaw\workspace
powershell -ExecutionPolicy Bypass -File cleanup-context.ps1
```

## 📝 执行日志示例
```
=== AI Stock Monitor Context Cleanup ===
执行时间：2026-03-25 18:40:00
  🗑️  删除：old_log_20260318.log
  🗑️  删除：old_log_20260317.log
  ⚠️   大文件：error.log (1200KB)
清理统计:
  删除文件：5
  保留文件：12
  大文件警告：2
完成时间：2026-03-25 18:40:05
```

## ⚙️ 系统设置

**时间计算**:
- 3 天 = 259,200,000 毫秒
- 执行间隔：每 3 天
- 自动定时触发

**脚本内容**:
- 删除超过 3 天的日志
- 标记大文件（>500KB）
- 输出详细统计

## 📊 任务状态

| 项目 | 值 |
|------|-----|
| 任务 ID | 2abc2dec-3216-4e1d-a82b-eac09103f77f |
| 名称 | context-cleanup-3days |
| 频率 | 每 3 天 |
| 状态 | 启用 |
| 下次执行 | +3 天 |

## 🎯 执行步骤

1. **自动触发**（每 3 天）:
   - 系统自动检查并执行
   - 无需手动干预
   - 输出执行结果

2. **手动触发**:
   ```powershell
   powershell -File cleanup-context.ps1
   ```
   - 立即执行一次
   - 验证脚本功能
   - 查看执行结果

## ✅ 完成状态

- ✅ 清理脚本已创建
- ✅ 自动任务已配置
- ✅ 执行频率：每 3 天
- ✅ 清理范围：AI Stock Monitor 日志
- ✅ 保留周期：3 天

**配置完成！每三天自动执行一次 context 清理任务。🎉**
