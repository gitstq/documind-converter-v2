"""
批处理管道 - 支持文件夹批量转换和管道处理
Batch Pipeline - Folder batch conversion and pipeline processing
"""

import os
import glob
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Union
from concurrent.futures import ThreadPoolExecutor, as_completed

from .converter import DocumentConverter
from .extractor import StructureExtractor
from .formatter import OutputFormatter


class BatchPipeline:
    """
    批处理管道
    支持批量文件转换、文件夹遍历、通配符匹配、并行处理
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.converter = DocumentConverter(self.config)
        self.extractor = StructureExtractor(self.config)
        self.formatter = OutputFormatter(config=self.config.get('format', {}))
        self.max_workers = self.config.get('max_workers', 4)
        self.verbose = self.config.get('verbose', True)
    
    def batch_convert(self,
                     input_pattern: str,
                     output_dir: Union[str, Path],
                     output_format: str = 'markdown',
                     options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        批量转换文件
        
        Args:
            input_pattern: 输入文件通配符模式 (如 "docs/*.md" 或 "docs/**/*.txt")
            output_dir: 输出目录
            output_format: 输出格式
            options: 转换选项
            
        Returns:
            处理结果统计
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 查找匹配的文件
        if '*' in input_pattern:
            files = glob.glob(input_pattern, recursive=True)
        else:
            files = [input_pattern]
        
        files = [f for f in files if os.path.isfile(f)]
        
        if not files:
            return {'success': 0, 'failed': 0, 'total': 0, 'errors': ['未找到匹配文件']}
        
        results = {'success': 0, 'failed': 0, 'total': len(files), 'errors': [], 'files': []}
        
        if self.verbose:
            print(f"🚀 开始批量转换: {len(files)} 个文件")
        
        # 并行处理
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {}
            for file_path in files:
                future = executor.submit(
                    self._process_single_file,
                    file_path, output_dir, output_format, options or {}
                )
                futures[future] = file_path
            
            for future in as_completed(futures):
                file_path = futures[future]
                try:
                    result = future.result()
                    if result['success']:
                        results['success'] += 1
                        results['files'].append(result)
                        if self.verbose:
                            print(f"  ✅ {Path(file_path).name}")
                    else:
                        results['failed'] += 1
                        results['errors'].append(f"{file_path}: {result['error']}")
                        if self.verbose:
                            print(f"  ❌ {Path(file_path).name}: {result['error']}")
                except Exception as e:
                    results['failed'] += 1
                    results['errors'].append(f"{file_path}: {str(e)}")
                    if self.verbose:
                        print(f"  ❌ {Path(file_path).name}: {str(e)}")
        
        if self.verbose:
            print(f"\n📊 完成: {results['success']}/{results['total']} 成功, {results['failed']} 失败")
        
        return results
    
    def _process_single_file(self, 
                            input_path: str,
                            output_dir: Path,
                            output_format: str,
                            options: Dict[str, Any]) -> Dict[str, Any]:
        """处理单个文件"""
        try:
            input_path = Path(input_path)
            
            # 生成输出文件名
            output_name = input_path.stem + f'.{output_format}'
            if output_format == 'markdown':
                output_name = input_path.stem + '.md'
            elif output_format == 'structured':
                output_name = input_path.stem + '.report.txt'
            
            output_path = output_dir / output_name
            
            # 转换
            result = self.converter.convert(
                input_path, 
                output_format=output_format,
                output_path=output_path,
                options=options
            )
            
            return {
                'success': True,
                'input': str(input_path),
                'output': str(output_path),
                'size': len(result)
            }
        
        except Exception as e:
            return {
                'success': False,
                'input': str(input_path),
                'error': str(e)
            }
    
    def convert_with_analysis(self,
                             input_path: Union[str, Path],
                             output_path: Optional[Union[str, Path]] = None,
                             output_format: str = 'markdown') -> Dict[str, Any]:
        """
        转换并分析文档
        
        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径
            output_format: 输出格式
            
        Returns:
            包含转换结果和分析结果的字典
        """
        input_path = Path(input_path)
        
        # 读取原始内容
        from .utils import FileUtils
        file_utils = FileUtils()
        raw_content = file_utils.read_file(input_path)
        
        # 解析文档
        ext = input_path.suffix.lower()
        parsers = {
            '.md': self.converter._parse_markdown,
            '.markdown': self.converter._parse_markdown,
            '.txt': self.converter._parse_plain_text,
            '.html': self.converter._parse_html,
            '.htm': self.converter._parse_html,
            '.json': self.converter._parse_json,
            '.yaml': self.converter._parse_yaml,
            '.yml': self.converter._parse_yaml,
            '.csv': self.converter._parse_csv,
            '.xml': self.converter._parse_xml,
        }
        
        if ext not in parsers:
            raise ValueError(f"不支持的文件格式: {ext}")
        
        parsed_data = parsers[ext](raw_content)
        
        # 分析文档
        analysis = self.extractor.analyze_document(raw_content)
        
        # 格式化输出
        formatted = self.formatter.format_document(parsed_data, analysis, output_format)
        
        # 保存
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            file_utils.write_file(output_path, formatted)
        
        return {
            'input': str(input_path),
            'output': str(output_path) if output_path else None,
            'format': output_format,
            'content': formatted,
            'analysis': analysis,
            'structure': parsed_data
        }
    
    def create_pipeline(self, *processors: Callable) -> Callable:
        """
        创建处理管道
        
        Args:
            *processors: 处理器函数列表
            
        Returns:
            管道函数
        """
        def pipeline(data):
            result = data
            for processor in processors:
                result = processor(result)
            return result
        
        return pipeline
    
    def watch_directory(self,
                       input_dir: Union[str, Path],
                       output_dir: Union[str, Path],
                   output_format: str = 'markdown',
                       interval: int = 5):
        """
        监视目录并自动转换新文件（简化版）
        
        Args:
            input_dir: 输入目录
            output_dir: 输出目录
            output_format: 输出格式
            interval: 检查间隔（秒）
        """
        import time
        
        input_dir = Path(input_dir)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        processed = set()
        
        print(f"👁️  监视目录: {input_dir}")
        print(f"   输出目录: {output_dir}")
        print(f"   按 Ctrl+C 停止\n")
        
        try:
            while True:
                # 查找所有支持的文件
                for ext in DocumentConverter.SUPPORTED_INPUT:
                    for file_path in input_dir.rglob(f'*{ext}'):
                        if str(file_path) not in processed:
                            try:
                                result = self.convert_with_analysis(
                                    file_path,
                                    output_dir / (file_path.stem + f'.{output_format}'),
                                    output_format
                                )
                                processed.add(str(file_path))
                                print(f"  ✅ 已处理: {file_path.name}")
                            except Exception as e:
                                print(f"  ❌ 失败: {file_path.name} - {e}")
                
                time.sleep(interval)
        
        except KeyboardInterrupt:
            print(f"\n🛑 停止监视，共处理 {len(processed)} 个文件")
