# -*- coding: utf-8 -*-
"""
第三步功能模块：交互式地修正 Markdown 文件中非标准的“加粗标题”。

本模块为“双模式”，既可以被 GUI 程序导入，也可以作为独立的命令行工具运行。

如何使用:

1. 作为可导入的 GUI 模块 (推荐):
    主 GUI 脚本 (main_gui.py) 会导入本文件中的 `GuiBoldHeaderCorrector` 类，
    并通过图形化弹窗与用户交互。

2. 作为独立的命令行脚本:
    在终端中直接运行此文件，并提供需要处理的 Markdown 文件路径。
    脚本会通过命令行 `input()` 与用户进行交互。

    用法:
    python markdown_setting.py <输入文件.md>

    示例:
    python markdown_setting.py my_notes.md
"""

import os
import re
import sys
import tkinter as tk
from tkinter import messagebox
from typing import List, Optional, Tuple


# ==============================================================================
#  GUI 版本 - 供 main_gui.py 调用
# ==============================================================================
class HeaderLevelDialog:
    """一个自定义对话框，用于选择标题级别。"""

    def __init__(self, parent, title_text, allow_level_one, header_tree=None):
        self.parent = parent
        self.title_text = title_text
        self.allow_level_one = allow_level_one
        self.header_tree = header_tree or []
        self.result = None
        
        # 深色主题颜色
        self.colors = {
            'bg': '#1a1a1a',
            'fg': '#ffffff',
            'button': '#ff69b4',
            'frame_bg': '#2a2a2a',
            'text_bg': '#2a2a2a',
        }
        
        # 创建顶层窗口
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"修正标题: 【{self.title_text}】")
        self.dialog.configure(bg=self.colors['bg'])
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 设置窗口大小
        window_width = 900
        window_height = 550
        
        # 计算窗口位置（居中在父窗口）
        parent.update_idletasks()
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        x = parent_x + (parent_width - window_width) // 2
        y = parent_y + (parent_height - window_height) // 2
        
        self.dialog.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # 禁止调整大小
        self.dialog.resizable(False, False)
        
        # 创建内容
        self._create_widgets()
        
        # 等待窗口关闭
        self.dialog.wait_window()

    def _create_widgets(self):
        """创建对话框内容"""
        # 主框架（左右分栏）
        main_frame = tk.Frame(self.dialog, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # 左侧：树状图
        left_frame = tk.LabelFrame(
            main_frame, 
            text="🌳 已处理的标题结构",
            bg=self.colors['frame_bg'],
            fg=self.colors['button'],
            font=('Arial', 10, 'bold')
        )
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, 
                       padx=(0, 10), ipadx=10, ipady=10)
        
        # 创建文本框显示树状图
        tree_text = tk.Text(
            left_frame, 
            width=45, 
            height=22, 
            wrap=tk.NONE,
            bg=self.colors['text_bg'],
            fg=self.colors['fg'],
            font=('Consolas', 9)
        )
        tree_scrollbar_y = tk.Scrollbar(
            left_frame, orient=tk.VERTICAL, command=tree_text.yview)
        tree_scrollbar_x = tk.Scrollbar(
            left_frame, orient=tk.HORIZONTAL, command=tree_text.xview)
        tree_text.configure(
            yscrollcommand=tree_scrollbar_y.set,
            xscrollcommand=tree_scrollbar_x.set)
        
        tree_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        tree_scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        tree_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 填充树状图
        if self.header_tree:
            for level, text in self.header_tree:
                indent = "  " * (level - 1)
                tree_text.insert(tk.END, f"{indent}{'#' * level} {text}\n")
        else:
            tree_text.insert(tk.END, "（暂无已处理的标题）\n")
        
        tree_text.config(state=tk.DISABLED)
        
        # 右侧：选择区域
        right_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH)
        
        # 当前标题显示
        current_frame = tk.LabelFrame(
            right_frame, 
            text="📌 当前标题",
            bg=self.colors['frame_bg'],
            fg=self.colors['button'],
            font=('Arial', 10, 'bold')
        )
        current_frame.pack(fill=tk.X, pady=(0, 15), ipadx=10, ipady=10)
        
        title_label = tk.Label(
            current_frame,
            text=self.title_text,
            font=('Arial', 12, 'bold'),
            wraplength=300,
            justify=tk.LEFT,
            bg=self.colors['frame_bg'],
            fg=self.colors['fg']
        )
        title_label.pack(pady=10)
        
        # 选择级别
        select_frame = tk.LabelFrame(
            right_frame, 
            text="⚙ 选择标题级别",
            bg=self.colors['frame_bg'],
            fg=self.colors['button'],
            font=('Arial', 10, 'bold')
        )
        select_frame.pack(fill=tk.BOTH, expand=True, ipadx=10, ipady=10)
        
        valid_range = "1-6" if self.allow_level_one else "2-6"
        instruction_label = tk.Label(
            select_frame,
            text=f"请选择标题级别 ({valid_range})",
            font=('Arial', 10),
            bg=self.colors['frame_bg'],
            fg=self.colors['fg']
        )
        instruction_label.pack(pady=15)

        # 级别按钮（垂直排列）
        button_frame = tk.Frame(select_frame, bg=self.colors['frame_bg'])
        button_frame.pack(pady=10)

        start_level = 1 if self.allow_level_one else 2
        for i in range(start_level, 7):
            btn = tk.Button(
                button_frame,
                text=f"H{i} - {'#' * i}",
                width=18,
                height=2,
                font=('Arial', 10, 'bold'),
                bg=self.colors['button'],
                fg='white',
                activebackground='#ff1493',
                activeforeground='white',
                relief=tk.FLAT,
                cursor='hand2',
                command=lambda level=i: self._set_level_and_close(level)
            )
            btn.pack(pady=4)
        
        # 底部按钮
        bottom_frame = tk.Frame(select_frame, bg=self.colors['frame_bg'])
        bottom_frame.pack(side=tk.BOTTOM, pady=15)
        
        tk.Button(
            bottom_frame,
            text="⊗ 跳过此项",
            width=14,
            font=('Arial', 9, 'bold'),
            bg=self.colors['button'],
            fg='white',
            activebackground='#ff1493',
            relief=tk.FLAT,
            cursor='hand2',
            command=self._skip
        ).pack(side=tk.TOP, pady=3)
        
        tk.Button(
            bottom_frame,
            text="✖ 取消整个流程",
            width=14,
            font=('Arial', 9, 'bold'),
            bg=self.colors['button'],
            fg='white',
            activebackground='#ff1493',
            relief=tk.FLAT,
            cursor='hand2',
            command=self._cancel_process
        ).pack(side=tk.TOP, pady=3)
        
        # 绑定ESC键
        self.dialog.bind("<Escape>", lambda e: self._skip())

    def _set_level_and_close(self, level):
        """设置级别并关闭"""
        self.result = level
        self.dialog.destroy()

    def _skip(self):
        """跳过当前项"""
        self.result = "skip"
        self.dialog.destroy()

    def _cancel_process(self):
        """取消整个流程"""
        self.result = "cancel_all"
        self.dialog.destroy()


class GuiBoldHeaderCorrector:
    """交互式修正 Markdown 文件中"加粗标题"的类 (GUI版本)。"""

    def __init__(self, input_path: str, output_path: str, parent_ui):
        if not os.path.isfile(input_path):
            raise FileNotFoundError(f"错误：找不到文件 '{input_path}'。")
        self.input_path = input_path
        self.output_path = output_path
        self.parent_ui = parent_ui
        self.allow_level_one = True
        self.first_level_one_set = False
        self.user_cancelled = False
        self.header_tree = []  # 存储已处理的标题结构

    def correct(self) -> None:
        with open(self.input_path, 'r', encoding='utf-8') as f:
            lines: List[str] = f.readlines()
        new_lines: List[str] = []
        
        # 首先扫描文件，收集现有的标准标题
        self._collect_existing_headers(lines)
        
        for line in lines:
            if self.user_cancelled:
                new_lines.append(line)
                continue
            result = self._get_corrected_line(line)
            if result:
                corrected_line, level = result
                new_lines.append(corrected_line)
                if level == 1 and not self.first_level_one_set:
                    self._ask_to_disable_level_one()
            else:
                # 检查是否是已存在的标准标题，如果是则跳过
                standard_header = re.match(r'^(#{1,6})\s+(.+)$', line)
                if not standard_header:
                    new_lines.append(line)
                else:
                    new_lines.append(line)
        
        if self.user_cancelled:
            raise InterruptedError("用户取消了标题修正流程。")
        with open(self.output_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)

    def _collect_existing_headers(self, lines: List[str]) -> None:
        """收集文件中已存在的标准标题"""
        for line in lines:
            match = re.match(r'^(#{1,6})\s+(.+)$', line.strip())
            if match:
                level = len(match.group(1))
                text = match.group(2).strip()
                self.header_tree.append((level, text))

    def _get_corrected_line(self,
                            original_line: str) -> Optional[Tuple[str, int]]:
        match = re.match(r'^\s*\*\*(.*?)\*\*\s*$', original_line)
        if not match:
            return None
        header_text = match.group(1).strip()
        if not header_text:
            return None
        self.parent_ui.log(f"找到潜在标题: 【{header_text}】")
        dialog = HeaderLevelDialog(
            self.parent_ui.root,
            header_text,
            self.allow_level_one,
            self.header_tree
        )
        result = dialog.result
        if result == "skip":
            self.parent_ui.log("--> 已跳过，保留原样。")
            return None
        if result == "cancel_all":
            self.user_cancelled = True
            return None
        if isinstance(result, int):
            level = result
            corrected_header = f"{'#' * level} {header_text}\n"
            self.parent_ui.log(f"--> 已转换为 {level} 级标题。")
            # 将新转换的标题添加到树中
            self.header_tree.append((level, header_text))
            return (corrected_header, level)
        return None

    def _ask_to_disable_level_one(self) -> None:
        self.first_level_one_set = True
        answer = messagebox.askyesnocancel(
            "一级标题设置", "这是第一个一级标题。之后是否还需要设置一级标题？\n"
            "(Yes = 继续允许, No = 禁用, Cancel = 取消整个流程)",
            parent=self.parent_ui.root)
        if answer is None:
            self.user_cancelled = True
        elif not answer:
            self.allow_level_one = False
            self.parent_ui.log("--> 好的，后续将禁用一级标题的设置。")


# ==============================================================================
#  命令行版本 - 供直接运行时使用
# ==============================================================================
class BoldHeaderCorrector:
    """一个用于在命令行中交互式修正“加粗标题”的类。"""

    def __init__(self, input_path: str):
        if not os.path.isfile(input_path):
            raise FileNotFoundError(f"错误：找不到文件 '{input_path}'。")
        self.input_path = input_path
        self.allow_level_one = True
        self.first_level_one_set = False

    def _get_corrected_line_cli(
            self, original_line: str) -> Optional[Tuple[str, int]]:
        match = re.match(r'^\s*\*\*(.*?)\*\*\s*$', original_line)
        if not match:
            return None
        header_text = match.group(1).strip()
        if not header_text:
            return None
        print("-" * 50)
        print(f"找到潜在标题: 【{header_text}】")
        prompt_range = "1-6" if self.allow_level_one else "2-6"
        valid_levels = range(1, 7) if self.allow_level_one else range(2, 7)
        while True:
            try:
                prompt = f"请输入标题级别 ({prompt_range}), 或直接按 Enter 跳过: "
                level_input = input(prompt)
                if not level_input:
                    print("--> 已跳过，保留原样。")
                    return None
                level = int(level_input)
                if level in valid_levels:
                    corrected_header = f"{'#' * level} {header_text}\n"
                    print(f"--> 已转换为 {level} 级标题。")
                    return (corrected_header, level)
                print(f"无效输入，请输入 {prompt_range} 之间的数字。")
            except ValueError:
                print("无效输入，请输入一个数字。")

    def _ask_to_disable_level_one_cli(self) -> None:
        self.first_level_one_set = True
        while True:
            prompt = ("这是第一个一级标题。之后是否还需要设置一级标题? (y/n): ")
            answer = input(prompt).lower()
            if answer in ['y', 'yes']:
                break
            if answer in ['n', 'no']:
                self.allow_level_one = False
                print("--> 好的，后续将禁用一级标题的设置。")
                break
            print("无效输入，请输入 'y' 或 'n'。")

    def correct(self) -> None:
        with open(self.input_path, 'r', encoding='utf-8') as f:
            lines: List[str] = f.readlines()
        print(f"开始处理文件: {self.input_path}\n")
        new_lines: List[str] = []
        for line in lines:
            result = self._get_corrected_line_cli(line)
            if result:
                corrected_line, level = result
                new_lines.append(corrected_line)
                if level == 1 and not self.first_level_one_set:
                    self._ask_to_disable_level_one_cli()
            else:
                new_lines.append(line)
        base, ext = os.path.splitext(self.input_path)
        output_path = f"{base}_corrected{ext}"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print("-" * 50)
        print("\n处理完成！")
        print(f"修正后的内容已保存到新文件: '{output_path}'")


def main() -> None:
    """脚本作为独立程序运行的主入口点。"""
    if len(sys.argv) != 2:
        print("错误：请提供要处理的 Markdown 文件名。")
        print(f"用法: python {sys.argv[0]} <文件名.md>")
        sys.exit(1)
    input_file = sys.argv[1]
    try:
        # 当直接运行时，使用命令行版本的修正器
        corrector = BoldHeaderCorrector(input_file)
        corrector.correct()
    except FileNotFoundError as e:
        print(e, file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"处理过程中发生未知错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
