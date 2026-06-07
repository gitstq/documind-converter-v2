"""
转换器单元测试
"""

import pytest
from pathlib import Path
from documind.converter import DocumentConverter


class TestDocumentConverter:
    """测试文档转换器"""
    
    def setup_method(self):
        self.converter = DocumentConverter()
    
    def test_parse_markdown(self):
        """测试Markdown解析"""
        content = """# 标题

这是段落1。

这是段落2。

## 子标题

- 列表项1
- 列表项2

```python
print("hello")
```
"""
        result = self.converter._parse_markdown(content)
        
        assert result['type'] == 'markdown'
        assert result['title'] == '标题'
        assert len(result['headings']) == 2
        assert len(result['paragraphs']) >= 1
        assert len(result['lists']) == 1
        assert len(result['code_blocks']) == 1
    
    def test_parse_html(self):
        """测试HTML解析"""
        content = """<html>
<head><title>测试页面</title></head>
<body>
<h1>主标题</h1>
<p>段落内容</p>
<a href="https://example.com">链接</a>
</body>
</html>"""
        
        result = self.converter._parse_html(content)
        
        assert result['type'] == 'html'
        assert result['title'] == '测试页面'
        assert len(result['headings']) == 1
        assert len(result['paragraphs']) == 1
        assert len(result['links']) == 1
    
    def test_parse_plain_text(self):
        """测试纯文本解析"""
        content = "第一行\n\n第二段内容"
        
        result = self.converter._parse_plain_text(content)
        
        assert result['type'] == 'text'
        assert len(result['paragraphs']) == 2
    
    def test_parse_json(self):
        """测试JSON解析"""
        content = '{"name": "test", "value": 123}'
        
        result = self.converter._parse_json(content)
        
        assert result['type'] == 'json'
        assert result['data']['name'] == 'test'
    
    def test_to_markdown(self):
        """测试Markdown输出"""
        data = {
            'type': 'test',
            'title': '测试',
            'headings': [{'level': 1, 'title': '标题'}],
            'paragraphs': ['段落'],
            'lists': [],
            'code_blocks': [],
            'tables': [],
            'links': []
        }
        
        result = self.converter._to_markdown(data, {})
        
        assert '# 测试' in result
        assert '# 标题' in result
        assert '段落' in result
    
    def test_to_html(self):
        """测试HTML输出"""
        data = {
            'type': 'test',
            'title': '测试',
            'headings': [{'level': 1, 'title': '标题'}],
            'paragraphs': ['段落'],
            'lists': [],
            'links': []
        }
        
        result = self.converter._to_html(data, {})
        
        assert '<html>' in result
        assert '测试' in result
        assert '段落' in result
    
    def test_unsupported_input_format(self):
        """测试不支持的输入格式"""
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.unknown', delete=False) as f:
            f.write(b'test')
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError):
                self.converter.convert(temp_path)
        finally:
            import os
            os.unlink(temp_path)
    
    def test_file_not_found(self):
        """测试文件不存在"""
        with pytest.raises(FileNotFoundError):
            self.converter.convert('nonexistent.md')
