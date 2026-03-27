# Context Cleanup Script - Runs every 3 days
# Cleans up AI Stock Monitor project log files

$workspace = "C:\Users\admin\.openclaw\workspace"
$aiStockDir = "$workspace\ai-stock-monitor"

Write-Host "== AI Stock Monitor Context Cleanup =="
Write-Host "Execution time: $((Get-Date).ToString('yyyy-MM-dd HH:mm:ss'))"

$keepDays = 3
$threshold = (Get-Date).AddDays(-$keepDays)
$deleted = 0
$kept = 0
$largeFiles = 0
$maxSizeKB = 500

if (Test-Path $aiStockDir) {
    Get-ChildItem -Path $aiStockDir -Filter "*.log" -File | ForEach-Object {
        if ($_.LastWriteTime -lt $threshold) {
            Remove-Item $_.FullName -Force
            Write-Host "  Deleted: $($_.Name)"
            $deleted++
        } else {
            $kept++
            if ($_.Length -gt ($maxSizeKB * 1024)) {
                $largeFiles++
                Write-Host "  Large file: $($_.Name)"
            }
        }
    }
} else {
    Write-Host "  ai-stock-monitor directory not found"
}

Write-Host "----- Cleanup statistics -----"
Write-Host "  Files deleted: $deleted"
Write-Host "  Files kept: $kept"
Write-Host "  Large files warning: $largeFiles"
Write-Host "Completion time: $((Get-Date).ToString('yyyy-MM-dd HH:mm:ss'))"