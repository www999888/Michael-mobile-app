# AI Stock Monitor - 一键启动脚本

echo "AI Stock Monitor - 启动中..."
echo "================================"
echo ""
echo "检查环境..."

# 检查 Python 版本
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "Python 版本：$python_version"

# 检查 Ollama
echo ""
echo "检查 Ollama..."
ollama list

echo ""
echo "启动 Streamlit Web 界面..."
echo "访问地址：http://localhost:8501"
echo "按 Ctrl+C 停止服务"
echo ""

streamlit run main.py --server.port 8501 --server.headless true
