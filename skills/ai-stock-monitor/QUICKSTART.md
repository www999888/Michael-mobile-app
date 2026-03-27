# 🚀 AI Stock Monitor - 快速开始指南

> **完全本地运行 | Ollama 本地 AI 分析 | 无云端依赖**

---

## 📦 1. 安装准备

### 环境要求
- ✅ Python 3.9+
- ✅ Ollama 服务运行中
- ✅ 推荐模型：llama3.2 或 qwen2.5

### 检查环境
```bash
# 检查 Python
python --version  # 应显示 3.9+

# 检查 Ollama
ollama list  # 应显示已安装的模型
```

### 安装 Ollama 模型（如果还没有）
```bash
# 启动 Ollama
ollama serve

# 拉取推荐模型（选择一个）
ollama pull llama3.2
ollama pull qwen2.5
ollama pull mistral
```

---

## 🔧 2. 安装步骤

### 方式 A: Windows 快速启动
```bash
# 进入项目目录
cd skills/ai-stock-monitor

# 运行 Windows 启动脚本
run.bat
```

### 方式 B: Linux/Mac 快速启动
```bash
# 进入项目目录
cd skills/ai-stock-monitor

# 运行启动脚本
chmod +x run.sh
./run.sh
```

### 方式 C: 手动安装
```bash
# 1. 创建虚拟环境
python -m venv venv

# 2. 激活虚拟环境
# Linux/Mac:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 启动应用
python main.py web
```

---

## 🌐 3. 启动应用

### 启动 Web UI（推荐）
```bash
python main.py web
```
浏览器访问：`http://localhost:8501`

### 启动快速演示
```bash
python main.py demo
```

### 启动后台监控
```bash
python main.py monitor
```

---

## 🎯 4. 使用指南

### 4.1 查看股票详情
1. 从左侧选择股票（默认：000001.SZ）
2. 点击"股票详情"
3. 查看 K 线图和技术指标

### 4.2 AI 分析
1. 点击"AI 分析"标签
2. 系统自动加载本地 AI 模型
3. 查看 AI 生成的分析报告
4. 获取交易建议

### 4.3 模拟交易
1. 点击"模拟交易"标签
2. 输入交易数量和价格
3. 点击"买入"或"卖出"
4. 查看持仓和盈亏

### 4.4 实时监控
1. 点击"▶️ 启动监控"
2. 设置监控间隔（默认 60 秒）
3. 查看实时告警

---

## 📊 5. 核心功能

### 技术分析
- ✅ MA（移动平均线）
- ✅ MACD（平滑异同移动平均线）
- ✅ KDJ（随机指标）
- ✅ RSI（相对强弱指标）
- ✅ BOLL（布林带）

### AI 分析能力
- 🔍 趋势判断
- 📈 动能分析
- 💡 买卖点建议
- ⚠️ 风险评估

### 模拟交易
- 💰 虚拟资金：100 万
- 📊 盈亏统计
- 📈 持仓管理
- 💳 费用计算

---

## 🔍 6. 测试验证

### 运行完整测试
```bash
python test_all.py
```

### 检查测试项目
- ✅ 数据获取
- ✅ 数据存储
- ✅ 技术分析
- ✅ AI 分析
- ✅ 监控模块
- ✅ 模拟交易

---

## 📋 7. 常见问题

### Q1: Ollama 模型未找到
```bash
# 检查 Ollama 是否运行
ollama list

# 拉取模型
ollama pull llama3.2
```

### Q2: 依赖安装失败
```bash
# 更新 pip
pip install --upgrade pip

# 使用国内镜像（可选）
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q3: Web UI 无法访问
```bash
# 检查端口是否被占用
netstat -ano | findstr :8501  # Windows
lsof -i :8501                 # Linux/Mac

# 修改端口
python main.py web --port 8502
```

### Q4: 中文乱码问题
```bash
# 设置环境变量
set PYTHONIOENCODING=utf-8  # Windows
export PYTHONIOENCODING=utf-8  # Linux/Mac
```

---

## 🐳 8. Docker 部署

### 快速部署
```bash
# 构建镜像
docker build -t ai-stock-monitor .

# 运行容器
docker run -d -p 8501:8501 --name stock-monitor ai-stock-monitor
```

### Docker Compose（推荐）
```bash
# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f ai-stock-monitor

# 停止服务
docker-compose down
```

---

## 📁 9. 项目结构

```
ai-stock-monitor/
├── config/              # 配置文件
├── data/               # 数据模块
├── analyzer/           # 分析模块
├── monitor/            # 监控模块
├── trader/             # 交易模块
├── ui/                 # Web UI
├── logs/               # 日志
├── data_storage/       # 数据库
├── main.py             # 主程序
├── requirements.txt    # 依赖
├── Dockerfile          # Docker 镜像
├── run.sh / run.bat    # 启动脚本
└── README.md           # 完整文档
```

---

## 📚 10. 后续步骤

### 推荐操作
1. ✅ 完成快速测试验证
2. ✅ 查看 Web UI 界面
3. ✅ 尝试 AI 分析功能
4. ✅ 了解配置说明

### 深入学习
- 📖 阅读 `README_DETAILED.md` 完整文档
- 🔧 了解 `settings.py` 配置说明
- 🎨 自定义技术指标参数
- 🤖 集成其他数据源

---

## 🎉 开始使用！

现在你已经完成了所有准备步骤，可以：

1. **启动 Web UI** - 开始股票分析之旅
2. **查看 AI 分析** - 体验本地大模型智能分析
3. **模拟交易** - 测试投资策略
4. **实时监控** - 设置告警系统

祝投资顺利！📈💰

---

**提示：** 如需详细文档，请查看 `README_DETAILED.md`
