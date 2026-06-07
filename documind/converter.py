"""
核心文档转换引擎 - 支持多种格式互转
Core Document Conversion Engine - Multi-format bidirectional conversion
"""

import re
import json
import html
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
from .utils import TextUtils, FileUtils


class DocumentConverter:
    """
    文档转换器主类 - 零依赖实现多格式文档转换
    """
    
    SUPPORTED_INPUT = {
        '.md', '.markdown', '.txt', '.html', '.htm', 
        '.json', '.yaml', '.yml', '.csv', '.xml',
        '.rst', '.org', '.tex'
    }
    
    SUPPORTED_OUTPUT = {
        'markdown', 'html', 'json', 'yaml', 
        'plain', 'structured'
    }
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.utils = TextUtils()
        self.file_utils = FileUtils()
        self._init_parsers()
    
    def _init_parsers(self):
        """初始化各格式解析器"""
        self.parsers = {
            '.md': self._parse_markdown,
            '.markdown': self._parse_markdown,
            '.txt': self._parse_plain_text,
            '.html': self._parse_html,
            '.htm': self._parse_html,
            '.json': self._parse_json,
            '.yaml': self._parse_yaml,
            '.yml': self._parse_yaml,
            '.csv': self._parse_csv,
            '.xml': self._parse_xml,
            '.rst': self._parse_rst,
            '.org': self._parse_org,
        }
    
    def convert(self, 
                input_path: Union[str, Path], 
                output_format: str = 'markdown',
                output_path: Optional[Union[str, Path]] = None,
                options: Optional[Dict[str, Any]] = None) -> str:
        """
        转换文档到目标格式
        
        Args:
            input_path: 输入文件路径
            output_format: 输出格式 (markdown/html/json/yaml/plain/structured)
            output_path: 输出文件路径 (可选)
            options: 转换选项
            
        Returns:
            转换后的内容字符串
        """
        input_path = Path(input_path)
        
        if not input_path.exists():
            raise FileNotFoundError(f"文件不存在: {input_path}")
        
        ext = input_path.suffix.lower()
        if ext not in self.SUPPORTED_INPUT:
            raise ValueError(f"不支持的输入格式: {ext}")
        
        if output_format not in self.SUPPORTED_OUTPUT:
            raise ValueError(f"不支持的输出格式: {output_format}")
        
        # 读取并解析源文件
        content = self.file_utils.read_file(input_path)
        parsed_data = self.parsers[ext](content)
        
        # 转换到目标格式
        result = self._format_output(parsed_data, output_format, options or {})
        
        # 保存到文件
        if output_path:
            self.file_utils.write_file(Path(output_path), result)
        
        return result
    
    def _parse_markdown(self, content: str) -> Dict[str, Any]:
        """解析Markdown为结构化数据"""
        lines = content.split('\n')
        structure = {
            'type': 'markdown',
            'title': '',
            'headings': [],
            'paragraphs': [],
            'lists': [],
            'code_blocks': [],
            'tables': [],
            'links': [],
            'raw': content
        }
        
        current_list = []
        in_code_block = False
        code_lang = ''
        code_content = []
        
        for line in lines:
            stripped = line.strip()
            
            # 代码块检测
            if stripped.startswith('```'):
                if not in_code_block:
                    in_code_block = True
                    code_lang = stripped[3:].strip()
                    code_content = []
                else:
                    in_code_block = False
                    structure['code_blocks'].append({
                        'language': code_lang,
                        'content': '\n'.join(code_content)
                    })
                continue
            
            if in_code_block:
                code_content.append(line)
                continue
            
            # 标题检测
            if stripped.startswith('#'):
                level = len(stripped) - len(stripped.lstrip('#'))
                title = stripped.lstrip('#').strip()
                structure['headings'].append({
                    'level': level,
                    'title': title,
                    'line': len(structure['headings'])
                })
                if level == 1 and not structure['title']:
                    structure['title'] = title
                continue
            
            # 列表检测
            list_match = re.match(r'^[\s]*([\-\*\+]|[0-9]+\.)\s+(.+)', stripped)
            if list_match:
                current_list.append({
                    'marker': list_match.group(1),
                    'content': list_match.group(2),
                    'indent': len(line) - len(line.lstrip())
                })
                continue
            elif current_list and not stripped:
                structure['lists'].append(current_list)
                current_list = []
            
            # 表格检测
            if '|' in stripped and not stripped.startswith('>'):
                cells = [c.strip() for c in stripped.split('|') if c.strip()]
                if cells and not all(c.replace('-', '').replace(':', '') == '' for c in cells):
                    structure['tables'].append(cells)
                continue
            
            # 链接检测
            links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', stripped)
            for text, url in links:
                structure['links'].append({'text': text, 'url': url})
            
            # 段落
            if stripped:
                structure['paragraphs'].append(stripped)
        
        if current_list:
            structure['lists'].append(current_list)
        
        return structure
    
    def _parse_html(self, content: str) -> Dict[str, Any]:
        """解析HTML为结构化数据"""
        structure = {
            'type': 'html',
            'title': '',
            'headings': [],
            'paragraphs': [],
            'lists': [],
            'links': [],
            'raw': content
        }
        
        # 提取标题
        title_match = re.search(r'<title[^>]*>(.*?)</title>', content, re.DOTALL | re.IGNORECASE)
        if title_match:
            structure['title'] = html.unescape(title_match.group(1).strip())
        
        # 提取h1-h6标题
        for level in range(1, 7):
            pattern = f'<h{level}[^>]*>(.*?)</h{level}>'
            matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
            for match in matches:
                clean = re.sub(r'<[^>]+>', '', match)
                structure['headings'].append({
                    'level': level,
                    'title': html.unescape(clean.strip()),
                    'line': 0
                })
        
        # 提取段落
        p_matches = re.findall(r'<p[^>]*>(.*?)</p>', content, re.DOTALL | re.IGNORECASE)
        for match in p_matches:
            clean = re.sub(r'<[^>]+>', '', match)
            text = html.unescape(clean.strip())
            if text:
                structure['paragraphs'].append(text)
        
        # 提取链接
        a_matches = re.findall(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', content, re.DOTALL | re.IGNORECASE)
        for url, text in a_matches:
            clean_text = re.sub(r'<[^>]+>', '', text)
            structure['links'].append({
                'text': html.unescape(clean_text.strip()),
                'url': url
            })
        
        return structure
    
    def _parse_plain_text(self, content: str) -> Dict[str, Any]:
        """解析纯文本"""
        lines = content.split('\n')
        structure = {
            'type': 'text',
            'title': lines[0] if lines else '',
            'headings': [],
            'paragraphs': [],
            'lists': [],
            'raw': content
        }
        
        current_para = []
        for line in lines:
            stripped = line.strip()
            if stripped:
                current_para.append(stripped)
            elif current_para:
                structure['paragraphs'].append(' '.join(current_para))
                current_para = []
        
        if current_para:
            structure['paragraphs'].append(' '.join(current_para))
        
        return structure
    
    def _parse_json(self, content: str) -> Dict[str, Any]:
        """解析JSON"""
        try:
            data = json.loads(content)
            return {
                'type': 'json',
                'title': 'JSON Document',
                'data': data,
                'raw': content
            }
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON解析错误: {e}")
    
    def _parse_yaml(self, content: str) -> Dict[str, Any]:
        """解析YAML (轻量级实现)"""
        structure = {
            'type': 'yaml',
            'title': 'YAML Document',
            'data': {},
            'raw': content
        }
        
        current_key = None
        current_list = []
        lines = content.split('\n')
        
        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                continue
            
            # 键值对
            if ':' in stripped and not stripped.startswith('-'):
                if current_list and current_key:
                    structure['data'][current_key] = current_list
                    current_list = []
                
                key, value = stripped.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                if value:
                    structure['data'][key] = self._parse_yaml_value(value)
                else:
                    current_key = key
            
            # 列表项
            elif stripped.startswith('-'):
                item = stripped[1:].strip()
                if ':' in item:
                    sub_key, sub_value = item.split(':', 1)
                    if current_key not in structure['data']:
                        structure['data'][current_key] = {}
                    if isinstance(structure['data'][current_key], dict):
                        structure['data'][current_key][sub_key.strip()] = self._parse_yaml_value(sub_value.strip())
                else:
                    current_list.append(self._parse_yaml_value(item))
        
        if current_list and current_key:
            structure['data'][current_key] = current_list
        
        return structure
    
    def _parse_yaml_value(self, value: str) -> Union[str, int, float, bool, None]:
        """解析YAML值"""
        value = value.strip().strip('"\'')
        
        if value.lower() in ('true', 'yes', 'on'):
            return True
        if value.lower() in ('false', 'no', 'off'):
            return False
        if value.lower() in ('null', '~', ''):
            return None
        
        try:
            if '.' in value:
                return float(value)
            return int(value)
        except ValueError:
            return value
    
    def _parse_csv(self, content: str) -> Dict[str, Any]:
        """解析CSV"""
        lines = content.strip().split('\n')
        if not lines:
            return {'type': 'csv', 'headers': [], 'rows': [], 'raw': content}
        
        headers = self._split_csv_line(lines[0])
        rows = []
        
        for line in lines[1:]:
            if line.strip():
                rows.append(self._split_csv_line(line))
        
        return {
            'type': 'csv',
            'title': 'CSV Document',
            'headers': headers,
            'rows': rows,
            'raw': content
        }
    
    def _split_csv_line(self, line: str) -> List[str]:
        """安全分割CSV行"""
        result = []
        current = []
        in_quotes = False
        
        for char in line:
            if char == '"':
                in_quotes = not in_quotes
            elif char == ',' and not in_quotes:
                result.append(''.join(current).strip().strip('"'))
                current = []
            else:
                current.append(char)
        
        result.append(''.join(current).strip().strip('"'))
        return result
    
    def _parse_xml(self, content: str) -> Dict[str, Any]:
        """解析XML为结构化数据"""
        structure = {
            'type': 'xml',
            'title': 'XML Document',
            'elements': [],
            'raw': content
        }
        
        # 提取标签和文本
        tag_pattern = re.compile(r'<([^/][^>]*)>([^<]*)</\1>')
        matches = tag_pattern.findall(content)
        
        for tag, text in matches:
            tag_name = tag.split()[0]
            structure['elements'].append({
                'tag': tag_name,
                'content': text.strip(),
                'attributes': self._parse_xml_attributes(tag)
            })
        
        return structure
    
    def _parse_xml_attributes(self, tag: str) -> Dict[str, str]:
        """解析XML属性"""
        attrs = {}
        attr_pattern = re.compile(r'(\w+)=["\']([^"\']+)["\']')
        matches = attr_pattern.findall(tag)
        for key, value in matches:
            attrs[key] = value
        return attrs
    
    def _parse_rst(self, content: str) -> Dict[str, Any]:
        """解析reStructuredText"""
        lines = content.split('\n')
        structure = {
            'type': 'rst',
            'title': '',
            'headings': [],
            'paragraphs': [],
            'raw': content
        }
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # 标题检测 (下划线样式)
            if i > 0 and stripped and all(c == stripped[0] for c in stripped) and len(stripped) >= 3:
                if i + 1 < len(lines) and lines[i + 1].strip():
                    title = lines[i - 1].strip()
                    level = self._get_rst_heading_level(stripped[0])
                    structure['headings'].append({
                        'level': level,
                        'title': title,
                        'line': i - 1
                    })
                    if not structure['title']:
                        structure['title'] = title
            
            # 段落
            elif stripped and not all(c == stripped[0] for c in stripped):
                structure['paragraphs'].append(stripped)
        
        return structure
    
    def _get_rst_heading_level(self, char: str) -> int:
        """获取RST标题级别"""
        levels = {'=': 1, '-': 2, '~': 3, '^': 4, '"': 5, "'": 6}
        return levels.get(char, 1)
    
    def _parse_org(self, content: str) -> Dict[str, Any]:
        """解析Org-mode"""
        lines = content.split('\n')
        structure = {
            'type': 'org',
            'title': '',
            'headings': [],
            'paragraphs': [],
            'raw': content
        }
        
        for line in lines:
            stripped = line.strip()
            
            # 标题检测
            if stripped.startswith('*'):
                level = len(stripped) - len(stripped.lstrip('*'))
                title = stripped.lstrip('*').strip()
                structure['headings'].append({
                    'level': level,
                    'title': title,
                    'line': 0
                })
                if level == 1 and not structure['title']:
                    structure['title'] = title
            elif stripped:
                structure['paragraphs'].append(stripped)
        
        return structure
    
    def _format_output(self, data: Dict[str, Any], format_type: str, options: Dict[str, Any]) -> str:
        """格式化输出"""
        formatters = {
            'markdown': self._to_markdown,
            'html': self._to_html,
            'json': self._to_json,
            'yaml': self._to_yaml,
            'plain': self._to_plain,
            'structured': self._to_structured
        }
        
        return formatters[format_type](data, options)
    
    def _to_markdown(self, data: Dict[str, Any], options: Dict[str, Any]) -> str:
        """转换为Markdown"""
        lines = []
        
        if data.get('title'):
            lines.append(f"# {data['title']}\n")
        
        # 标题
        for heading in data.get('headings', []):
            prefix = '#' * heading['level']
            lines.append(f"{prefix} {heading['title']}\n")
        
        # 段落
        for para in data.get('paragraphs', []):
            lines.append(f"{para}\n")
        
        # 列表
        for lst in data.get('lists', []):
            for item in lst:
                indent = '  ' * (item['indent'] // 2)
                lines.append(f"{indent}{item['marker']} {item['content']}\n")
            lines.append('')
        
        # 代码块
        for block in data.get('code_blocks', []):
            lines.append(f"```{block['language']}")
            lines.append(block['content'])
            lines.append("```\n")
        
        # 表格
        for table in data.get('tables', []):
            if table:
                lines.append('| ' + ' | '.join(table) + ' |')
                lines.append('|' + '|'.join(['---'] * len(table)) + '|')
            lines.append('')
        
        # 链接
        for link in data.get('links', []):
            lines.append(f"[{link['text']}]({link['url']})")
        
        return '\n'.join(lines)
    
    def _to_html(self, data: Dict[str, Any], options: Dict[str, Any]) -> str:
        """转换为HTML"""
        lines = ['<!DOCTYPE html>', '<html>', '<head>', '<meta charset="UTF-8">']
        
        if data.get('title'):
            lines.append(f"<title>{html.escape(data['title'])}</title>")
        
        lines.extend(['</head>', '<body>'])
        
        if data.get('title'):
            lines.append(f"<h1>{html.escape(data['title'])}</h1>")
        
        for heading in data.get('headings', []):
            tag = f"h{heading['level']}"
            lines.append(f"<{tag}>{html.escape(heading['title'])}</{tag}>")
        
        for para in data.get('paragraphs', []):
            lines.append(f"<p>{html.escape(para)}</p>")
        
        for lst in data.get('lists', []):
            lines.append('<ul>')
            for item in lst:
                lines.append(f"<li>{html.escape(item['content'])}</li>")
            lines.append('</ul>')
        
        for link in data.get('links', []):
            lines.append(f'<a href="{html.escape(link["url"])}">{html.escape(link["text"])}</a>')
        
        lines.extend(['</body>', '</html>'])
        
        return '\n'.join(lines)
    
    def _to_json(self, data: Dict[str, Any], options: Dict[str, Any]) -> str:
        """转换为JSON"""
        indent = options.get('indent', 2)
        return json.dumps(data, ensure_ascii=False, indent=indent)
    
    def _to_yaml(self, data: Dict[str, Any], options: Dict[str, Any]) -> str:
        """转换为YAML (轻量级实现)"""
        lines = []
        
        def _dump_value(key: str, value: Any, indent: int = 0):
            prefix = '  ' * indent
            if isinstance(value, dict):
                lines.append(f"{prefix}{key}:")
                for k, v in value.items():
                    _dump_value(k, v, indent + 1)
            elif isinstance(value, list):
                lines.append(f"{prefix}{key}:")
                for item in value:
                    if isinstance(item, dict):
                        first = True
                        for k, v in item.items():
                            if first:
                                lines.append(f"{prefix}  - {k}: {self._yaml_scalar(v)}")
                                first = False
                            else:
                                lines.append(f"{prefix}    {k}: {self._yaml_scalar(v)}")
                    else:
                        lines.append(f"{prefix}  - {self._yaml_scalar(item)}")
            else:
                lines.append(f"{prefix}{key}: {self._yaml_scalar(value)}")
        
        for key, value in data.items():
            _dump_value(key, value)
        
        return '\n'.join(lines)
    
    def _yaml_scalar(self, value: Any) -> str:
        """YAML标量格式化"""
        if isinstance(value, bool):
            return 'true' if value else 'false'
        if value is None:
            return 'null'
        if isinstance(value, (int, float)):
            return str(value)
        if isinstance(value, str):
            if any(c in value for c in [':', '#', '{', '}', '[', ']', ',', '&', '*', '?', '|', '-', '<', '>', '=', '!', '%', '@', '`', '"', "'"]):
                escaped = value.replace('\\', '\\\\').replace('"', '\\"')
                return f'"{escaped}"'
            return value
        return str(value)
    
    def _to_plain(self, data: Dict[str, Any], options: Dict[str, Any]) -> str:
        """转换为纯文本"""
        lines = []
        
        if data.get('title'):
            lines.append(data['title'])
            lines.append('=' * len(data['title']))
            lines.append('')
        
        for heading in data.get('headings', []):
            indent = '  ' * (heading['level'] - 1)
            lines.append(f"{indent}{heading['title']}")
        
        for para in data.get('paragraphs', []):
            lines.append(para)
        
        return '\n\n'.join(lines)
    
    def _to_structured(self, data: Dict[str, Any], options: Dict[str, Any]) -> str:
        """转换为结构化报告"""
        lines = [
            '=' * 60,
            '文档结构化分析报告',
            '=' * 60,
            ''
        ]
        
        lines.append(f"文档类型: {data.get('type', 'unknown')}")
        lines.append(f"文档标题: {data.get('title', 'N/A')}")
        lines.append('')
        
        headings = data.get('headings', [])
        if headings:
            lines.append(f"标题层级: {len(headings)} 个")
            for h in headings:
                indent = '  ' * (h['level'] - 1)
                lines.append(f"{indent}• {h['title']}")
            lines.append('')
        
        paragraphs = data.get('paragraphs', [])
        if paragraphs:
            lines.append(f"段落数量: {len(paragraphs)}")
            lines.append('')
        
        lists = data.get('lists', [])
        if lists:
            lines.append(f"列表数量: {len(lists)}")
            lines.append('')
        
        code_blocks = data.get('code_blocks', [])
        if code_blocks:
            lines.append(f"代码块数量: {len(code_blocks)}")
            for block in code_blocks:
                lines.append(f"  - {block.get('language', 'text')}: {len(block['content'])} 字符")
            lines.append('')
        
        links = data.get('links', [])
        if links:
            lines.append(f"链接数量: {len(links)}")
            lines.append('')
        
        lines.append('=' * 60)
        
        return '\n'.join(lines)
