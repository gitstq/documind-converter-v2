<div align="center">

# 🧠 DocuMind-Converter

**轻量级AI文档智能转换与结构化提取引擎**

*Lightweight AI Document Intelligent Conversion & Structured Extraction Engine*

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Zero Dependencies](https://img.shields.io/badge/Zero-Dependencies-orange)](setup.py)
[![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen)]()

[English](#english) | [简体中文](#简体中文) | [繁體中文](#繁體中文)

</div>

---

## 简体中文

### 🎉 项目介绍

DocuMind-Converter 是一款**零依赖**的轻量级AI文档智能转换与结构化提取引擎，专为开发者、内容创作者和数据处理专家设计。

**灵感来源**：本项目受到微软 [markitdown](https://github.com/microsoft/markitdown) 项目的启发，但采用了完全不同的技术路线——我们追求**极致轻量**和**零依赖**，让文档转换不再受困于复杂的依赖链。

**核心价值**：
- 🚀 **零依赖架构** - 纯Python标准库实现，无需安装任何第三方包
- 🤖 **AI智能分析** - 内置关键词提取、摘要生成、实体识别等智能功能
- 🔄 **多格式互转** - 支持 Markdown ↔ HTML ↔ JSON ↔ YAML ↔ Plain 双向转换
- 📊 **结构化输出** - 不仅转换格式，更提取文档结构、生成目录、识别关键信息
- 🖥️ **交互式TUI** - 提供美观的终端交互界面，零学习成本
- 📁 **批量处理** - 支持文件夹批量转换、通配符匹配、并行处理

### ✨ 核心特性

| 特性 | 描述 | 状态 |
|------|------|------|
| 📝 **多格式支持** | Markdown/HTML/JSON/YAML/CSV/XML/RST/Org-mode | ✅ 已支持 |
| 🧠 **智能分析** | 关键词提取、摘要生成、可读性分析 | ✅ 已支持 |
| 🔍 **实体识别** | 自动识别邮箱、URL、IP、日期、版本号 | ✅ 已支持 |
| 📑 **目录生成** | 自动生成文档目录(TOC) | ✅ 已支持 |
| 🎨 **多主题** | Default/Minimal/Fancy 三种输出主题 | ✅ 已支持 |
| 📊 **增强报告** | 结构化分析报告，包含统计和可读性评分 | ✅ 已支持 |
| 🖥️ **TUI界面** | 交互式终端界面，菜单驱动 | ✅ 已支持 |
| 📁 **批量处理** | 文件夹批量转换、并行处理 | ✅ 已支持 |
| 🔄 **管道模式** | 支持自定义处理管道链 | ✅ 已支持 |
| 🌐 **中英文支持** | 完整的中英文文档内容处理 | ✅ 已支持 |

### 🚀 快速开始

#### 环境要求

- **Python**: 3.10 或更高版本
- **操作系统**: Windows / macOS / Linux

#### 安装

```bash
# 从源码安装
git clone https://github.com/gitstq/documind-converter-v2.git
cd documind-converter-v2
pip install -e .

# 或使用 pip (即将发布)
pip install documind-converter
```

#### 基本使用

```bash
# 单文件转换
documind convert input.md -o output.html -f html

# 批量转换
documind batch "docs/*.md" -o out/ -f json

# 文档分析
documind analyze document.md -o report.txt

# 查看文档信息
documind info document.md

# 交互式TUI界面
documind-tui
```

#### Python API

```python
from documind import DocumentConverter, StructureExtractor, BatchPipeline

# 单文件转换
converter = DocumentConverter()
result = converter.convert('input.md', output_format='html', output_path='output.html')

# 文档分析
extractor = StructureExtractor()
analysis = extractor.analyze_document(open('doc.md').read())
print(f"关键词: {[kw[0] for kw in analysis['keywords'][:5]]}")
print(f"摘要: {analysis['summary']}")

# 批量转换
pipeline = BatchPipeline()
results = pipeline.batch_convert('docs/*.md', 'output/', 'html')
```

### 📖 详细使用指南

#### 命令行界面

```bash
# 转换格式
documind convert input.md -o output.html -f html --theme fancy

# 分析文档
documind analyze paper.md -o analysis.report -f report

# 批量处理
documind batch "**/*.md" -o converted/ -f structured -j 8

# 查看帮助
documind --help
documind convert --help
```

#### 支持的格式

**输入格式**: `.md`, `.markdown`, `.txt`, `.html`, `.htm`, `.json`, `.yaml`, `.yml`, `.csv`, `.xml`, `.rst`, `.org`

**输出格式**: `markdown`, `html`, `json`, `yaml`, `plain`, `structured`

#### 高级配置

```python
from documind import DocumentConverter, OutputFormatter

# 自定义配置
config = {
    'min_keyword_length': 3,
    'max_keywords': 30,
    'format': {
        'theme': 'fancy',
        'include_toc': True,
        'include_stats': True
    }
}

converter = DocumentConverter(config)
formatter = OutputFormatter(theme='fancy', config=config['format'])
```

### 💡 设计思路与迭代规划

#### 技术选型原因

- **纯标准库实现**: 消除依赖地狱，确保在任何Python环境中开箱即用
- **模块化架构**: Converter/Extractor/Formatter/Pipeline 四层分离，易于扩展
- **规则+统计混合**: 轻量级NLP实现，无需重型ML框架即可实现智能分析

#### 后续迭代计划

- [ ] v1.1.0: 支持 PDF/Word/Excel 解析（基于纯Python实现）
- [ ] v1.2.0: 集成 LLM API 进行智能摘要和翻译
- [ ] v1.3.0: 支持插件系统，允许自定义转换器
- [ ] v2.0.0: Web UI 界面，支持在线文档处理

### 📦 打包与部署

```bash
# 构建分发包
python setup.py sdist bdist_wheel

# 本地安装
pip install -e .

# 运行测试
pytest tests/ -v

# 代码格式化
black documind/ tests/ --line-length 100
```

### 🤝 贡献指南

欢迎提交 Issue 和 PR！

- 提交 Issue 请描述清楚问题和复现步骤
- 提交 PR 请确保通过所有测试
- 遵循 PEP 8 代码规范

### 📄 开源协议

本项目采用 [MIT 协议](LICENSE) 开源。

---

## English

### 🎉 Introduction

DocuMind-Converter is a **zero-dependency** lightweight AI document intelligent conversion and structured extraction engine, designed for developers, content creators, and data processing professionals.

**Inspiration**: This project is inspired by Microsoft's [markitdown](https://github.com/microsoft/markitdown), but takes a completely different technical approach — we pursue **extreme lightweight** and **zero dependencies**, making document conversion free from complex dependency chains.

**Core Values**:
- 🚀 **Zero Dependency** - Pure Python standard library, no third-party packages needed
- 🤖 **AI Smart Analysis** - Built-in keyword extraction, summary generation, entity recognition
- 🔄 **Multi-format Conversion** - Markdown ↔ HTML ↔ JSON ↔ YAML ↔ Plain bidirectional conversion
- 📊 **Structured Output** - Not just format conversion, but document structure extraction
- 🖥️ **Interactive TUI** - Beautiful terminal interface with zero learning curve
- 📁 **Batch Processing** - Folder batch conversion, wildcard matching, parallel processing

### ✨ Features

| Feature | Description | Status |
|---------|-------------|--------|
| 📝 **Multi-format** | Markdown/HTML/JSON/YAML/CSV/XML/RST/Org-mode | ✅ Supported |
| 🧠 **Smart Analysis** | Keyword extraction, summary generation, readability analysis | ✅ Supported |
| 🔍 **Entity Recognition** | Auto-detect emails, URLs, IPs, dates, versions | ✅ Supported |
| 📑 **TOC Generation** | Automatic table of contents generation | ✅ Supported |
| 🎨 **Themes** | Default/Minimal/Fancy output themes | ✅ Supported |
| 📊 **Enhanced Reports** | Structured analysis reports with statistics | ✅ Supported |
| 🖥️ **TUI Interface** | Interactive terminal menu-driven interface | ✅ Supported |
| 📁 **Batch Processing** | Folder batch conversion with parallel processing | ✅ Supported |
| 🔄 **Pipeline Mode** | Custom processing pipeline chains | ✅ Supported |
| 🌐 **Bilingual** | Full Chinese and English content processing | ✅ Supported |

### 🚀 Quick Start

#### Requirements

- **Python**: 3.10 or higher
- **OS**: Windows / macOS / Linux

#### Installation

```bash
# Install from source
git clone https://github.com/gitstq/documind-converter-v2.git
cd documind-converter-v2
pip install -e .

# Or use pip (coming soon)
pip install documind-converter
```

#### Basic Usage

```bash
# Single file conversion
documind convert input.md -o output.html -f html

# Batch conversion
documind batch "docs/*.md" -o out/ -f json

# Document analysis
documind analyze document.md -o report.txt

# View document info
documind info document.md

# Interactive TUI
documind-tui
```

#### Python API

```python
from documind import DocumentConverter, StructureExtractor, BatchPipeline

# Single file conversion
converter = DocumentConverter()
result = converter.convert('input.md', output_format='html', output_path='output.html')

# Document analysis
extractor = StructureExtractor()
analysis = extractor.analyze_document(open('doc.md').read())
print(f"Keywords: {[kw[0] for kw in analysis['keywords'][:5]]}")
print(f"Summary: {analysis['summary']}")

# Batch conversion
pipeline = BatchPipeline()
results = pipeline.batch_convert('docs/*.md', 'output/', 'html')
```

### 📖 Detailed Guide

#### CLI Commands

```bash
# Convert format
documind convert input.md -o output.html -f html --theme fancy

# Analyze document
documind analyze paper.md -o analysis.report -f report

# Batch processing
documind batch "**/*.md" -o converted/ -f structured -j 8

# View help
documind --help
documind convert --help
```

#### Supported Formats

**Input**: `.md`, `.markdown`, `.txt`, `.html`, `.htm`, `.json`, `.yaml`, `.yml`, `.csv`, `.xml`, `.rst`, `.org`

**Output**: `markdown`, `html`, `json`, `yaml`, `plain`, `structured`

### 💡 Design & Roadmap

#### Technical Choices

- **Pure Standard Library**: Eliminate dependency hell, ensure out-of-box experience
- **Modular Architecture**: Converter/Extractor/Formatter/Pipeline separation
- **Rule + Statistics Hybrid**: Lightweight NLP without heavy ML frameworks

#### Roadmap

- [ ] v1.1.0: PDF/Word/Excel parsing (pure Python)
- [ ] v1.2.0: LLM API integration for smart summarization
- [ ] v1.3.0: Plugin system for custom converters
- [ ] v2.0.0: Web UI for online document processing

### 📦 Packaging & Deployment

```bash
# Build distribution
python setup.py sdist bdist_wheel

# Local install
pip install -e .

# Run tests
pytest tests/ -v

# Code formatting
black documind/ tests/ --line-length 100
```

### 🤝 Contributing

Issues and PRs are welcome!

- Describe issues clearly with reproduction steps
- Ensure all tests pass before submitting PR
- Follow PEP 8 code style

### 📄 License

This project is open-sourced under the [MIT License](LICENSE).

---

## 繁體中文

### 🎉 項目介紹

DocuMind-Converter 是一款**零依賴**的輕量級AI文檔智能轉換與結構化提取引擎，專為開發者、內容創作者和數據處理專家設計。

**核心價值**：
- 🚀 **零依賴架構** - 純Python標準庫實現，無需安裝任何第三方包
- 🤖 **AI智能分析** - 內置關鍵詞提取、摘要生成、實體識別等智能功能
- 🔄 **多格式互轉** - 支持 Markdown ↔ HTML ↔ JSON ↔ YAML ↔ Plain 雙向轉換
- 📊 **結構化輸出** - 不僅轉換格式，更提取文檔結構、生成目錄、識別關鍵信息
- 🖥️ **交互式TUI** - 提供美觀的終端交互界面，零學習成本
- 📁 **批量處理** - 支持文件夾批量轉換、通配符匹配、並行處理

### ✨ 核心特性

| 特性 | 描述 | 狀態 |
|------|------|------|
| 📝 **多格式支持** | Markdown/HTML/JSON/YAML/CSV/XML/RST/Org-mode | ✅ 已支持 |
| 🧠 **智能分析** | 關鍵詞提取、摘要生成、可讀性分析 | ✅ 已支持 |
| 🔍 **實體識別** | 自動識別郵箱、URL、IP、日期、版本號 | ✅ 已支持 |
| 📑 **目錄生成** | 自動生成文檔目錄(TOC) | ✅ 已支持 |
| 🎨 **多主題** | Default/Minimal/Fancy 三種輸出主題 | ✅ 已支持 |
| 📊 **增強報告** | 結構化分析報告，包含統計和可讀性評分 | ✅ 已支持 |
| 🖥️ **TUI界面** | 交互式終端界面，菜單驅動 | ✅ 已支持 |
| 📁 **批量處理** | 文件夾批量轉換、並行處理 | ✅ 已支持 |
| 🌐 **中英文支持** | 完整的中英文文檔內容處理 | ✅ 已支持 |

### 🚀 快速開始

#### 環境要求

- **Python**: 3.10 或更高版本
- **操作系統**: Windows / macOS / Linux

#### 安裝

```bash
# 從源碼安裝
git clone https://github.com/gitstq/documind-converter-v2.git
cd documind-converter-v2
pip install -e .
```

#### 基本使用

```bash
# 單文件轉換
documind convert input.md -o output.html -f html

# 批量轉換
documind batch "docs/*.md" -o out/ -f json

# 文檔分析
documind analyze document.md -o report.txt

# 交互式TUI界面
documind-tui
```

#### Python API

```python
from documind import DocumentConverter, StructureExtractor

# 單文件轉換
converter = DocumentConverter()
result = converter.convert('input.md', output_format='html')

# 文檔分析
extractor = StructureExtractor()
analysis = extractor.analyze_document(open('doc.md').read())
print(f"關鍵詞: {[kw[0] for kw in analysis['keywords'][:5]]}")
```

### 📄 開源協議

本項目採用 [MIT 協議](LICENSE) 開源。

---

<div align="center">

**Made with ❤️ by DocuMind Team**

[GitHub](https://github.com/gitstq/documind-converter-v2) | [Issues](https://github.com/gitstq/documind-converter-v2/issues) | [License](LICENSE)

</div>
