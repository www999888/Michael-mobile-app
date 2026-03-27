AI Stock Monitor - 本地私有化 AI 股票盯盘交易工具

🎯 项目介绍
==========
这是一个完全本地的 AI 股票分析工具，使用本地 Ollama 大模型进行智能分析。
- ✅ 实时监控股票价格、成交量、涨跌幅
- ✅ 自动计算技术指标（MACD、RSI、KDJ、BOLL）
- ✅ 本地大模型生成 AI 分析 + 交易建议
- ✅ 支持模拟交易、盈亏统计、告警提醒
- ✅ 全本地运行，不上传任何数据

📁 项目结构
==========
ai-stock-monitor/
├── config/          # 配置文件
├── data/           # 数据模块
├── analyzer/       # 分析模块
├── monitor/        # 盯盘模块
├── trader/         # 模拟交易模块
├── ui/             # Web 界面
├── logs/           # 日志目录
├── main.py         # 主入口
├── requirements.txt # 依赖列表
├── run.bat         # 启动脚本
├── build_exe.bat   # 打包脚本

🚀 快速开始
==========
1. 确保已安装 Ollama 并拉取模型：
   ollama pull qwen3.5:35b

2. 安装 Python 依赖：
   pip install -r requirements.txt

3. 启动应用：
   run.bat
   或
   streamlit run main.py

4. 浏览器访问：http://localhost:8501

📊 功能说明
==========
- 📈 实时行情监控
- 🤖 AI 智能分析（使用本地大模型）
- 💼 模拟交易
- 📉 技术分析（MACD、RSI、KDJ、BOLL）
- 🔔 价格告警
- 📊 盈亏统计

⚙️ 配置说明
==========
在 config/settings.py 中配置：
- 股票池
- 技术指标参数
- 告警阈值
- 模拟交易参数

🔧 开发模式
==========
- 使用模拟数据进行开发测试
- 可接入真实数据源（如 Tushare）
- 支持自定义 AI 模型

📝 许可证
==========
MIT License - 自由使用

⚠️ 免责声明
==========
本工具仅供学习和研究使用，不构成任何投资建议。
股市有风险，投资需谨慎。
