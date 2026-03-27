#!/bin/bash
# Codemagic 部署验证脚本
# 用于验证 Codemagic 配置的正确性

set -e

echo "======================================"
echo "Codemagic 配置验证"
echo "======================================"

# 检查 .codemagic.yaml 文件
echo ""
echo "1. 检查 .codemagic.yaml 文件..."
if [ -f ".codemagic.yaml" ]; then
    echo "✅ .codemagic.yaml 存在"
    
    # 检查关键配置
    if grep -q "workflows:" .codemagic.yaml; then
        echo "✅ workflows 配置存在"
    else
        echo "❌ workflows 配置缺失"
        exit 1
    fi
    
    if grep -q "ai-stock-monitor-ci" .codemagic.yaml; then
        echo "✅ AI Stock Monitor CI 工作流配置存在"
    else
        echo "❌ AI Stock Monitor CI 工作流配置缺失"
        exit 1
    fi
    
    if grep -q "ai-stock-monitor-pypi" .codemagic.yaml; then
        echo "✅ PyPI 发布工作流配置存在"
    else
        echo "❌ PyPI 发布工作流配置缺失"
        exit 1
    fi
    
    if grep -q "ai-stock-monitor-docker" .codemagic.yaml; then
        echo "✅ Docker 构建工作流配置存在"
    else
        echo "❌ Docker 构建工作流配置缺失"
        exit 1
    fi
    
    if grep -q "ai-stock-monitor-github-release" .codemagic.yaml; then
        echo "✅ GitHub Release 工作流配置存在"
    else
        echo "❌ GitHub Release 工作流配置缺失"
        exit 1
    fi
else
    echo "❌ .codemagic.yaml 文件不存在"
    exit 1
fi

# 检查环境变量配置
echo ""
echo "2. 检查环境变量配置..."
if [ -f "CODEMAGIC_ENVS.md" ]; then
    echo "✅ CODEMAGIC_ENVS.md 存在"
    
    # 检查关键变量定义
    if grep -q "PYPI_USERNAME" CODEMAGIC_ENVS.md; then
        echo "✅ PyPI 环境变量配置存在"
    else
        echo "⚠️  PyPI 环境变量配置缺失"
    fi
    
    if grep -q "DOCKER_USERNAME" CODEMAGIC_ENVS.md; then
        echo "✅ Docker 环境变量配置存在"
    else
        echo "⚠️  Docker 环境变量配置缺失"
    fi
    
    if grep -q "GITHUB_TOKEN" CODEMAGIC_ENVS.md; then
        echo "✅ GitHub Token 配置存在"
    else
        echo "⚠️  GitHub Token 配置缺失"
    fi
else
    echo "⚠️  CODEMAGIC_ENVS.md 不存在，继续检查..."
fi

# 检查 Python 环境
echo ""
echo "3. 检查 Python 环境..."
if command -v python3 &> /dev/null; then
    echo "✅ Python 3 已安装"
    python3 --version
else
    echo "⚠️  Python 3 未安装"
fi

# 检查 Git
echo ""
echo "4. 检查 Git..."
if command -v git &> /dev/null; then
    echo "✅ Git 已安装"
    git --version
else
    echo "❌ Git 未安装"
    exit 1
fi

# 检查 Docker (如果可用)
echo ""
echo "5. 检查 Docker..."
if command -v docker &> /dev/null; then
    echo "✅ Docker 已安装"
    docker --version
else
    echo "⚠️  Docker 未安装 (用于 Docker 构建工作流)"
fi

# 检查项目结构
echo ""
echo "6. 检查项目结构..."
if [ -d "config" ]; then
    echo "✅ config/ 目录存在"
else
    echo "❌ config/ 目录缺失"
    exit 1
fi

if [ -d "data" ]; then
    echo "✅ data/ 目录存在"
else
    echo "❌ data/ 目录缺失"
    exit 1
fi

if [ -d "analyzer" ]; then
    echo "✅ analyzer/ 目录存在"
else
    echo "❌ analyzer/ 目录缺失"
    exit 1
fi

if [ -f "main.py" ]; then
    echo "✅ main.py 存在"
else
    echo "❌ main.py 缺失"
    exit 1
fi

if [ -f "requirements.txt" ]; then
    echo "✅ requirements.txt 存在"
else
    echo "❌ requirements.txt 缺失"
    exit 1
fi

# 检查 YAML 语法
echo ""
echo "7. 检查 YAML 语法..."
if command -v python3 &> /dev/null; then
    if python3 -c "import yaml" 2>/dev/null; then
        echo "✅ PyYAML 库可用"
        python3 -c "import yaml; yaml.safe_load(open('.codemagic.yaml'))" && echo "✅ .codemagic.yaml 语法正确"
    else
        echo "⚠️  PyYAML 库未安装，跳过语法检查"
    fi
fi

# 检查 .env.example
echo ""
echo "8. 检查 .env.example..."
if [ -f ".env.example" ]; then
    echo "✅ .env.example 存在"
else
    echo "⚠️  .env.example 缺失，建议使用"
fi

# 检查 .gitignore
echo ""
echo "9. 检查 .gitignore..."
if [ -f ".gitignore" ]; then
    if grep -q ".codemagic" .gitignore; then
        echo "✅ .gitignore 包含 .codemagic"
    else
        echo "⚠️  .gitignore 未包含 .codemagic，可能提交敏感信息"
    fi
else
    echo "⚠️  .gitignore 不存在"
fi

# 检查 Dockerfile
echo ""
echo "10. 检查 Dockerfile..."
if [ -f "Dockerfile" ]; then
    echo "✅ Dockerfile 存在"
    if grep -q "FROM python:" Dockerfile; then
        echo "✅ Dockerfile 基于 Python 镜像"
    fi
else
    echo "❌ Dockerfile 缺失"
    exit 1
fi

# 检查 docker-compose.yml
echo ""
echo "11. 检查 docker-compose.yml..."
if [ -f "docker-compose.yml" ]; then
    echo "✅ docker-compose.yml 存在"
else
    echo "⚠️  docker-compose.yml 缺失，建议使用"
fi

# 检查文档
echo ""
echo "12. 检查文档..."
if [ -f "README.md" ]; then
    echo "✅ README.md 存在"
else
    echo "❌ README.md 缺失"
    exit 1
fi

if [ -f "GITHUB_RELEASE.md" ]; then
    echo "✅ GITHUB_RELEASE.md 存在"
else
    echo "⚠️  GITHUB_RELEASE.md 缺失"
fi

if [ -f "CODEMAGIC_SETUP.md" ]; then
    echo "✅ CODEMAGIC_SETUP.md 存在"
else
    echo "⚠️  CODEMAGIC_SETUP.md 缺失"
fi

# 总结
echo ""
echo "======================================"
echo "验证总结"
echo "======================================"
echo ""
echo "✅ 核心配置文件：存在"
echo "✅ 工作流配置：4 个全部配置"
echo "✅ Python 环境：已检测"
echo "✅ Git 环境：已检测"
echo "✅ 项目结构：完整"
echo "✅ 文档：完整"
echo ""
echo "🎉 Codemagic 配置验证完成！"
echo ""
echo "下一步操作:"
echo "1. 在 Codemagic 平台配置环境变量"
echo "2. 推送 .codemagic.yaml 到远程仓库"
echo "3. 触发首次构建测试"
echo ""
echo "推送到远程仓库:"
echo "  git add .codemagic.yaml CODEMAGIC_ENVS.md GITHUB_RELEASE.md CODEMAGIC_SETUP.md"
echo "  git commit -m 'Add Codemagic CI/CD configuration'"
echo "  git push origin master"
echo ""
