"""
智能结构提取器 - AI驱动的文档关键信息提取
Intelligent Structure Extractor - AI-powered document key information extraction
"""

import re
import json
from typing import Dict, List, Optional, Any, Tuple
from collections import Counter


class StructureExtractor:
    """
    文档结构智能提取器
    支持关键词提取、摘要生成、目录构建、实体识别（轻量级规则实现）
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.stopwords = self._load_stopwords()
        self.min_keyword_length = self.config.get('min_keyword_length', 2)
        self.max_keywords = self.config.get('max_keywords', 20)
    
    def _load_stopwords(self) -> set:
        """加载中英文停用词"""
        # 英文停用词
        en_stopwords = {
            'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
            'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'could', 'should', 'may', 'might', 'must', 'shall',
            'can', 'need', 'dare', 'ought', 'used', 'to', 'of', 'in',
            'for', 'on', 'with', 'at', 'by', 'from', 'as', 'into',
            'through', 'during', 'before', 'after', 'above', 'below',
            'between', 'under', 'and', 'but', 'or', 'yet', 'so', 'if',
            'because', 'although', 'though', 'while', 'where', 'when',
            'that', 'which', 'who', 'whom', 'whose', 'what', 'this',
            'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
            'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'its',
            'our', 'their', 'mine', 'yours', 'hers', 'ours', 'theirs',
            'myself', 'yourself', 'himself', 'herself', 'itself', 'ourselves',
            'themselves', 'what', 'which', 'who', 'when', 'where', 'why',
            'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most',
            'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own',
            'same', 'than', 'too', 'very', 'just', 'now', 'then', 'here',
            'there', 'once', 'again', 'further', 'also', 'back', 'still',
            'well', 'even', 'new', 'good', 'first', 'last', 'long', 'great',
            'little', 'own', 'old', 'right', 'big', 'high', 'different',
            'small', 'large', 'next', 'early', 'young', 'important', 'few',
            'public', 'bad', 'same', 'able', 'up', 'out', 'off', 'over',
            'down', 'on', 'all', 'any', 'both', 'each', 'few', 'more',
            'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only',
            'own', 'same', 'so', 'than', 'too', 'very', 'can', 'will',
            'just', 'should', 'now', 'using', 'use', 'used', 'based',
            'via', 'one', 'two', 'three', 'way', 'make', 'made', 'see',
            'get', 'got', 'go', 'going', 'gone', 'know', 'known', 'take',
            'taken', 'come', 'came', 'coming', 'think', 'thought', 'look',
            'looked', 'looking', 'want', 'wanted', 'give', 'given', 'giving',
            'find', 'found', 'finding', 'tell', 'told', 'telling', 'become',
            'became', 'becoming', 'leave', 'left', 'leaving', 'feel', 'felt',
            'feeling', 'put', 'putting', 'bring', 'brought', 'bringing',
            'begin', 'began', 'beginning', 'keep', 'kept', 'keeping',
            'hold', 'held', 'holding', 'write', 'wrote', 'written', 'writing',
            'stand', 'stood', 'standing', 'hear', 'heard', 'hearing',
            'let', 'letting', 'mean', 'meant', 'meaning', 'set', 'setting',
            'meet', 'met', 'meeting', 'pay', 'paid', 'paying', 'sit', 'sat',
            'sitting', 'speak', 'spoke', 'spoken', 'speaking', 'lie', 'lay',
            'lain', 'lying', 'lead', 'led', 'leading', 'read', 'reading',
            'grow', 'grew', 'grown', 'growing', 'lose', 'lost', 'losing',
            'fall', 'fell', 'fallen', 'falling', 'send', 'sent', 'sending',
            'build', 'built', 'building', 'understand', 'understood',
            'understanding', 'draw', 'drew', 'drawn', 'drawing', 'break',
            'broke', 'broken', 'breaking', 'spend', 'spent', 'spending',
            'cut', 'cutting', 'rise', 'rose', 'risen', 'rising', 'drive',
            'drove', 'driven', 'driving', 'buy', 'bought', 'buying', 'wear',
            'wore', 'worn', 'wearing', 'choose', 'chose', 'chosen', 'choosing'
        }
        
        # 中文停用词
        zh_stopwords = {
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人',
            '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去',
            '你', '会', '着', '没有', '看', '好', '自己', '这', '那',
            '这些', '那些', '这个', '那个', '之', '与', '及', '等',
            '或', '但', '而', '如果', '因为', '所以', '虽然', '但是',
            '可以', '需要', '进行', '通过', '对于', '关于', '以及',
            '其中', '其', '为', '以', '将', '被', '把', '让', '向',
            '从', '到', '对', '跟', '比', '给', '为', '于', '即',
            '便', '即使', '尽管', '不管', '无论', '只要', '只有',
            '无论', '不论', '不管', '尽管', '即使', '即便', '哪怕',
            '一些', '一定', '一样', '一般', '一直', '一切', '一种',
            '第一', '对于', '由于', '根据', '按照', '随着', '除了',
            '除', '之外', '以外', '以内', '以下', '以上', '以前',
            '以后', '以来', '以内', '以内', '时候', '时间', '地方',
            '人们', '东西', '事情', '工作', '问题', '部分', '情况',
            '系统', '方式', '方法', '过程', '结果', '原因', '目的',
            '作用', '意义', '价值', '特点', '优点', '缺点', '方面',
            '领域', '范围', '程度', '水平', '标准', '条件', '环境',
            '基础', '核心', '关键', '重点', '主要', '重要', '基本',
            '具体', '实际', '确实', '实在', '确实', '的确', '肯定',
            '可能', '也许', '大概', '大约', '差不多', '几乎', '简直',
            '根本', '完全', '十分', '非常', '特别', '相当', '比较',
            '相对', '绝对', '唯一', '仅仅', '只不过', '只是', '不过',
            '而已', '罢了', '算了', '也罢', '也好', '也行', '也行',
            '也是', '也是', '还是', '或者', '要么', '既', '又',
            '不但', '不仅', '不只', '不光', '不单', '不独', '而且',
            '并且', '况且', '何况', '再说', '再者', '否则', '不然',
            '要不', '要不然', '要么', '因为', '由于', '因此', '因而',
            '所以', '于是', '从而', '可见', '足见', '看来', '看起来',
            '看上去', '听起来', '说起来', '想起来', '做起来', '用起来',
            '看起来', '看上去', '听起来', '看起来', '看起来'
        }
        
        return en_stopwords | zh_stopwords
    
    def extract_keywords(self, text: str, top_n: Optional[int] = None) -> List[Tuple[str, float]]:
        """
        提取关键词（基于TF-IDF思想的轻量级实现）
        
        Args:
            text: 输入文本
            top_n: 返回前N个关键词
            
        Returns:
            [(关键词, 权重), ...]
        """
        top_n = top_n or self.max_keywords
        
        # 分词（支持中英文）
        words = self._tokenize(text)
        
        # 过滤停用词和短词
        filtered = [w for w in words 
                   if w.lower() not in self.stopwords 
                   and len(w) >= self.min_keyword_length
                   and not w.isdigit()]
        
        if not filtered:
            return []
        
        # 计算词频
        word_freq = Counter(filtered)
        total = len(filtered)
        
        # 计算TF分数（考虑词长奖励）
        scores = {}
        for word, freq in word_freq.most_common():
            tf = freq / total
            length_bonus = min(len(word) / 10, 1.5)  # 词长奖励
            scores[word] = tf * length_bonus
        
        # 提取n-gram短语
        bigrams = self._extract_ngrams(text, 2)
        trigrams = self._extract_ngrams(text, 3)
        
        for phrase in bigrams + trigrams:
            if phrase in scores:
                scores[phrase] *= 1.5  # 短语加分
            else:
                scores[phrase] = 0.3
        
        # 排序返回
        sorted_keywords = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_keywords[:top_n]
    
    def _tokenize(self, text: str) -> List[str]:
        """轻量级分词（支持中英文）"""
        words = []
        
        # 提取英文单词
        en_words = re.findall(r'[a-zA-Z]+', text)
        words.extend(en_words)
        
        # 提取中文词语（基于简单规则）
        zh_chars = re.findall(r'[\u4e00-\u9fff]+', text)
        for chars in zh_chars:
            # 简单2-4字切分
            for i in range(len(chars)):
                for length in [2, 3, 4]:
                    if i + length <= len(chars):
                        words.append(chars[i:i + length])
        
        return words
    
    def _extract_ngrams(self, text: str, n: int) -> List[str]:
        """提取n-gram短语"""
        # 清理文本
        cleaned = re.sub(r'[^\u4e00-\u9fffa-zA-Z0-9\s]', ' ', text)
        tokens = cleaned.split()
        
        ngrams = []
        for i in range(len(tokens) - n + 1):
            gram = ' '.join(tokens[i:i + n])
            if len(gram) >= 4:  # 过滤太短的结果
                ngrams.append(gram.lower())
        
        return ngrams
    
    def generate_summary(self, text: str, max_sentences: int = 3) -> str:
        """
        生成文本摘要（基于句子权重）
        
        Args:
            text: 输入文本
            max_sentences: 最大句子数
            
        Returns:
            摘要文本
        """
        sentences = self._split_sentences(text)
        if len(sentences) <= max_sentences:
            return text
        
        # 计算句子权重
        keywords = [kw[0] for kw in self.extract_keywords(text, top_n=30)]
        sentence_scores = []
        
        for i, sent in enumerate(sentences):
            score = 0
            
            # 关键词匹配
            for kw in keywords:
                if kw.lower() in sent.lower():
                    score += 1
            
            # 位置权重（开头和结尾的句子更重要）
            if i == 0:
                score *= 2.0
            elif i == len(sentences) - 1:
                score *= 1.5
            elif i < len(sentences) * 0.2:
                score *= 1.3
            
            # 长度惩罚（太长或太短的句子降权）
            word_count = len(sent.split())
            if word_count < 5:
                score *= 0.5
            elif word_count > 50:
                score *= 0.8
            
            sentence_scores.append((i, score, sent))
        
        # 选择Top N句子并保持原始顺序
        top_sentences = sorted(sentence_scores, key=lambda x: x[1], reverse=True)[:max_sentences]
        top_sentences.sort(key=lambda x: x[0])  # 按原始位置排序
        
        return ' '.join([s[2] for s in top_sentences])
    
    def _split_sentences(self, text: str) -> List[str]:
        """分割句子（支持中英文）"""
        # 中文句子分隔符
        text = re.sub(r'([。！？；])', r'\1\n', text)
        # 英文句子分隔符
        text = re.sub(r'([.!?])\s+', r'\1\n', text)
        
        sentences = [s.strip() for s in text.split('\n') if s.strip()]
        return sentences
    
    def build_toc(self, headings: List[Dict[str, Any]]) -> str:
        """
        构建目录（Table of Contents）
        
        Args:
            headings: 标题列表 [{'level': 1, 'title': '...'}, ...]
            
        Returns:
            Markdown格式的目录
        """
        lines = ['## 目录\n']
        
        for i, h in enumerate(headings):
            indent = '  ' * (h['level'] - 1)
            anchor = self._generate_anchor(h['title'])
            lines.append(f"{indent}- [{h['title']}](#{anchor})")
        
        return '\n'.join(lines) + '\n'
    
    def _generate_anchor(self, title: str) -> str:
        """生成锚点链接"""
        anchor = re.sub(r'[^\w\s\u4e00-\u9fff-]', '', title)
        anchor = re.sub(r'\s+', '-', anchor.strip())
        return anchor.lower()
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        轻量级实体识别（基于规则）
        
        Args:
            text: 输入文本
            
        Returns:
            {'emails': [...], 'urls': [...], 'ips': [...], 'dates': [...], 'versions': [...]}
        """
        entities = {
            'emails': [],
            'urls': [],
            'ips': [],
            'dates': [],
            'versions': [],
            'paths': [],
            'commands': []
        }
        
        # 邮箱
        entities['emails'] = list(set(re.findall(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text
        )))
        
        # URL
        entities['urls'] = list(set(re.findall(
            r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?',
            text
        )))
        
        # IP地址
        entities['ips'] = list(set(re.findall(
            r'\b(?:\d{1,3}\.){3}\d{1,3}\b', text
        )))
        
        # 日期
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',
            r'\d{4}/\d{2}/\d{2}',
            r'\d{2}-\d{2}-\d{4}',
            r'\d{2}/\d{2}/\d{4}',
            r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4}'
        ]
        for pattern in date_patterns:
            entities['dates'].extend(re.findall(pattern, text, re.IGNORECASE))
        entities['dates'] = list(set(entities['dates']))
        
        # 版本号
        entities['versions'] = list(set(re.findall(
            r'\bv?\d+\.\d+(?:\.\d+)?(?:-[\w.]+)?\b', text
        )))
        
        # 文件路径
        entities['paths'] = list(set(re.findall(
            r'(?:/[^/\s]+)+/?|(?:[A-Za-z]:\\[^\s]+)', text
        )))
        
        # 命令行命令
        entities['commands'] = list(set(re.findall(
            r'`([^`]+)`|(?:^|\n)\s*\$\s+(.+)', text
        )))
        
        return entities
    
    def analyze_document(self, content: str) -> Dict[str, Any]:
        """
        完整文档分析
        
        Args:
            content: 文档内容
            
        Returns:
            完整的分析结果字典
        """
        return {
            'statistics': self._get_statistics(content),
            'keywords': self.extract_keywords(content),
            'summary': self.generate_summary(content),
            'entities': self.extract_entities(content),
            'readability': self._analyze_readability(content)
        }
    
    def _get_statistics(self, content: str) -> Dict[str, int]:
        """获取文档统计信息"""
        lines = content.split('\n')
        words = content.split()
        chars = len(content)
        
        # 中文字符数
        zh_chars = len(re.findall(r'[\u4e00-\u9fff]', content))
        
        # 代码块检测
        code_blocks = len(re.findall(r'```', content)) // 2
        
        return {
            'total_characters': chars,
            'total_lines': len(lines),
            'total_words': len(words),
            'chinese_characters': zh_chars,
            'english_words': len(words) - zh_chars,
            'code_blocks': code_blocks,
            'paragraphs': len([l for l in lines if l.strip()])
        }
    
    def _analyze_readability(self, text: str) -> Dict[str, Any]:
        """
        可读性分析（简化版Flesch-Kincaid）
        """
        sentences = self._split_sentences(text)
        words = text.split()
        
        if not sentences or not words:
            return {'score': 0, 'level': 'unknown'}
        
        avg_sentence_length = len(words) / len(sentences)
        avg_word_length = sum(len(w) for w in words) / len(words)
        
        # 简化可读性分数 (0-100)
        score = max(0, min(100, 100 - (avg_sentence_length * 2) - (avg_word_length * 5)))
        
        if score >= 80:
            level = 'very_easy'
        elif score >= 60:
            level = 'easy'
        elif score >= 40:
            level = 'medium'
        elif score >= 20:
            level = 'difficult'
        else:
            level = 'very_difficult'
        
        return {
            'score': round(score, 2),
            'level': level,
            'avg_sentence_length': round(avg_sentence_length, 2),
            'avg_word_length': round(avg_word_length, 2)
        }
