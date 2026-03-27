@echo off
echo AI Stock Monitor - 打包为 EXE
echo ==============================

REM 检查是否已安装 PyInstaller
python -m pip install --upgrade pip -q
pip install pyinstaller -q

REM 确保所有依赖已安装
echo 正在检查依赖...
pip install streamlit pandas numpy requests python-dotenv tushare -q

REM 清理旧的打包文件
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build
if exist "ai_stock_monitor.spec" del /q "ai_stock_monitor.spec"

REM 创建 spec 文件
echo 正在创建打包配置...
pyi-makespec --onefile --windowed --name "AI_Stock_Monitor" --add-data "ui;ui" --add-data "config;config" --add-data "data;data" --add-data "analyzer;analyzer" --add-data "monitor;monitor" --add-data "trader;trader" main.py

REM 检查 spec 文件是否存在
if not exist "AI_Stock_Monitor.spec" (
    echo 错误：spec 文件未生成
    pause
    exit /b 1
)

REM 使用 spec 文件打包
echo 正在打包...
pyinstaller AI_Stock_Monitor.spec

REM 检查打包结果
if exist "dist\AI_Stock_Monitor.exe" (
    echo.
    echo 打包完成！
    echo 可执行文件位置：dist\AI_Stock_Monitor.exe
    echo.
    echo 使用说明：
    echo 1. 确保已安装 Ollama 并运行：ollama serve
    echo 2. 双击 AI_Stock_Monitor.exe 运行
    echo 3. 浏览器访问：http://localhost:8501
) else (
    echo 打包失败！
    echo 请检查错误信息
)

pause
