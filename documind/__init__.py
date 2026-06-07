"""
DocuMind-Converter 🧠
轻量级AI文档智能转换与结构化提取引擎
Lightweight AI Document Intelligent Conversion & Structured Extraction Engine

Zero Dependencies · Multi-Format · AI-Powered · TUI Dashboard
"""

__version__ = "1.0.0"
__author__ = "DocuMind Team"
__license__ = "MIT"

from .converter import DocumentConverter
from .extractor import StructureExtractor
from .formatter import OutputFormatter
from .pipeline import BatchPipeline

__all__ = [
    "DocumentConverter",
    "StructureExtractor", 
    "OutputFormatter",
    "BatchPipeline",
]
