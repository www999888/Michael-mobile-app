#!/bin/bash
# AI Stock Monitor - Linux/Mac 启动脚本

echo "========================================"
echo "  📊 AI Stock Monitor"
echo "========================================"

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "[错误] Python 3.9+ 未安装"
    echo "请先安装 Python 3.9+"
    exit 1
fi

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo "[1/3] 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "[2/3] 安装依赖包..."
pip install -r requirements.txt

# 检查 Ollama
echo "[3/3] 检查 Ollama 服务..."
if curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "✅ Ollama 已运行"
else
    echo "⚠️ Ollama 未运行，请先启动 Ollama"
fi

echo ""
echo "========================================"
echo "  正在启动 Web 界面..."
echo "  访问地址：http://localhost:8501"
echo "========================================"
echo ""

python main.py web
