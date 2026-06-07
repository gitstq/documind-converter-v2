"""
提取器单元测试
"""

import pytest
from documind.extractor import StructureExtractor


class TestStructureExtractor:
    """测试结构提取器"""
    
    def setup_method(self):
        self.extractor = StructureExtractor()
    
    def test_extract_keywords(self):
        """测试关键词提取"""
        text = "Python is a great programming language. Python is easy to learn."
        keywords = self.extractor.extract_keywords(text)
        
        assert len(keywords) > 0
        assert any('python' in kw[0].lower() for kw in keywords)
    
    def test_extract_keywords_chinese(self):
        """测试中文关键词提取"""
        text = "Python是一种优秀的编程语言。Python易于学习。"
        keywords = self.extractor.extract_keywords(text)
        
        assert len(keywords) > 0
    
    def test_generate_summary(self):
        """测试摘要生成"""
        text = "First sentence about Python. Second sentence about programming. Third sentence about learning."
        summary = self.extractor.generate_summary(text, max_sentences=2)
        
        assert len(summary) > 0
        assert len(summary.split('.')) <= 3
    
    def test_build_toc(self):
        """测试目录构建"""
        headings = [
            {'level': 1, 'title': '第一章'},
            {'level': 2, 'title': '1.1 节'},
            {'level': 2, 'title': '1.2 节'},
            {'level': 1, 'title': '第二章'}
        ]
        
        toc = self.extractor.build_toc(headings)
        
        assert '目录' in toc
        assert '第一章' in toc
        assert '1.1 节' in toc
    
    def test_extract_entities(self):
        """测试实体识别"""
        text = """
        Contact: test@example.com
        Website: https://example.com
        Version: 1.2.3
        IP: 192.168.1.1
        Date: 2024-01-15
        """
        
        entities = self.extractor.extract_entities(text)
        
        assert 'test@example.com' in entities['emails']
        assert 'https://example.com' in entities['urls']
        assert '1.2.3' in entities['versions']
        assert '192.168.1.1' in entities['ips']
    
    def test_analyze_document(self):
        """测试完整文档分析"""
        text = "Python is great. Python is easy."
        
        analysis = self.extractor.analyze_document(text)
        
        assert 'statistics' in analysis
        assert 'keywords' in analysis
        assert 'summary' in analysis
        assert 'entities' in analysis
        assert 'readability' in analysis
        
        assert analysis['statistics']['total_words'] > 0
    
    def test_readability_analysis(self):
        """测试可读性分析"""
        text = "This is a simple sentence."
        
        analysis = self.extractor.analyze_document(text)
        readability = analysis['readability']
        
        assert 'score' in readability
        assert 'level' in readability
        assert 0 <= readability['score'] <= 100
