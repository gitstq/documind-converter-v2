"""
命令行界面 - 提供交互式终端体验
Command Line Interface - Interactive terminal experience
"""

import sys
import argparse
from pathlib import Path
from typing import Optional, List

from .converter import DocumentConverter
from .extractor import StructureExtractor
from .formatter import OutputFormatter
from .pipeline import BatchPipeline
from . import __version__


def create_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        prog='documind',
        description='🧠 DocuMind-Converter - 轻量级AI文档智能转换与结构化提取引擎',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  %(prog)s convert input.md -o output.html          # 单文件转换
  %(prog)s convert docs/*.md -o out/ -f json        # 批量转换
  %(prog)s analyze document.md                      # 分析文档
  %(prog)s batch "docs/**/*.txt" -o out/ -f html    # 批量处理

更多信息: https://github.com/gitstq/documind-converter
        '''
    )
    
    parser.add_argument(
        '-v', '--version',
        action='version',
        version=f'%(prog)s {__version__}'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='显示详细输出'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # convert 命令
    convert_parser = subparsers.add_parser(
        'convert',
        help='转换文档格式',
        description='将文档从一种格式转换为另一种格式'
    )
    convert_parser.add_argument(
        'input',
        help='输入文件路径或通配符'
    )
    convert_parser.add_argument(
        '-o', '--output',
        help='输出文件或目录路径'
    )
    convert_parser.add_argument(
        '-f', '--format',
        default='markdown',
        choices=['markdown', 'html', 'json', 'yaml', 'plain', 'structured'],
        help='输出格式 (默认: markdown)'
    )
    convert_parser.add_argument(
        '-t', '--theme',
        default='default',
        choices=['default', 'minimal', 'fancy'],
        help='输出主题 (默认: default)'
    )
    convert_parser.add_argument(
        '--no-toc',
        action='store_true',
        help='不包含目录'
    )
    convert_parser.add_argument(
        '--no-stats',
        action='store_true',
        help='不包含统计信息'
    )
    
    # analyze 命令
    analyze_parser = subparsers.add_parser(
        'analyze',
        help='分析文档结构',
        description='分析文档结构并生成报告'
    )
    analyze_parser.add_argument(
        'input',
        help='输入文件路径'
    )
    analyze_parser.add_argument(
        '-o', '--output',
        help='输出报告文件路径'
    )
    analyze_parser.add_argument(
        '-f', '--format',
        default='report',
        choices=['report', 'json', 'markdown'],
        help='报告格式 (默认: report)'
    )
    
    # batch 命令
    batch_parser = subparsers.add_parser(
        'batch',
        help='批量处理文档',
        description='批量转换多个文档'
    )
    batch_parser.add_argument(
        'pattern',
        help='文件匹配模式 (如 "docs/*.md" 或 "docs/**/*.txt")'
    )
    batch_parser.add_argument(
        '-o', '--output-dir',
        required=True,
        help='输出目录'
    )
    batch_parser.add_argument(
        '-f', '--format',
        default='markdown',
        choices=['markdown', 'html', 'json', 'yaml', 'plain', 'structured'],
        help='输出格式 (默认: markdown)'
    )
    batch_parser.add_argument(
        '-j', '--jobs',
        type=int,
        default=4,
        help='并行工作线程数 (默认: 4)'
    )
    
    # info 命令
    info_parser = subparsers.add_parser(
        'info',
        help='显示文档信息',
        description='显示文档的基本信息和统计'
    )
    info_parser.add_argument(
        'input',
        help='输入文件路径'
    )
    
    return parser


def handle_convert(args) -> int:
    """处理 convert 命令"""
    try:
        converter = DocumentConverter()
        
        # 检查是否是批量模式
        if '*' in args.input:
            pipeline = BatchPipeline(config={'verbose': args.verbose})
            results = pipeline.batch_convert(
                args.input,
                args.output or '.',
                args.format
            )
            
            if args.verbose:
                print(f"\n📊 结果:")
                print(f"  成功: {results['success']}")
                print(f"  失败: {results['failed']}")
                print(f"  总计: {results['total']}")
            
            return 0 if results['failed'] == 0 else 1
        
        # 单文件转换
        input_path = Path(args.input)
        if not input_path.exists():
            print(f"❌ 错误: 文件不存在: {input_path}")
            return 1
        
        output_path = args.output
        if not output_path:
            # 自动生成输出文件名
            suffix = '.md' if args.format == 'markdown' else f'.{args.format}'
            output_path = input_path.with_suffix(suffix)
        
        options = {
            'theme': args.theme,
            'include_toc': not args.no_toc,
            'include_stats': not args.no_stats
        }
        
        result = converter.convert(
            input_path,
            output_format=args.format,
            output_path=output_path,
            options=options
        )
        
        if args.verbose:
            print(f"✅ 转换完成: {input_path} -> {output_path}")
            print(f"   输出大小: {len(result)} 字符")
        
        return 0
    
    except Exception as e:
        print(f"❌ 转换失败: {e}")
        return 1


def handle_analyze(args) -> int:
    """处理 analyze 命令"""
    try:
        pipeline = BatchPipeline()
        result = pipeline.convert_with_analysis(
            args.input,
            args.output,
            args.format
        )
        
        if not args.output:
            print(result['content'])
        else:
            print(f"✅ 分析报告已保存: {args.output}")
        
        # 打印关键信息
        analysis = result['analysis']
        print(f"\n📊 分析摘要:")
        print(f"  关键词: {', '.join([kw[0] for kw in analysis['keywords'][:5]])}")
        print(f"  可读性: {analysis['readability']['score']}/100 ({analysis['readability']['level']})")
        
        return 0
    
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        return 1


def handle_batch(args) -> int:
    """处理 batch 命令"""
    try:
        pipeline = BatchPipeline(config={
            'max_workers': args.jobs,
            'verbose': True
        })
        
        results = pipeline.batch_convert(
            args.pattern,
            args.output_dir,
            args.format
        )
        
        print(f"\n{'='*50}")
        print(f"📊 批量处理完成")
        print(f"{'='*50}")
        print(f"  成功: {results['success']}")
        print(f"  失败: {results['failed']}")
        print(f"  总计: {results['total']}")
        
        if results['errors']:
            print(f"\n⚠️  错误详情:")
            for error in results['errors'][:5]:
                print(f"  - {error}")
        
        return 0 if results['failed'] == 0 else 1
    
    except Exception as e:
        print(f"❌ 批量处理失败: {e}")
        return 1


def handle_info(args) -> int:
    """处理 info 命令"""
    try:
        from .utils import FileUtils
        
        file_utils = FileUtils()
        content = file_utils.read_file(args.input)
        
        extractor = StructureExtractor()
        analysis = extractor.analyze_document(content)
        stats = analysis['statistics']
        
        print(f"\n📄 文件信息: {Path(args.input).name}")
        print(f"{'='*50}")
        print(f"  路径: {args.input}")
        print(f"  大小: {file_utils.get_file_size(args.input):,} 字节")
        print(f"  扩展名: {file_utils.get_file_extension(args.input)}")
        print(f"\n📊 内容统计:")
        print(f"  字符数: {stats['total_characters']:,}")
        print(f"  行数: {stats['total_lines']:,}")
        print(f"  词数: {stats['total_words']:,}")
        print(f"  中文字符: {stats['chinese_characters']:,}")
        print(f"  段落数: {stats['paragraphs']:,}")
        print(f"  代码块: {stats['code_blocks']:,}")
        print(f"\n📖 可读性:")
        print(f"  分数: {analysis['readability']['score']}/100")
        print(f"  等级: {analysis['readability']['level']}")
        print(f"\n🔑 关键词:")
        for kw in analysis['keywords'][:10]:
            print(f"  - {kw[0]} ({kw[1]:.3f})")
        
        return 0
    
    except Exception as e:
        print(f"❌ 获取信息失败: {e}")
        return 1


def main(args: Optional[List[str]] = None) -> int:
    """主入口函数"""
    parser = create_parser()
    parsed_args = parser.parse_args(args)
    
    if not parsed_args.command:
        parser.print_help()
        return 0
    
    handlers = {
        'convert': handle_convert,
        'analyze': handle_analyze,
        'batch': handle_batch,
        'info': handle_info,
    }
    
    handler = handlers.get(parsed_args.command)
    if handler:
        return handler(parsed_args)
    
    parser.print_help()
    return 0


if __name__ == '__main__':
    sys.exit(main())
