# -*- coding: utf-8 -*-
"""
Markdown 处理工具 - 命令行版本 (main.py)

本脚本提供一键式处理流程，自动执行所有五个步骤：
1. Word 转 Markdown (docx_to_markdown.py)
2. 清理 HTML 格式 (markdown_cleaner.py)
3. 修正代码块 (markdown_repair.py)
4. 修正标题 (markdown_setting.py)
5. 文件分块 (markdown_split.py)

用法:
    python main.py <输入文件.docx> [输出目录]

示例:
    python main.py document.docx output
    python main.py "E:\TestProgram\周报上位机\飞镖上位机周报.docx" "E:\TestProgram\output"
"""

import os
import sys
import shutil
from pathlib import Path


def check_and_install_dependencies():
    """检测并安装缺失的依赖。"""
    missing_deps = []

    # 检查Python包
    try:
        import tqdm
    except ImportError:
        missing_deps.append('tqdm')

    try:
        import docx
    except ImportError:
        missing_deps.append('python-docx')

    # 检查Pandoc
    pandoc_missing = shutil.which("pandoc") is None

    if missing_deps or pandoc_missing:
        print("\n" + "=" * 70)
        print("⚠ 检测到缺失的依赖")
        print("=" * 70)

        if missing_deps:
            print(f"\n缺少 Python 包: {', '.join(missing_deps)}")

        if pandoc_missing:
            print("\n缺少 Pandoc（必需的外部程序）")

        print("\n推荐使用自动安装工具:")
        print("  python install_dependencies.py")
        print("\n或手动安装:")
        if missing_deps:
            print(f"  pip install {' '.join(missing_deps)}")
        if pandoc_missing:
            print("  访问 https://pandoc.org/installing.html")

        choice = input("\n是否现在自动安装? (y/n): ").lower().strip()

        if choice == 'y':
            print("\n正在调用自动安装工具...")
            try:
                import subprocess
                result = subprocess.run(
                    [sys.executable, "install_dependencies.py", "--auto"],
                    check=False
                )
                if result.returncode == 0:
                    print("\n✓ 依赖安装完成！请重新运行此脚本。")
                else:
                    print("\n⚠ 安装过程中出现问题，请手动安装依赖。")
                sys.exit(0)
            except Exception as e:
                print(f"\n✗ 自动安装失败: {e}")
                print("请手动运行: python install_dependencies.py")
                sys.exit(1)
        else:
            print("\n请先安装依赖，然后重新运行此脚本。")
            sys.exit(1)


# 首先检查依赖
check_and_install_dependencies()

# 导入各个处理模块
from docx_to_markdown import PandocConverter
from markdown_cleaner import MarkdownCleaner
from markdown_repair import CodeBlockProcessor
from markdown_setting import BoldHeaderCorrector
from markdown_split import MarkdownSplitter


class MarkdownProcessor:
    """Markdown 处理器主类，负责协调所有处理步骤。"""

    def __init__(self, docx_path: str, output_dir: str = None):
        """
        初始化处理器。

        Args:
            docx_path: 输入的 Word 文件路径
            output_dir: 输出目录路径，默认为输入文件所在目录下的output文件夹
        """
        self.docx_path = docx_path

        # 如果未指定输出目录，使用输入文件所在目录下的output文件夹
        if output_dir is None:
            input_dir = os.path.dirname(os.path.abspath(docx_path))
            self.output_dir = os.path.join(input_dir, 'output')
        else:
            self.output_dir = output_dir

        self.base_name = Path(docx_path).stem

        # 创建输出目录
        os.makedirs(self.output_dir, exist_ok=True)

        # 定义中间文件路径
        self.step1_output = os.path.join(self.output_dir, f"{self.base_name}.md")
        self.step2_output = os.path.join(self.output_dir, f"{self.base_name}_cleaned.md")
        self.step3_output = os.path.join(self.output_dir, f"{self.base_name}_repaired.md")
        self.step4_output = os.path.join(self.output_dir, f"{self.base_name}_repaired_corrected.md")
        self.step5_output_dir = os.path.join(self.output_dir, f"{self.base_name}_split")

    def print_step(self, step_num: int, total: int, description: str):
        """打印步骤信息。"""
        print("\n" + "=" * 70)
        print(f"步骤 {step_num}/{total}: {description}")
        print("=" * 70)

    def step1_convert_docx(self) -> bool:
        """步骤 1: 将 Word 文档转换为 Markdown。"""
        self.print_step(1, 5, "Word 转 Markdown")
        try:
            converter = PandocConverter(self.docx_path, self.output_dir)
            md_path = converter.convert()
            print(f"✓ 成功生成: {md_path}")
            return True
        except Exception as e:
            print(f"✗ 错误: {e}")
            return False

    def step2_clean_markdown(self) -> bool:
        """步骤 2: 清理 Markdown 中的 HTML 格式。"""
        self.print_step(2, 5, "清理 HTML 格式")
        try:
            cleaner = MarkdownCleaner(self.step1_output, self.step2_output)
            cleaner.clean()
            print(f"✓ 成功生成: {self.step2_output}")
            return True
        except Exception as e:
            print(f"✗ 错误: {e}")
            return False

    def step3_repair_code_blocks(self) -> bool:
        """步骤 3: 修正代码块格式（交互式）。"""
        self.print_step(3, 5, "修正代码块格式")
        try:
            print("注意: 此步骤需要交互式输入。")
            print("-" * 70)

            with open(self.step2_output, 'r', encoding='utf-8') as f:
                content = f.read()

            processor = CodeBlockProcessor()
            corrected_content = processor.run(content)

            with open(self.step3_output, 'w', encoding='utf-8') as f:
                f.write(corrected_content)

            print(f"✓ 成功生成: {self.step3_output}")
            return True
        except Exception as e:
            print(f"✗ 错误: {e}")
            return False

    def step4_correct_headers(self) -> bool:
        """步骤 4: 修正标题格式（交互式）。"""
        self.print_step(4, 5, "修正标题格式")
        try:
            print("注意: 此步骤需要交互式输入。")
            print("-" * 70)

            corrector = BoldHeaderCorrector(self.step3_output)
            corrector.correct()

            print(f"✓ 成功生成: {self.step4_output}")
            return True
        except Exception as e:
            print(f"✗ 错误: {e}")
            return False

    def step5_split_markdown(self) -> bool:
        """步骤 5: 按标题拆分文件。"""
        self.print_step(5, 5, "按标题拆分文件")
        try:
            splitter = MarkdownSplitter(self.step4_output, self.step5_output_dir)
            splitter.split(split_by="##", show_progress=True)
            print(f"✓ 成功生成拆分文件到: {self.step5_output_dir}")
            return True
        except Exception as e:
            print(f"✗ 错误: {e}")
            return False

    def process_all(self, skip_steps: list = None) -> bool:
        """
        执行所有处理步骤。

        Args:
            skip_steps: 要跳过的步骤列表，例如 [4, 5]

        Returns:
            处理是否成功
        """
        skip_steps = skip_steps or []

        print("\n" + "=" * 70)
        print("Markdown 处理工具 - 自动化处理流程")
        print("=" * 70)
        print(f"输入文件: {self.docx_path}")
        print(f"输出目录: {self.output_dir}")
        print("=" * 70)

        steps = [
            (1, self.step1_convert_docx),
            (2, self.step2_clean_markdown),
            (3, self.step3_repair_code_blocks),
            (4, self.step4_correct_headers),
            (5, self.step5_split_markdown)
        ]

        for step_num, step_func in steps:
            if step_num in skip_steps:
                print(f"\n⊘ 跳过步骤 {step_num}")
                continue

            if not step_func():
                print(f"\n✗ 步骤 {step_num} 失败，流程中止。")
                return False

        print("\n" + "=" * 70)
        print("✓ 所有步骤完成！")
        print("=" * 70)
        print(f"\n最终输出:")
        print(f"  - 完整文件: {self.step4_output}")
        print(f"  - 拆分文件: {self.step5_output_dir}")
        print("=" * 70 + "\n")

        return True


def main():
    """主函数，处理命令行参数。"""
    # 检查命令行参数
    if len(sys.argv) < 2:
        print("错误: 缺少必要参数！\n")
        print("用法: python main.py <输入文件.docx> [输出目录]")
        print("\n示例:")
        print('  python main.py document.docx')
        print('  python main.py document.docx output')
        print('  python main.py "E:\\TestProgram\\周报上位机\\飞镖上位机周报.docx" "E:\\TestProgram\\output"')
        sys.exit(1)

    docx_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else 'output'

    # 检查输入文件是否存在
    if not os.path.exists(docx_file):
        print(f"错误: 文件不存在 -> {docx_file}")
        sys.exit(1)

    # 检查文件扩展名
    if not docx_file.lower().endswith('.docx'):
        print("警告: 输入文件不是 .docx 格式，可能无法正确处理。")
        choice = input("是否继续? (y/n): ").lower()
        if choice != 'y':
            print("已取消。")
            sys.exit(0)

    # 询问是否跳过某些步骤
    print("\n您可以选择跳过某些步骤（通常建议执行所有步骤）:")
    print("  步骤 1: Word 转 Markdown")
    print("  步骤 2: 清理 HTML 格式")
    print("  步骤 3: 修正代码块 (需要交互)")
    print("  步骤 4: 修正标题 (需要交互)")
    print("  步骤 5: 文件拆分")

    skip_input = input("\n要跳过的步骤 (用逗号分隔，如: 4,5)，直接回车执行所有步骤: ").strip()
    skip_steps = []
    if skip_input:
        try:
            skip_steps = [int(s.strip()) for s in skip_input.split(',')]
        except ValueError:
            print("输入格式错误，将执行所有步骤。")

    # 创建处理器并执行
    try:
        processor = MarkdownProcessor(docx_file, output_dir)
        success = processor.process_all(skip_steps=skip_steps)

        if success:
            sys.exit(0)
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n用户中断操作。")
        sys.exit(1)
    except Exception as e:
        print(f"\n发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
