"""
工具函数集合
Utility functions collection
"""

import re
from pathlib import Path
from typing import Union, Optional


class TextUtils:
    """文本处理工具"""
    
    @staticmethod
    def truncate(text: str, max_length: int = 100, suffix: str = '...') -> str:
        """截断文本"""
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix
    
    @staticmethod
    def slugify(text: str) -> str:
        """生成URL友好的slug"""
        text = re.sub(r'[^\w\s-]', '', text.lower())
        text = re.sub(r'[-\s]+', '-', text)
        return text.strip('-')
    
    @staticmethod
    def count_words(text: str) -> int:
        """统计词数（支持中英文）"""
        # 英文单词
        en_words = len(re.findall(r'[a-zA-Z]+', text))
        # 中文字符
        zh_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        return en_words + zh_chars
    
    @staticmethod
    def strip_html(html_text: str) -> str:
        """去除HTML标签"""
        clean = re.sub(r'<[^>]+>', '', html_text)
        return clean
    
    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """规范化空白字符"""
        return ' '.join(text.split())


class FileUtils:
    """文件处理工具"""
    
    @staticmethod
    def read_file(path: Union[str, Path], encoding: str = 'utf-8') -> str:
        """读取文本文件"""
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {path}")
        return path.read_text(encoding=encoding)
    
    @staticmethod
    def write_file(path: Union[str, Path], content: str, encoding: str = 'utf-8') -> None:
        """写入文本文件"""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding=encoding)
    
    @staticmethod
    def get_file_size(path: Union[str, Path]) -> int:
        """获取文件大小（字节）"""
        return Path(path).stat().st_size
    
    @staticmethod
    def get_file_extension(path: Union[str, Path]) -> str:
        """获取文件扩展名"""
        return Path(path).suffix.lower()
    
    @staticmethod
    def ensure_dir(path: Union[str, Path]) -> Path:
        """确保目录存在"""
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        return path
