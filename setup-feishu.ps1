# 飞书快速配置脚本
# 使用方法: .\setup-feishu.ps1

param(
    [Parameter(Mandatory=$false)]
    [string]$ConfigPath = "$env:APPDATA\openclaw\config.json",

    [Parameter(Mandatory=$false)]
    [string]$FeishuConfigPath = "C:\Users\admin\.openclaw\openclaw.json"
)

Write-Host "🔍 检查配置文件..." -ForegroundColor Cyan

# 检查配置文件是否存在
if (-not (Test-Path $FeishuConfigPath)) {
    Write-Host "❌ 未找到配置文件: $FeishuConfigPath" -ForegroundColor Red
    exit 1
}

# 读取配置文件
$config = Get-Content -Path $FeishuConfigPath -Raw | ConvertFrom-Json

# 检查是否已有飞书配置
if ($config.channels.feishu) {
    Write-Host "⚠️ 飞书配置已存在！" -ForegroundColor Yellow
    Write-Host "路径: $FeishuConfigPath" -ForegroundColor Gray
    Write-Host ""
    Write-Host "当前配置:" -ForegroundColor Yellow
    Write-Host "  App ID: $($config.channels.feishu.appId)" -ForegroundColor Gray
    Write-Host "  Domain: $($config.channels.feishu.domain)" -ForegroundColor Gray
    Write-Host "  Tools: $($config.channels.feishu.tools | ConvertTo-Json)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "如需修改，请编辑配置文件后运行此脚本" -ForegroundColor Yellow
    exit 0
}

Write-Host "📝 准备添加飞书配置..." -ForegroundColor Cyan

# 检查是否需要创建 channels 对象
if (-not $config.channels) {
    $config.channels = @{}
}

# 获取用户输入
Write-Host ""
Write-Host "请填写飞书应用信息:" -ForegroundColor Yellow
Write-Host ""

$appId = Read-Host "App ID (例如: cli_xxxx)"
$appSecret = Read-Host "App Secret"
$encryptKey = Read-Host "Encrypt Key (43 characters)"
$verificationToken = Read-Host "Verification Token (32 characters)"

# 验证密钥长度
if ($encryptKey.Length -ne 43) {
    Write-Host "❌ Encrypt Key 必须是 43 个字符" -ForegroundColor Red
    exit 1
}

if ($verificationToken.Length -ne 32) {
    Write-Host "❌ Verification Token 必须是 32 个字符" -ForegroundColor Red
    exit 1
}

# 添加飞书配置
$config.channels.feishu = @{
    enabled = $true
    appId = $appId
    appSecret = $appSecret
    encryptKey = $encryptKey
    verificationToken = $verificationToken
    domain = "feishu"
    connectionMode = "websocket"
    webhookPath = "/feishu/webhook"
    tools = @{
        doc = $true
        drive = $true
        wiki = $true
        perm = $false
    }
    groupPolicy = "open"
    dmPolicy = "pairing"
    systemPrompt = "你是一个飞书机器人助手，帮助用户管理文档、文件和知识库。"
}

# 保存配置
try {
    $config | ConvertTo-Json -Depth 10 | Set-Content -Path $FeishuConfigPath -Encoding UTF8
    Write-Host ""
    Write-Host "✅ 飞书配置已添加！" -ForegroundColor Green
    Write-Host ""
    Write-Host "下一步:" -ForegroundColor Cyan
    Write-Host "1. 重启 OpenClaw: openclaw restart" -ForegroundColor Gray
    Write-Host "2. 在飞书中邀请机器人: @BotName" -ForegroundColor Gray
    Write-Host ""
    Write-Host "配置详情:" -ForegroundColor Yellow
    Write-Host "  App ID: $appId" -ForegroundColor Gray
    Write-Host "  Domain: feishu" -ForegroundColor Gray
    Write-Host "  Tools: doc, drive, wiki" -ForegroundColor Gray
}
catch {
    Write-Host "❌ 保存配置失败: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

exit 0