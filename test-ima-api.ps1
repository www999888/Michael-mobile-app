# 加载凭证
$CLIENT_ID = Get-Content "C:\Users\admin\.config\ima\client_id"
$API_KEY = Get-Content "C:\Users\admin\.config\ima\api_key"

# 测试 API 调用 - 获取当前用户信息
$body = @{ } | ConvertTo-Json -Depth 10
$utf8Bytes = [System.Text.Encoding]::UTF8.GetBytes($body)

$headers = @{
    "ima-openapi-clientid" = $CLIENT_ID
    "ima-openapi-apikey" = $API_KEY
    "Content-Type" = "application/json; charset=utf-8"
}

try {
    $response = Invoke-RestMethod -Uri "https://ima.qq.com/v1/user/info" -Method Post -Body $utf8Bytes -Headers $headers -ErrorAction Stop
    Write-Host "✅ API 连接成功！"
    $response | ConvertTo-Json
} catch {
    Write-Host "❌ API 连接失败：" $_.Exception.Message
}
