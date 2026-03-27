AI Stock Monitor - 本地 AI 股票盯盘分析交易系统

完全本地运行，利用 Ollama 大模型进行智能分析
无云端依赖，数据隐私安全

📁 项目结构
├── config/                    # 配置文件
│   ├── __init__.py
│   ├── settings.py           # 全局配置
│   └── logging_config.py     # 日志配置
├── data/                     # 数据模块
│   ├── __init__.py
│   ├── data_fetcher.py       # 股票数据获取 (Tushare)
│   └── data_storage.py       # 数据存储和缓存
├── analyzer/                 # 分析模块
│   ├── __init__.py
│   ├── tech_analyzer.py      # 技术指标分析
│   └── ai_analyzer.py        # Ollama AI 分析
├── monitor/                  # 盯盘模块
│   ├── __init__.py
│   └── stock_monitor.py      # 实时监控和告警
├── trader/                   # 模拟交易模块
│   ├── __init__.py
│   └── sim_trader.py         # 模拟交易和盈亏计算
├── ui/                       # Web UI
│   ├── __init__.py
│   ├── web_ui.py             # Streamlit 界面
│   └── static/               # 静态资源
├── logs/                     # 日志目录
├── data_storage/             # 本地数据库
├── main.py                   # 项目入口
├── requirements.txt          # Python 依赖
├── Dockerfile                # Docker 镜像
├── docker-compose.yml        # Docker 编排
├── run.bat                   # Windows 启动脚本
├── run.sh                    # Linux/Mac 启动脚本
├── README.md                 # 项目文档
└── .env.example              # 环境变量示例

🔧 核心功能
1. 实时盯盘 - 监控股票价格、成交量、涨跌幅
2. 技术分析 - 自动计算 MA/MACD/KDJ/RSI/BOLL
3. AI 分析 - Ollama 本地大模型智能决策
4. 模拟交易 - 虚拟资金模拟买卖，盈亏统计
5. 告警系统 - 价格/涨跌幅/成交量异常告警
6. Web UI - Streamlit 可视化界面

📊 技术指标支持
- MA (Moving Average) - 移动平均线
- MACD - 平滑异同移动平均线
- KDJ - 随机指标
- RSI - 相对强弱指标
- BOLL - 布林带

🤖 AI 分析能力
- 趋势分析 - 基于历史数据预测走势
- 技术面解读 - 综合指标分析
- 交易建议 - 买入/卖出/持有建议
- 风险评估 - 波动率和风险等级

🚀 快速开始
1. 安装 Python 3.9+
2. pip install -r requirements.txt
3. 配置 .env 文件
4. ollama pull llama3.2 或你的模型
5. 运行 python main.py 启动

📖 详细文档见 README.md
