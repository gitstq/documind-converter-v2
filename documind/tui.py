"""
终端交互界面 (TUI) - 提供交互式文档处理体验
Terminal User Interface - Interactive document processing experience
"""

import os
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any


class SimpleTUI:
    """
    简化版终端交互界面
    使用标准输入输出实现，无需额外依赖
    """
    
    COLORS = {
        'reset': '\033[0m',
        'bold': '\033[1m',
        'dim': '\033[2m',
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m',
        'bg_blue': '\033[44m',
    }
    
    def __init__(self):
        self.width = self._get_terminal_width()
    
    def _get_terminal_width(self) -> int:
        """获取终端宽度"""
        try:
            return os.get_terminal_size().columns
        except:
            return 80
    
    def color(self, text: str, color: str) -> str:
        """添加颜色"""
        return f"{self.COLORS.get(color, '')}{text}{self.COLORS['reset']}"
    
    def print_header(self, title: str):
        """打印标题头"""
        width = min(self.width, 70)
        print()
        print(self.color('═' * width, 'cyan'))
        print(self.color(f"  {title}".center(width), 'bold'))
        print(self.color('═' * width, 'cyan'))
        print()
    
    def print_section(self, title: str):
        """打印章节标题"""
        print()
        print(self.color(f"▸ {title}", 'bold'))
        print(self.color('─' * min(len(title) + 4, self.width), 'dim'))
    
    def print_success(self, message: str):
        """打印成功消息"""
        print(self.color(f"✅ {message}", 'green'))
    
    def print_error(self, message: str):
        """打印错误消息"""
        print(self.color(f"❌ {message}", 'red'))
    
    def print_warning(self, message: str):
        """打印警告消息"""
        print(self.color(f"⚠️  {message}", 'yellow'))
    
    def print_info(self, message: str):
        """打印信息消息"""
        print(self.color(f"ℹ️  {message}", 'blue'))
    
    def print_menu(self, options: List[str], title: str = "请选择"):
        """打印菜单选项"""
        self.print_section(title)
        for i, option in enumerate(options, 1):
            print(f"  {self.color(str(i), 'cyan')}. {option}")
        print()
    
    def get_input(self, prompt: str, default: str = '') -> str:
        """获取用户输入"""
        if default:
            full_prompt = f"{prompt} [{default}]: "
        else:
            full_prompt = f"{prompt}: "
        
        try:
            value = input(self.color(full_prompt, 'yellow')).strip()
            return value if value else default
        except (EOFError, KeyboardInterrupt):
            print()
            return default
    
    def get_choice(self, prompt: str, options: List[str], default: int = 1) -> int:
        """获取用户选择"""
        self.print_menu(options, prompt)
        
        while True:
            try:
                choice = self.get_input("请输入选项", str(default))
                choice_num = int(choice)
                if 1 <= choice_num <= len(options):
                    return choice_num
                self.print_warning(f"请输入 1-{len(options)} 之间的数字")
            except ValueError:
                self.print_warning("请输入有效的数字")
    
    def confirm(self, prompt: str, default: bool = True) -> bool:
        """确认提示"""
        suffix = "[Y/n]" if default else "[y/N]"
        response = self.get_input(f"{prompt} {suffix}", "Y" if default else "N")
        return response.lower() in ('y', 'yes', '是', '确认')
    
    def print_progress(self, current: int, total: int, prefix: str = "进度"):
        """打印进度条"""
        if total == 0:
            return
        
        width = 40
        filled = int(width * current / total)
        bar = '█' * filled + '░' * (width - filled)
        percent = current / total * 100
        
        print(f"\r{prefix}: {self.color(bar, 'cyan')} {percent:.1f}% ({current}/{total})", end='', flush=True)
        
        if current >= total:
            print()
    
    def print_file_list(self, files: List[Dict[str, Any]]):
        """打印文件列表"""
        if not files:
            self.print_info("暂无文件")
            return
        
        print(f"  {'序号':<6}{'文件名':<30}{'大小':<12}{'状态':<10}")
        print(f"  {'─'*6}{'─'*30}{'─'*12}{'─'*10}")
        
        for i, f in enumerate(files, 1):
            name = f.get('name', 'unknown')[:28]
            size = self._format_size(f.get('size', 0))
            status = f.get('status', 'pending')
            
            status_colors = {
                'done': 'green',
                'processing': 'yellow',
                'error': 'red',
                'pending': 'dim'
            }
            
            status_icon = {'done': '✅', 'processing': '⏳', 'error': '❌', 'pending': '⬜'}
            
            print(f"  {i:<6}{name:<30}{size:<12}{self.color(status_icon.get(status, '?') + ' ' + status, status_colors.get(status, 'reset')):<10}")
    
    def _format_size(self, size: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    
    def print_stats(self, stats: Dict[str, Any]):
        """打印统计信息"""
        self.print_section("统计信息")
        
        items = [
            ("总字符数", stats.get('total_characters', 0)),
            ("总行数", stats.get('total_lines', 0)),
            ("总词数", stats.get('total_words', 0)),
            ("中文字符", stats.get('chinese_characters', 0)),
            ("段落数", stats.get('paragraphs', 0)),
            ("代码块", stats.get('code_blocks', 0)),
        ]
        
        for label, value in items:
            print(f"  {label:<12}: {self.color(str(value), 'cyan')}")
    
    def clear_screen(self):
        """清屏"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def wait_for_key(self, message: str = "按 Enter 键继续..."):
        """等待用户按键"""
        try:
            input(self.color(message, 'dim'))
        except (EOFError, KeyboardInterrupt):
            pass


class InteractiveApp:
    """
    交互式应用主类
    """
    
    def __init__(self):
        self.tui = SimpleTUI()
        self.converter = None
        self.extractor = None
        self.pipeline = None
    
    def run(self):
        """运行交互式应用"""
        self.tui.clear_screen()
        self.tui.print_header("🧠 DocuMind-Converter")
        print(self.tui.color("  轻量级AI文档智能转换与结构化提取引擎", 'dim'))
        print(self.tui.color("  Lightweight AI Document Intelligent Conversion & Structured Extraction Engine", 'dim'))
        print()
        
        while True:
            choice = self.tui.get_choice("主菜单", [
                "📄 单文件转换",
                "📁 批量转换",
                "🔍 文档分析",
                "ℹ️  文档信息",
                "❌ 退出"
            ])
            
            if choice == 1:
                self._single_convert()
            elif choice == 2:
                self._batch_convert()
            elif choice == 3:
                self._analyze_document()
            elif choice == 4:
                self._show_info()
            elif choice == 5:
                print()
                self.tui.print_info("感谢使用 DocuMind-Converter! 👋")
                break
    
    def _single_convert(self):
        """单文件转换"""
        self.tui.print_section("单文件转换")
        
        input_path = self.tui.get_input("请输入文件路径")
        if not input_path or not Path(input_path).exists():
            self.tui.print_error("文件不存在")
            return
        
        formats = ['markdown', 'html', 'json', 'yaml', 'plain', 'structured']
        format_choice = self.tui.get_choice("选择输出格式", formats)
        output_format = formats[format_choice - 1]
        
        output_path = self.tui.get_input("输出路径 (留空自动命名)", "")
        
        try:
            from .converter import DocumentConverter
            from .pipeline import BatchPipeline
            
            pipeline = BatchPipeline()
            result = pipeline.convert_with_analysis(
                input_path,
                output_path if output_path else None,
                output_format
            )
            
            self.tui.print_success(f"转换完成: {result['output'] or '已输出到控制台'}")
            
            # 显示分析摘要
            analysis = result['analysis']
            self.tui.print_stats(analysis['statistics'])
            
        except Exception as e:
            self.tui.print_error(f"转换失败: {e}")
        
        self.tui.wait_for_key()
    
    def _batch_convert(self):
        """批量转换"""
        self.tui.print_section("批量转换")
        
        pattern = self.tui.get_input("文件匹配模式 (如: docs/*.md)")
        if not pattern:
            self.tui.print_warning("未输入匹配模式")
            return
        
        output_dir = self.tui.get_input("输出目录", "output")
        
        formats = ['markdown', 'html', 'json', 'yaml', 'plain', 'structured']
        format_choice = self.tui.get_choice("选择输出格式", formats)
        output_format = formats[format_choice - 1]
        
        try:
            from .pipeline import BatchPipeline
            
            pipeline = BatchPipeline(config={'verbose': True})
            results = pipeline.batch_convert(pattern, output_dir, output_format)
            
            print()
            self.tui.print_success(f"批量转换完成!")
            print(f"  成功: {self.tui.color(str(results['success']), 'green')}")
            print(f"  失败: {self.tui.color(str(results['failed']), 'red') if results['failed'] > 0 else '0'}")
            print(f"  总计: {results['total']}")
            
        except Exception as e:
            self.tui.print_error(f"批量转换失败: {e}")
        
        self.tui.wait_for_key()
    
    def _analyze_document(self):
        """分析文档"""
        self.tui.print_section("文档分析")
        
        input_path = self.tui.get_input("请输入文件路径")
        if not input_path or not Path(input_path).exists():
            self.tui.print_error("文件不存在")
            return
        
        try:
            from .pipeline import BatchPipeline
            
            pipeline = BatchPipeline()
            result = pipeline.convert_with_analysis(input_path, None, 'report')
            
            print()
            print(result['content'])
            
        except Exception as e:
            self.tui.print_error(f"分析失败: {e}")
        
        self.tui.wait_for_key()
    
    def _show_info(self):
        """显示文档信息"""
        self.tui.print_section("文档信息")
        
        input_path = self.tui.get_input("请输入文件路径")
        if not input_path or not Path(input_path).exists():
            self.tui.print_error("文件不存在")
            return
        
        try:
            from .utils import FileUtils
            from .extractor import StructureExtractor
            
            file_utils = FileUtils()
            content = file_utils.read_file(input_path)
            extractor = StructureExtractor()
            analysis = extractor.analyze_document(content)
            
            print()
            self.tui.print_section(f"文件: {Path(input_path).name}")
            print(f"  路径: {input_path}")
            print(f"  大小: {file_utils.get_file_size(input_path):,} 字节")
            print(f"  扩展名: {file_utils.get_file_extension(input_path)}")
            
            self.tui.print_stats(analysis['statistics'])
            
            print()
            self.tui.print_section("关键词")
            for kw in analysis['keywords'][:10]:
                print(f"  • {kw[0]} ({kw[1]:.3f})")
            
            print()
            self.tui.print_section("可读性")
            readability = analysis['readability']
            print(f"  分数: {readability['score']}/100")
            print(f"  等级: {readability['level']}")
            
        except Exception as e:
            self.tui.print_error(f"获取信息失败: {e}")
        
        self.tui.wait_for_key()


def run_tui():
    """运行TUI应用"""
    try:
        app = InteractiveApp()
        app.run()
    except KeyboardInterrupt:
        print("\n\n已退出")
        sys.exit(0)
