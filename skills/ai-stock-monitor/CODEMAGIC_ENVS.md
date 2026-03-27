# Codemagic 环境变量配置
# 在 Codemagic 平台的 Settings > Environment variables 中配置
# 不要将敏感信息提交到版本控制！

# === PyPI 发布环境变量 ===
PYPI_USERNAME: your-pypi-username
PYPI_PASSWORD: your-pypi-api-token
# 获取方式：https://pypi.org/help/#apitoken

# === Docker 环境变量 ===
DOCKER_USERNAME: your-docker-username
DOCKER_PASSWORD: your-docker-password
DOCKER_EMAIL: your-email@example.com
# 获取方式：Docker Hub > Account Settings > Access Tokens

# === GitHub 环境变量 ===
GITHUB_TOKEN: your-github-token
# 获取方式：GitHub > Settings > Developer settings > Personal access tokens
# 权限：repo (仓库访问), contents (release 创建)

# === Slack 通知环境变量 ===
SLACK_WEBHOOK_URL: https://hooks.slack.com/services/YOUR/WEBHOOK/URL
# 获取方式：Slack > Custom Integrations > Incoming Webhooks

# === 项目特定环境变量 ===
TUSHARE_TOKEN: your-tushare-token
# 获取方式：https://tushare.pro 注册获取免费 token

# === 其他配置 ===
# STREAMLIT_SERVER_PORT: 8501
# OLLAMA_BASE_URL: http://localhost:11434

# === 本地开发测试环境变量 ===
# 在本地开发时可以使用 .env 文件
# .env 文件已添加到 .gitignore
