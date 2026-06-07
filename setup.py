"""
DocuMind-Converter 安装配置
"""

from setuptools import setup, find_packages
from pathlib import Path

# 读取README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

setup(
    name="documind-converter",
    version="1.0.0",
    author="DocuMind Team",
    author_email="documind@example.com",
    description="轻量级AI文档智能转换与结构化提取引擎",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gitstq/documind-converter",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup",
        "Topic :: Utilities",
    ],
    python_requires=">=3.10",
    entry_points={
        "console_scripts": [
            "documind=documind.cli:main",
            "documind-tui=documind.tui:run_tui",
        ],
    },
    keywords="document converter markdown html json yaml ai extraction",
    project_urls={
        "Bug Reports": "https://github.com/gitstq/documind-converter/issues",
        "Source": "https://github.com/gitstq/documind-converter",
    },
)
