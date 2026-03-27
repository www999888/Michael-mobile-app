# 📦 GitHub Release 指南

## 🎯 发布流程

### 1. 准备发布

#### 步骤 1: 检查代码质量
```bash
# 运行完整测试
python test_all.py

# 检查代码质量
black --check .
flake8 .
```

#### 步骤 2: 更新版本号
编辑以下文件中的版本号：
- `analyzer/__init__.py` - `__version__ = "X.Y.Z"`
- `main.py` - 如果定义了版本号
- `README.md` - 版本号更新

#### 步骤 3: 更新 CHANGELOG.md
在 `CHANGELOG.md` 中添加本次更新的说明：
```markdown
## [X.Y.Z] - YYYY-MM-DD
### 添加
- 新功能描述

### 修改
- 修改描述

### 修复
- 修复描述
```

### 2. 创建 Git 标签

#### 版本命名规则
- 语义化版本：`v1.0.0`
- 发布分支：`release/v1.0.0`

#### 创建标签
```bash
# 确保代码已提交
git add .
git commit -m "v1.0.0 - 准备发布"

# 创建标签
git tag v1.0.0

# 推送标签到远程仓库
git push origin v1.0.0

# 推送 release 分支
git push origin release/v1.0.0
```

### 3. Codemagic 自动发布

#### 触发自动发布
当 Git 标签推送到仓库后，Codemagic 会自动触发发布流程：

1. **AI Stock Monitor - PyPI Release**
   - 构建 Python 包
   - 上传到 TestPyPI
   - 上传到 PyPI（需要生产 token）

2. **AI Stock Monitor - Docker Build & Push**
   - 构建 Docker 镜像
   - 推送到 Docker Hub
   - 生成 Docker Compose 文件

3. **AI Stock Monitor - GitHub Release**
   - 创建 GitHub Release
   - 上传发布资产
   - 自动生成 CHANGELOG

### 4. 验证发布

#### 检查 PyPI
```bash
# 访问 PyPI 页面
https://pypi.org/project/ai-stock-monitor/v1.0.0/

# 测试安装
pip install ai-stock-monitor
```

#### 检查 Docker Hub
```bash
# 拉取最新镜像
docker pull ai-stock-monitor:v1.0.0

# 运行测试
docker run -p 8501:8501 ai-stock-monitor:v1.0.0
```

#### 检查 GitHub Release
```bash
# 访问 GitHub 页面
https://github.com/www999888/Michael-mobile-app/releases

# 下载 Release 资产
# - ai-stock-monitor-docs-v1.0.0.zip
# - ai-stock-monitor-src-v1.0.0.zip
```

---

## 📋 发布清单

### 发布前检查
- [ ] 所有测试通过
- [ ] 代码质量检查通过
- [ ] 版本号已更新
- [ ] CHANGELOG 已更新
- [ ] 文档已更新

### 发布后验证
- [ ] PyPI 发布成功
- [ ] Docker 镜像已推送
- [ ] GitHub Release 创建成功
- [ ] 安装测试成功
- [ ] 运行测试成功

### 通知相关人员
- [ ] 邮件通知
- [ ] Slack 通知
- [ ] 更新内部文档

---

## 🚀 自动化工作流

### Codemagic 自动触发规则

| 事件 | 分支 | 触发工作流 |
|------|------|------------|
| Git 标签推送到 `release/*` | release/* | ✅ PyPI, Docker, GitHub Release |
| Git 标签推送到 `master` | master | ✅ PyPI, Docker, GitHub Release |
| Git 标签推送到 `develop` | develop | ✅ CI Build & Test |

### 手动触发发布

在 Codemagic 平台：
1. 进入项目：`www999888/Michael-mobile-app`
2. 选择 "Workflows"
3. 点击要发布的工作流
4. 点击 "Start build"
5. 选择触发方式 (tag/push)

---

## 🛡️ 安全注意事项

### Token 管理
- ✅ 所有敏感信息存储在 Codemagic Environment Variables
- ✅ .env 文件已添加到 .gitignore
- ✅ 不要将 Token 硬编码到代码中

### 访问控制
- ✅ PyPI Token 仅用于发布
- ✅ GitHub Token 最小权限 (repo, contents)
- ✅ Docker Token 仅用于推送镜像

### 版本控制
- ✅ 使用语义化版本 (SemVer)
- ✅ 每次发布创建 Git 标签
- ✅ 维护 CHANGELOG.md

---

## 📚 相关文档

- [Codemagic 文档](https://docs.codemagic.io)
- [PyPI 文档](https://pypi.org/help/#apitoken)
- [Docker Hub 文档](https://docs.docker.com/docker-hub/)
- [GitHub API 文档](https://docs.github.com/en/rest)

---

**祝你发布顺利！** 🎉

*更新时间：2026-03-27*
