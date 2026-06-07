"""
输出格式化器 - 支持多种输出格式和模板
Output Formatter - Multiple output formats and templates support
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from datetime import datetime


class OutputFormatter:
    """
    输出格式化器
    支持多种输出格式、自定义模板、主题样式
    """
    
    THEMES = {
        'default': {
            'heading_char': '#',
            'bullet': '-',
            'code_fence': '```',
            'table_border': '|',
            'quote_prefix': '>',
            'separator': '---'
        },
        'minimal': {
            'heading_char': '#',
            'bullet': '*',
            'code_fence': '```',
            'table_border': '|',
            'quote_prefix': '>',
            'separator': '---'
        },
        'fancy': {
            'heading_char': '█',
            'bullet': '▸',
            'code_fence': '```',
            'table_border': '│',
            'quote_prefix': '┃',
            'separator': '═══'
        }
    }
    
    def __init__(self, theme: str = 'default', config: Optional[Dict[str, Any]] = None):
        self.theme = self.THEMES.get(theme, self.THEMES['default'])
        self.config = config or {}
        self.include_toc = self.config.get('include_toc', True)
        self.include_stats = self.config.get('include_stats', True)
        self.include_timestamp = self.config.get('include_timestamp', True)
    
    def format_document(self, 
                       data: Dict[str, Any],
                       analysis: Optional[Dict[str, Any]] = None,
                       output_format: str = 'markdown') -> str:
        """
        格式化完整文档
        
        Args:
            data: 文档结构化数据
            analysis: 分析结果（可选）
            output_format: 输出格式
            
        Returns:
            格式化后的字符串
        """
        if output_format == 'markdown':
            return self._format_markdown(data, analysis)
        elif output_format == 'html':
            return self._format_html(data, analysis)
        elif output_format == 'json':
            return self._format_json(data, analysis)
        elif output_format == 'report':
            return self._format_report(data, analysis)
        else:
            raise ValueError(f"不支持的输出格式: {output_format}")
    
    def _format_markdown(self, data: Dict[str, Any], analysis: Optional[Dict[str, Any]]) -> str:
        """格式化为增强Markdown"""
        lines = []
        
        # 文档头部
        if self.include_timestamp:
            lines.append(f"<!-- 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -->")
            lines.append('')
        
        # 标题
        if data.get('title'):
            lines.append(f"# {data['title']}")
            lines.append('')
        
        # 目录
        if self.include_toc and data.get('headings'):
            from .extractor import StructureExtractor
            extractor = StructureExtractor()
            toc = extractor.build_toc(data['headings'])
            lines.append(toc)
            lines.append(self.theme['separator'])
            lines.append('')
        
        # 文档统计
        if self.include_stats and analysis:
            stats = analysis.get('statistics', {})
            lines.append('## 📊 文档统计')
            lines.append('')
            lines.append(f"- **总字符数**: {stats.get('total_characters', 0)}")
            lines.append(f"- **总行数**: {stats.get('total_lines', 0)}")
            lines.append(f"- **总词数**: {stats.get('total_words', 0)}")
            lines.append(f"- **中文字符**: {stats.get('chinese_characters', 0)}")
            lines.append(f"- **代码块数**: {stats.get('code_blocks', 0)}")
            lines.append('')
        
        # 摘要
        if analysis and analysis.get('summary'):
            lines.append('## 📝 摘要')
            lines.append('')
            lines.append(f"> {analysis['summary']}")
            lines.append('')
        
        # 关键词
        if analysis and analysis.get('keywords'):
            lines.append('## 🔑 关键词')
            lines.append('')
            keywords = [f"`{kw[0]}`" for kw in analysis['keywords'][:10]]
            lines.append(' '.join(keywords))
            lines.append('')
        
        lines.append(self.theme['separator'])
        lines.append('')
        
        # 正文内容
        lines.append('## 📄 正文')
        lines.append('')
        
        # 标题
        for heading in data.get('headings', []):
            prefix = self.theme['heading_char'] * heading['level']
            lines.append(f"{prefix} {heading['title']}")
            lines.append('')
        
        # 段落
        for para in data.get('paragraphs', []):
            lines.append(para)
            lines.append('')
        
        # 列表
        for lst in data.get('lists', []):
            for item in lst:
                indent = '  ' * (item.get('indent', 0) // 2)
                lines.append(f"{indent}{self.theme['bullet']} {item['content']}")
            lines.append('')
        
        # 代码块
        for block in data.get('code_blocks', []):
            lines.append(f"{self.theme['code_fence']}{block.get('language', '')}")
            lines.append(block['content'])
            lines.append(self.theme['code_fence'])
            lines.append('')
        
        # 表格
        for table in data.get('tables', []):
            if table:
                border = self.theme['table_border']
                lines.append(f"{border} {' '.join([f'{border} {c} ' for c in table])}{border}")
                lines.append(f"{border}{'---'.join([''] * (len(table) + 1))}{border}")
            lines.append('')
        
        # 链接
        if data.get('links'):
            lines.append('## 🔗 链接')
            lines.append('')
            for link in data['links']:
                lines.append(f"- [{link['text']}]({link['url']})")
            lines.append('')
        
        # 实体识别
        if analysis and analysis.get('entities'):
            entities = analysis['entities']
            has_entities = any(entities.get(k) for k in entities)
            if has_entities:
                lines.append('## 🔍 识别到的实体')
                lines.append('')
                
                if entities.get('emails'):
                    lines.append('**邮箱地址**:')
                    for email in entities['emails'][:5]:
                        lines.append(f"- {email}")
                    lines.append('')
                
                if entities.get('urls'):
                    lines.append('**URL链接**:')
                    for url in entities['urls'][:5]:
                        lines.append(f"- {url}")
                    lines.append('')
                
                if entities.get('versions'):
                    lines.append('**版本号**:')
                    for v in entities['versions'][:5]:
                        lines.append(f"- {v}")
                    lines.append('')
        
        # 可读性分析
        if analysis and analysis.get('readability'):
            readability = analysis['readability']
            lines.append('## 📖 可读性分析')
            lines.append('')
            lines.append(f"- **可读性分数**: {readability['score']}/100")
            lines.append(f"- **难度等级**: {readability['level']}")
            lines.append(f"- **平均句长**: {readability['avg_sentence_length']}")
            lines.append('')
        
        return '\n'.join(lines)
    
    def _format_html(self, data: Dict[str, Any], analysis: Optional[Dict[str, Any]]) -> str:
        """格式化为增强HTML"""
        import html as html_module
        
        lines = [
            '<!DOCTYPE html>',
            '<html lang="zh-CN">',
            '<head>',
            '  <meta charset="UTF-8">',
            '  <meta name="viewport" content="width=device-width, initial-scale=1.0">',
        ]
        
        title = data.get('title', 'Document')
        lines.append(f'  <title>{html_module.escape(title)}</title>')
        lines.append('  <style>')
        lines.append(self._get_html_css())
        lines.append('  </style>')
        lines.append('</head>')
        lines.append('<body>')
        lines.append('  <div class="container">')
        
        # 标题
        if data.get('title'):
            lines.append(f'    <h1 class="doc-title">{html_module.escape(data["title"])}</h1>')
        
        # 元信息
        if self.include_timestamp:
            lines.append(f'    <div class="meta">生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>')
        
        # 统计卡片
        if analysis and analysis.get('statistics'):
            stats = analysis['statistics']
            lines.append('    <div class="stats-grid">')
            lines.append(f'      <div class="stat-card"><div class="stat-value">{stats.get("total_characters", 0)}</div><div class="stat-label">字符</div></div>')
            lines.append(f'      <div class="stat-card"><div class="stat-value">{stats.get("total_lines", 0)}</div><div class="stat-label">行数</div></div>')
            lines.append(f'      <div class="stat-card"><div class="stat-value">{stats.get("total_words", 0)}</div><div class="stat-label">词数</div></div>')
            lines.append('    </div>')
        
        # 摘要
        if analysis and analysis.get('summary'):
            lines.append('    <div class="section">')
            lines.append('      <h2>📝 摘要</h2>')
            lines.append(f'      <div class="summary">{html_module.escape(analysis["summary"])}</div>')
            lines.append('    </div>')
        
        # 关键词
        if analysis and analysis.get('keywords'):
            lines.append('    <div class="section">')
            lines.append('      <h2>🔑 关键词</h2>')
            lines.append('      <div class="keywords">')
            for kw in analysis['keywords'][:10]:
                lines.append(f'        <span class="keyword">{html_module.escape(kw[0])}</span>')
            lines.append('      </div>')
            lines.append('    </div>')
        
        # 正文
        lines.append('    <div class="section content">')
        lines.append('      <h2>📄 正文</h2>')
        
        for heading in data.get('headings', []):
            tag = f'h{heading["level"] + 1}'
            lines.append(f'      <{tag}>{html_module.escape(heading["title"])}</{tag}>')
        
        for para in data.get('paragraphs', []):
            lines.append(f'      <p>{html_module.escape(para)}</p>')
        
        for lst in data.get('lists', []):
            lines.append('      <ul>')
            for item in lst:
                lines.append(f'        <li>{html_module.escape(item["content"])}</li>')
            lines.append('      </ul>')
        
        for block in data.get('code_blocks', []):
            lines.append(f'      <pre><code class="language-{block.get("language", "text")}">')
            lines.append(html_module.escape(block['content']))
            lines.append('      </code></pre>')
        
        lines.append('    </div>')
        lines.append('  </div>')
        lines.append('</body>')
        lines.append('</html>')
        
        return '\n'.join(lines)
    
    def _get_html_css(self) -> str:
        """获取HTML样式"""
        return '''
    :root {
      --primary: #2563eb;
      --secondary: #64748b;
      --bg: #f8fafc;
      --card-bg: #ffffff;
      --text: #1e293b;
      --border: #e2e8f0;
    }
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { 
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.6;
    }
    .container { max-width: 900px; margin: 0 auto; padding: 2rem; }
    .doc-title { font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem; }
    .meta { color: var(--secondary); font-size: 0.875rem; margin-bottom: 1.5rem; }
    .stats-grid { 
      display: grid; 
      grid-template-columns: repeat(3, 1fr); 
      gap: 1rem; 
      margin-bottom: 2rem;
    }
    .stat-card { 
      background: var(--card-bg); 
      padding: 1rem; 
      border-radius: 0.5rem; 
      text-align: center;
      border: 1px solid var(--border);
    }
    .stat-value { font-size: 1.5rem; font-weight: 700; color: var(--primary); }
    .stat-label { font-size: 0.875rem; color: var(--secondary); }
    .section { 
      background: var(--card-bg); 
      padding: 1.5rem; 
      border-radius: 0.5rem; 
      margin-bottom: 1rem;
      border: 1px solid var(--border);
    }
    .section h2 { font-size: 1.25rem; margin-bottom: 1rem; color: var(--primary); }
    .summary { 
      background: #eff6ff; 
      padding: 1rem; 
      border-radius: 0.375rem; 
      border-left: 4px solid var(--primary);
    }
    .keywords { display: flex; flex-wrap: wrap; gap: 0.5rem; }
    .keyword { 
      background: #dbeafe; 
      color: var(--primary); 
      padding: 0.25rem 0.75rem; 
      border-radius: 9999px;
      font-size: 0.875rem;
    }
    .content h3 { margin: 1rem 0 0.5rem; }
    .content p { margin-bottom: 0.75rem; }
    .content ul { margin-left: 1.5rem; margin-bottom: 0.75rem; }
    pre { 
      background: #1e293b; 
      color: #e2e8f0; 
      padding: 1rem; 
      border-radius: 0.375rem; 
      overflow-x: auto;
      margin-bottom: 1rem;
    }
    code { font-family: 'Consolas', 'Monaco', monospace; font-size: 0.875rem; }
    '''
    
    def _format_json(self, data: Dict[str, Any], analysis: Optional[Dict[str, Any]]) -> str:
        """格式化为JSON"""
        output = {
            'document': data,
            'analysis': analysis,
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'version': '1.0.0'
            }
        }
        return json.dumps(output, ensure_ascii=False, indent=2)
    
    def _format_report(self, data: Dict[str, Any], analysis: Optional[Dict[str, Any]]) -> str:
        """格式化为分析报告"""
        lines = [
            '=' * 70,
            '                    📊 文档智能分析报告',
            '=' * 70,
            ''
        ]
        
        # 基本信息
        lines.append('【基本信息】')
        lines.append(f"  文档标题: {data.get('title', 'N/A')}")
        lines.append(f"  文档类型: {data.get('type', 'unknown')}")
        lines.append(f"  生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append('')
        
        # 统计信息
        if analysis and analysis.get('statistics'):
            stats = analysis['statistics']
            lines.append('【统计信息】')
            lines.append(f"  总字符数: {stats.get('total_characters', 0)}")
            lines.append(f"  总行数: {stats.get('total_lines', 0)}")
            lines.append(f"  总词数: {stats.get('total_words', 0)}")
            lines.append(f"  中文字符: {stats.get('chinese_characters', 0)}")
            lines.append(f"  段落数: {stats.get('paragraphs', 0)}")
            lines.append(f"  代码块: {stats.get('code_blocks', 0)}")
            lines.append('')
        
        # 摘要
        if analysis and analysis.get('summary'):
            lines.append('【内容摘要】')
            lines.append(f"  {analysis['summary']}")
            lines.append('')
        
        # 关键词
        if analysis and analysis.get('keywords'):
            lines.append('【关键词】')
            keywords_str = ', '.join([f"{kw[0]}({kw[1]:.3f})" for kw in analysis['keywords'][:15]])
            lines.append(f"  {keywords_str}")
            lines.append('')
        
        # 标题结构
        if data.get('headings'):
            lines.append('【文档结构】')
            for h in data['headings']:
                indent = '  ' * h['level']
                lines.append(f"{indent}└─ {h['title']}")
            lines.append('')
        
        # 可读性
        if analysis and analysis.get('readability'):
            readability = analysis['readability']
            lines.append('【可读性分析】')
            lines.append(f"  可读性分数: {readability['score']}/100")
            lines.append(f"  难度等级: {readability['level']}")
            lines.append(f"  平均句长: {readability['avg_sentence_length']}")
            lines.append('')
        
        # 实体
        if analysis and analysis.get('entities'):
            entities = analysis['entities']
            lines.append('【识别实体】')
            for entity_type, values in entities.items():
                if values:
                    lines.append(f"  {entity_type}: {', '.join(values[:5])}")
            lines.append('')
        
        lines.append('=' * 70)
        
        return '\n'.join(lines)
    
    def apply_template(self, content: str, template_path: Optional[Union[str, Path]] = None,
                      variables: Optional[Dict[str, str]] = None) -> str:
        """
        应用模板
        
        Args:
            content: 原始内容
            template_path: 模板文件路径
            variables: 模板变量
            
        Returns:
            应用模板后的内容
        """
        variables = variables or {}
        variables['content'] = content
        variables['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if template_path and Path(template_path).exists():
            template = Path(template_path).read_text(encoding='utf-8')
        else:
            template = '{{content}}'
        
        # 简单变量替换
        for key, value in variables.items():
            template = template.replace(f'{{{{{key}}}}}', str(value))
        
        return template
