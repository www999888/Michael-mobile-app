# 📊 AI Stock Monitor - 本地 AI 股票盯盘分析交易系统

> 🌟 **完全本地运行 | 无云端依赖 | 数据隐私安全**

一个基于 **Ollama 本地大模型**的股票监控分析工具，支持实时盯盘、技术分析、AI 决策、模拟交易等功能。

---

## ✨ 核心功能

### 1. 📈 实时盯盘
- 监控股票价格、成交量、涨跌幅
- 自动计算技术指标（MA、MACD、KDJ、RSI、BOLL）
- 价格/成交量异常告警

### 2. 🤖 AI 智能分析
- **Ollama 本地大模型**进行趋势研判
- 综合技术分析生成交易建议
- 风险评估和买卖点建议

### 3. 💼 模拟交易
- 虚拟资金模拟买卖
- 持仓管理
- 盈亏统计和绩效报告

### 4. 🎨 Web 可视化
- Streamlit 交互式界面
- 实时 K 线图和技术指标
- 资金分布可视化

---

## 🚀 快速开始

### 环境要求
- **Python:** 3.9+
- **Ollama:** 已安装并运行
- **推荐模型:** llama3.2, qwen2.5, mistral

### 安装步骤

#### 1. 克隆项目
```bash
cd skills/ai-stock-monitor
```

#### 2. 安装依赖
```bash
# 方式 A: 使用虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

#### 3. 配置 Ollama
```bash
# 启动 Ollama 服务
ollama serve

# 拉取推荐模型
ollama pull llama3.2
```

#### 4. 启动应用
```bash
# 方式 A: 运行快速演示
python main.py demo

# 方式 B: 启动 Web UI
python main.py web

# 方式 C: 使用启动脚本
./run.sh    # Linux/Mac
run.bat     # Windows
```

#### 5. 访问 Web 界面
浏览器打开：`http://localhost:8501`

---

## 📋 项目结构

```
ai-stock-monitor/
├── config/                    # 配置文件
│   ├── __init__.py
│   ├── settings.py           # 全局配置（股票池、接口、模型、阈值）
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
├── logs/                     # 日志目录
├── data_storage/             # 本地数据库
├── main.py                   # 项目入口
├── requirements.txt          # Python 依赖
├── Dockerfile                # Docker 镜像
├── docker-compose.yml        # Docker 编排
├── run.bat                   # Windows 启动脚本
├── run.sh                    # Linux/Mac 启动脚本
└── README.md                 # 项目文档
```

---

## 🔧 配置说明

### settings.py 核心配置

```python
# 股票池配置
STOCK_POOL = {
    "A 股": ["000001.SZ", "600000.SH", ...],
    "ETF": ["510300.SH", "510500.SH"],
}

# 默认监控股票池
DEFAULT_STOCKS = ["000001.SZ", "600000.SH", ...]

# Ollama 配置
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.2"  # 或 qwen2.5, mistral

# 技术分析参数
TECH_ANALYSIS_PARAMS = {
    "MA": {"short_period": 5, "medium_period": 10, "long_period": 20},
    "MACD": {"fast_period": 12, "slow_period": 26, "signal_period": 9},
    "KDJ": {"n_period": 9, "m1_period": 3, "m2_period": 3},
    "RSI": {"short_period": 6, "long_period": 12},
    "BOLL": {"period": 20, "mult": 2.0}
}

# 模拟交易配置
SIM_TRADING = {
    "initial_capital": 1000000,  # 初始资金 100 万
    "min_shares": 100,           # 最小交易单位 100 股
}

# 功能开关
FEATURES = {
    "realtime_monitor": True,   # 实时盯盘
    "ai_analysis": True,        # AI 分析
    "sim_trading": True,        # 模拟交易
    "alerts": True,             # 告警通知
    "auto_trade": False         # 自动交易（危险！建议先用模拟）
}
```

---

## 📊 技术指标说明

### 移动平均线 (MA)
- **MA 短:** 5 日均线，短期趋势
- **MA 中:** 10 日均线，中期趋势
- **MA 长:** 20 日均线，长期趋势

### MACD (平滑异同移动平均线)
- **快线:** EMA(12)
- **慢线:** EMA(26)
- **Signal:** 信号线
- **Histogram:** 柱状图

### KDJ (随机指标)
- **K:** 快速随机值
- **D:** 慢速随机值
- **J:** 方向敏感值
- **超卖:** K < 20，超买：K > 80

### RSI (相对强弱指标)
- **RSI(6):** 短期强弱
- **RSI(12):** 中长期强弱
- **超卖:** RSI < 30，超买：RSI > 70

### BOLL (布林带)
- **上轨:** 压力位
- **中轨:** 均线
- **下轨:** 支撑位
- **带宽:** 波动率指标

---

## 🎯 使用示例

### 1. 启动快速演示
```bash
python main.py demo
```

### 2. 启动 Web UI
```bash
python main.py web
# 浏览器访问 http://localhost:8501
```

### 3. 启动监控（后台运行）
```bash
python main.py monitor
```

### 4. 命令行分析
```python
from analyzer.tech_analyzer import get_analyzer
from data.data_fetcher import MockDataGenerator

analyzer = get_analyzer()
df = MockDataGenerator.generate_mock_daily_data("000001.SZ", 30)
df_indicators = analyzer.calculate_all_indicators(df)
signals = analyzer.get_signal(df_indicators, "000001.SZ")
print(f"信号：{signals['overall_signal']}")
```

---

## 🐳 Docker 部署

### 使用 Docker Compose（推荐）

```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f ai-stock-monitor

# 停止
docker-compose down
```

### 单 Docker 容器

```bash
# 构建镜像
docker build -t ai-stock-monitor .

# 运行容器
docker run -d -p 8501:8501 --name stock-monitor ai-stock-monitor
```

---

## 📈 模拟交易

### 功能特点
- ✅ 虚拟资金 100 万
- ✅ 支持买卖操作
- ✅ 自动计算费用（佣金、印花税）
- ✅ 持仓管理
- ✅ 盈亏统计

### 操作流程
1. 选择股票
2. 查看技术分析和 AI 建议
3. 执行买卖操作
4. 查看持仓和盈亏

---

## 🔍 告警系统

### 支持告警类型
- ⚠️ **价格涨跌幅:** 超过 5% 触发
- 📈 **成交量放大:** 超过 2 倍触发
- 📉 **趋势告警:** 强烈下跌信号触发
- 📊 **价格阈值:** 低于/高于指定价格

### 配置告警阈值
```python
ALERT_THRESHOLDS = {
    "price_change_percent": 5.0,  # 涨跌幅超过 5%
    "volume_increase": 2.0,       # 成交量放大 2 倍
    "min_price": 1.0,             # 最低价格阈值
}
```

---

## 📝 日志管理

### 日志文件位置
- `logs/monitor.log` - 主日志
- `logs/data.log` - 数据日志
- `logs/analysis.log` - 分析日志
- `logs/trading.log` - 交易日志
- `logs/ui.log` - UI 日志

### 日志级别
```python
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
```

---

## 🛠️ 扩展开发

### 添加新指标
1. 在 `analyzer/tech_analyzer.py` 添加计算方法
2. 在 `TECH_ANALYSIS_PARAMS` 添加参数配置

### 自定义告警逻辑
1. 继承 `StockMonitor` 类
2. 重写 `check_XXX_alert` 方法
3. 在 `stock_monitor.py` 中注册回调

### 集成其他数据源
1. 继承 `TushareFetcher` 类
2. 实现数据获取接口
3. 在 `settings.py` 中配置新数据源

---

## 📚 技术栈

| 类别 | 技术 |
|------|------|
| **数据分析** | pandas, numpy, ta-lib |
| **AI 引擎** | Ollama (llama3.2, qwen2.5, mistral) |
| **Web 界面** | Streamlit, Plotly |
| **数据库** | SQLite (本地) |
| **网络请求** | requests |
| **日志** | Python logging |

---

## 🌐 支持的 Ollama 模型

| 模型 | 大小 | 特点 |
|------|------|------|
| **llama3.2** | 3B/11B | Meta 出品，性能优秀 |
| **qwen2.5** | 0.5B-72B | 阿里云，中文优化 |
| **mistral** | 7B | 推理快速，逻辑强 |
| **gemma** | 2B/7B | Google，轻量级 |
| **phi3** | 3.8B | 微软，小模型大能力 |

---

## ⚠️ 注意事项

### 数据安全
- ✅ **全本地运行** - 数据不上传云端
- ✅ **SQLite 本地存储** - 隐私安全
- ⚠️ **不要使用真实交易** - 仅限模拟

### 性能优化
- 定期清理缓存（24 小时过期）
- 限制数据获取天数（默认 30 天）
- 监控日志文件大小（10MB 自动轮转）

### 使用建议
1. **先使用模拟数据测试** 功能
2. **配置 Tushare token** 获取真实数据
3. **选择合适的 Ollama 模型** - 推荐 llama3.2 或 qwen2.5
4. **定期备份数据** - SQLite 数据库文件

---

## 📊 项目进度

- [x] 项目结构设计
- [x] 数据模块
- [x] 技术分析模块
- [x] AI 分析模块
- [x] 盯盘监控模块
- [x] 模拟交易模块
- [x] Web UI 界面
- [x] 启动脚本
- [x] Docker 部署
- [x] 完整文档

---

## 🙏 致谢

- **Ollama** - 本地大模型推理平台
- **Tushare** - 股票数据接口
- **Streamlit** - Web 应用框架
- **Plotly** - 交互式图表库

---

## 📄 许可证

MIT License - 自由使用和修改

---

## 📮 联系方式

如有问题或建议，欢迎提交 Issue 或 Pull Request。

---

**🚀 立即开始你的本地 AI 股票分析之旅！**
