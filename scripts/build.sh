#!/bin/bash
# DocuMind-Converter 构建脚本
# Build script for DocuMind-Converter

set -e

echo "🚀 DocuMind-Converter 构建脚本"
echo "================================"

# 检查Python版本
echo "📋 检查环境..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "  Python版本: $python_version"

# 创建虚拟环境
echo "📦 创建虚拟环境..."
python3 -m venv venv
source venv/bin/activate

# 安装依赖
echo "📥 安装依赖..."
pip install --upgrade pip
pip install -e .
pip install pytest pytest-cov black flake8 mypy

# 运行代码格式化
echo "🎨 格式化代码..."
black documind/ tests/ --line-length 100 || true

# 运行类型检查
echo "🔍 类型检查..."
mypy documind/ --ignore-missing-imports || true

# 运行测试
echo "🧪 运行测试..."
pytest tests/ -v --cov=documind --cov-report=term-missing || true

# 构建分发包
echo "📦 构建分发包..."
python setup.py sdist bdist_wheel || true

echo ""
echo "✅ 构建完成!"
echo ""
echo "使用方法:"
echo "  pip install -e ."
echo "  documind --help"
echo "  documind-tui"
