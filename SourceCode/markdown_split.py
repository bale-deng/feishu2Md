# -*- coding: utf-8 -*-
"""
Markdown 文件拆分工具 (markdown_split.py)

本模块提供了一个命令行工具和一个可导入的类，用于根据指定级别的标题
将单个 Markdown 文件拆分成多个独立的文件。

功能特性:
- 可根据 `#`, `##`, `###` 等标题进行分割。
- 为每个标题及其内容创建一个新的 .md 文件。
- 自动清理标题以生成安全、有效的文件名。
- 在命令行模式下提供一个进度条。

如何使用:

1. 作为独立的命令行脚本:
    在终端中运行此文件，并提供输入和输出文件的路径。

    用法:
    python markdown_split.py <输入文件.md> [可选的输出文件夹]

    示例:
    python markdown_split.py my_notes.md my_split_notes

2. 作为可导入的模块:
    在您自己的 Python 脚本中导入 `MarkdownSplitter` 类来使用其核心功能。

    示例:
    from markdown_split import MarkdownSplitter

    try:
        # 初始化拆分器，传入输入文件和输出目录
        splitter = MarkdownSplitter('my_notes.md', 'my_split_notes')
        # 执行拆分，按三级标题分割，并关闭进度条显示
        splitter.split(split_by="###", show_progress=False)
        print("文件拆分成功！")
    except FileNotFoundError as e:
        print(e)
    except Exception as e:
        print(f"发生未知错误: {e}")
"""

import os
import re
import sys
from typing import List

# 尝试导入 tqdm 库，如果失败则提示用户安装
try:
    from tqdm import tqdm
except ImportError:
    print("错误：缺少 'tqdm' 库。")
    print("请先通过命令 'pip install tqdm' 来安装它。")
    sys.exit(1)


class MarkdownSplitter:
    """
    一个用于根据指定级别标题拆分 Markdown 文件的类。
    """

    def __init__(self, input_file: str, output_dir: str = 'output'):
        """
        初始化 MarkdownSplitter。

        Args:
            input_file: 要处理的输入 Markdown 文件的路径。
            output_dir: 用于存放拆分后文件的输出目录路径。

        Raises:
            FileNotFoundError: 如果输入文件不存在。
        """
        if not os.path.exists(input_file):
            error_msg = f"错误：找不到输入文件 '{input_file}'。请检查路径。"
            raise FileNotFoundError(error_msg)
        self.input_file = input_file
        self.output_dir = output_dir
        self.content: str = ""

    @staticmethod
    def _sanitize_filename(name: str) -> str:
        """
        清理字符串，使其成为一个有效的文件名。
        这是一个静态方法，因为它不依赖于任何实例状态。
        """
        # 移除标题前的 # 号和空格
        name = re.sub(r'^[#\s]+', '', name.strip())
        # 移除 Windows 和 aLinux 不支持的文件名字符
        name = re.sub(r'[\\/*?:"<>|]', "", name)
        # 将连续的空格替换为下划线
        name = re.sub(r'\s+', '_', name)
        # 限制文件名长度
        return name[:100]

    def _read_content(self) -> bool:
        """从输入文件读取内容，如果成功则返回 True。"""
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                self.content = f.read()
            return True
        except Exception as e:
            print(f"读取文件时发生错误：{e}")
            return False

    def split(self, split_by: str = "##", show_progress: bool = True) -> None:
        """
        执行拆分操作。

        Args:
            split_by: 用于拆分的标题级别, 例如 "##" 或 "###"。
            show_progress: 是否在控制台显示进度条。对于外部调用，建议设为 False。
        """
        if not self._read_content():
            print("文件内容为空或读取失败，已中止操作。")
            return

        os.makedirs(self.output_dir, exist_ok=True)

        # 根据传入的 split_by 参数构建动态的正则表达式
        split_pattern = re.escape(split_by)
        regex = rf'(\n{split_pattern}\s.*)\n'
        sections: List[str] = re.split(regex, self.content)

        # 处理第一个标题之前的内容 (前言部分)
        prologue: str = sections[0].strip()
        if prologue:
            filename = "00_前言.md"
            filepath = os.path.join(self.output_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(prologue)
            if show_progress:
                print(f"已创建前言文件: {filepath}")

        # 设置循环迭代器，根据参数决定是否使用 tqdm 包装
        section_pairs = range(1, len(sections), 2)
        iterator = (tqdm(section_pairs, desc="正在拆分文件", unit="个文件")
                    if show_progress else section_pairs)

        if show_progress and len(sections) > 1:
            print(f"\n开始处理 {split_by} 级标题并生成文件...")

        for i in iterator:
            header: str = sections[i].strip()
            body: str = ""
            if (i + 1) < len(sections):
                body = sections[i + 1].strip()

            filename = self._sanitize_filename(header) + ".md"
            filepath = os.path.join(self.output_dir, filename)

            full_content = f"{header}\n\n{body}"
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(full_content)

        if show_progress:
            print(f"\n处理完成！所有文件已保存在 '{self.output_dir}' 文件夹中。")


def main() -> None:
    """
    脚本的主入口点，处理命令行参数。
    """
    if len(sys.argv) < 2:
        print("错误：请提供要处理的 Markdown 文件名。")
        print(f"用法: python {sys.argv[0]} <输入文件名> [可选的输出文件夹名]")
        print(f"示例: python {sys.argv[0]} my_notes.md")
        sys.exit(1)

    input_file_path: str = sys.argv[1]
    if len(sys.argv) > 2:
        output_directory_path: str = sys.argv[2]
    else:
        output_directory_path: str = 'output'

    try:
        splitter = MarkdownSplitter(input_file_path, output_directory_path)
        # 命令行模式默认使用 "##" 进行拆分
        splitter.split()
    except FileNotFoundError as e:
        print(e)
    except Exception as e:
        print(f"处理过程中发生未知错误: {e}")


if __name__ == "__main__":
    main()
