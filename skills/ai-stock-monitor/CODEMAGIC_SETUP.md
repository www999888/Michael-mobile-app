# 🚀 Codemagic 配置指南

## 📋 项目信息

**项目名称:** AI Stock Monitor  
**Git 仓库:** https://github.com/www999888/Michael-mobile-app  
**Codemagic 项目:** www999888/Michael-mobile-app  
**文档:** skills/ai-stock-monitor/

---

## 🎯 Codemagic 工作流概览

### 工作流 1: CI Build & Test
**名称:** `ai-stock-monitor-ci`  
**触发:** push, tag, pull_request  
**平台:** macOS (mac_mini_m2)  
**Python:** 3.11

**功能:**
- ✅ 环境检测 (Python, pip)
- ✅ 虚拟环境创建
- ✅ 依赖安装
- ✅ 完整测试套件 (test_all.py)
- ✅ 代码质量检查 (Black, Flake8)
- ✅ 项目结构验证

**输出:**
- 📊 测试报告
- 📈 代码覆盖率
- 📁 构建产物

### 工作流 2: PyPI Release
**名称:** `ai-stock-monitor-pypi`  
**触发:** Git 标签 (release/*)  
**Python:** 3.11

**功能:**
- ✅ 版本检测
- ✅ 构建 Python 包 (wheel, sdist)
- ✅ TestPyPI 测试发布
- ✅ PyPI 生产发布

**前提:**
- 📦 PYPI_USERNAME
- 🔐 PYPI_PASSWORD

### 工作流 3: Docker Build & Push
**名称:** `ai-stock-monitor-docker`  
**触发:** Git 标签 (release/*)  
**Python:** 3.11  
**Docker:** latest

**功能:**
- ✅ Docker 环境检测
- ✅ Docker 登录
- ✅ 镜像构建 (多标签)
- ✅ 镜像推送 (Docker Hub + Codemagic Registry)
- ✅ 生成 Docker Compose 文件

**输出:**
- 🐳 Docker 镜像
- 📝 docker-compose.yml

### 工作流 4: GitHub Release
**名称:** `ai-stock-monitor-github-release`  
**触发:** Git 标签 (release/*)  
**Python:** 3.11

**功能:**
- ✅ GitHub 环境检查
- ✅ CHANGELOG 生成
- ✅ GitHub Release 创建
- ✅ 资产上传

**前提:**
- 🔑 GITHUB_TOKEN (repo, contents 权限)

---

## ⚙️ 配置步骤

### Step 1: 连接到 Git 仓库

1. 登录 Codemagic
2. 点击 "Start building for free"
3. 选择 GitHub 登录
4. 授予仓库访问权限
5. 选择仓库：`www999888/Michael-mobile-app`

### Step 2: 配置环境变量

在 Codemagic 平台:
1. 进入项目 → Settings → Environment variables
2. 添加以下变量:

| 变量名 | 说明 | 是否敏感 |
|--------|------|---------|
| PYPI_USERNAME | PyPI 用户名 | ❌ |
| PYPI_PASSWORD | PyPI API Token | ✅ |
| DOCKER_USERNAME | Docker Hub 用户名 | ❌ |
| DOCKER_PASSWORD | Docker Access Token | ✅ |
| DOCKER_EMAIL | Docker 邮箱 | ❌ |
| GITHUB_TOKEN | GitHub Personal Access Token | ✅ |
| TUSHARE_TOKEN | Tushare API Token | ✅ |
| SLACK_WEBHOOK_URL | Slack Webhook URL | ✅ |

**敏感信息标记:** 勾选 "Secure variable" (加密存储)

### Step 3: 上传配置文件

1. 将 `.codemagic.yaml` 上传到仓库根目录
2. 确保文件内容正确
3. 推送到远程仓库

### Step 4: 测试工作流

#### 测试 CI Build & Test
```bash
# 推送代码到 master
git push origin master
```

#### 测试 PyPI Release
```bash
# 创建测试标签
git tag v0.0.1-test
git push origin v0.0.1-test
```

#### 测试 Docker Build
```bash
# 创建发布标签
git tag v1.0.0
git push origin v1.0.0
```

---

## 📊 工作流配置详解

### Python 环境配置

```yaml
environment:
  python: 3.11
  env:
    - PYTHONIOENCODING: UTF-8
    - PYTHONUTF8: 1
    - LC_ALL: en_US.UTF-8
```

### 触发器配置

```yaml
triggering:
  events:
    - push
    - tag
    - pull_request
  branch_patterns:
    - pattern: master
      include: true
    - pattern: release/*
      include: true
```

### 脚本步骤

```yaml
scripts:
  - name: 环境检查
    script: |
      echo "Python version: $PYTHON_VERSION"
      python --version
      pip --version
      python -m venv venv
      source venv/bin/activate
      pip install -r requirements.txt
      python test_all.py
```

### 艺术制品配置

```yaml
artifacts:
  - build/**
  - dist/*.whl
  - dist/*.tar.gz
  - coverage.xml
  - .codemagic/**
```

### 发布配置

```yaml
publishing:
  email:
    recipients:
      - admin@example.com
      - devops@example.com
    notifications:
      - success
      - failure
  slack:
    notifications:
      - success
      - failure
    channel: "#ai-stock-monitor-builds"
```

---

## 🔍 故障排查

### 问题 1: 环境变量未生效

**症状:** 脚本中使用变量时报错
**解决:**
1. 检查变量是否设置为 "Secure variable"
2. 确认变量名称正确
3. 重启构建

### 问题 2: PyPI 上传失败

**症状:** `twine upload` 失败
**解决:**
1. 检查 PYPI_PASSWORD 是否正确
2. 验证 Token 权限
3. 检查版本号是否已存在

### 问题 3: Docker 镜像推送失败

**症状:** `docker push` 失败
**解决:**
1. 检查 DOCKER_USERNAME 和 DOCKER_PASSWORD
2. 验证 Docker Hub 权限
3. 检查 Docker 版本兼容性

### 问题 4: GitHub Release 创建失败

**症状:** `gh release create` 失败
**解决:**
1. 检查 GITHUB_TOKEN 权限
2. 确认仓库名称正确
3. 验证 Git 标签是否存在

---

## 📈 监控和告警

### 构建状态监控

1. **Codemagic Dashboard**
   - 实时查看构建状态
   - 构建历史
   - 构建时长统计

2. **Slack 通知**
   - 构建开始
   - 构建成功
   - 构建失败
   - 始终通知

3. **邮件通知**
   - 配置收件人
   - 选择通知类型
   - 过滤条件

### 日志管理

```bash
# 查看构建日志
https://codemagic.io/workspace/{workspace_id}/builds

# 下载日志文件
- .codemagic/build_log.txt
- .codemagic/test_results/**
- .codemagic/docker_logs/**
```

---

## 🎯 最佳实践

### 1. 小步快跑
- ✅ 频繁提交小改动
- ✅ 每次提交触发测试
- ✅ 快速发现问题

### 2. 自动化测试
- ✅ 所有测试自动化
- ✅ 覆盖核心功能
- ✅ 测试覆盖率监控

### 3. 版本控制
- ✅ 语义化版本
- ✅ Git 标签管理
- ✅ CHANGELOG 维护

### 4. 安全优先
- ✅ 使用环境变量存储敏感信息
- ✅ Token 最小权限
- ✅ .env 文件 gitignore

### 5. 持续优化
- ✅ 监控构建时长
- ✅ 优化缓存策略
- ✅ 定期清理旧构建

---

## 📞 支持资源

### Codemagic 文档
- [官方文档](https://docs.codemagic.io)
- [YAML 配置参考](https://docs.codemagic.io/yaml/basics)
- [环境变量管理](https://docs.codemagic.io/yaml/environment-variables)
- [工作流配置](https://docs.codemagic.io/yaml/workflows)

### 社区支持
- [Codemagic Discord](https://discord.gg/codemagic)
- [GitHub Issues](https://github.com/codemium/codemagic-cli-agent/issues)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/codemagic)

---

## 🚀 快速开始

### 1. 上传 .codemagic.yaml
```bash
cd skills/ai-stock-monitor
git add .codemagic.yaml
git commit -m "Add Codemagic configuration"
git push origin master
```

### 2. 配置环境变量
访问 Codemagic 平台 → Settings → Environment variables

### 3. 触发首次构建
```bash
# 推送代码触发 CI
git push origin master
```

### 4. 查看结果
- Codemagic Dashboard
- Slack 通知
- 邮件通知

---

**祝你使用 Codemagic 愉快！** 🎉

*更新时间：2026-03-27*
