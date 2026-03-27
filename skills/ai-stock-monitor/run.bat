@echo off
REM AI Stock Monitor - Windows 启动脚本
REM Python 3.9+ required

echo ========================================
echo   📊 AI Stock Monitor
echo ========================================

REM 检查 Python 是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] Python 未安装或未添加到 PATH
    echo 请先安装 Python 3.9+ 并从官网下载 pip
    pause
    exit /b 1
)

REM 创建虚拟环境
if not exist "venv" (
    echo [1/3] 创建虚拟环境...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [错误] 虚拟环境创建失败
        pause
        exit /b 1
    )
)

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 安装依赖
echo [2/3] 安装依赖包...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)

REM 检查 Ollama
echo [3/3] 检查 Ollama 服务...
powershell -Command "if (Test-Path 'http://localhost:11434/api/tags') { echo '✅ Ollama 已运行' } else { echo '⚠️ Ollama 未运行，请先启动 Ollama' }"

REM 启动 Web UI
echo.
echo ========================================
echo   正在启动 Web 界面...
echo   访问地址：http://localhost:8501
echo ========================================
echo.

python main.py web

pause
