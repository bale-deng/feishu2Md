# -*- coding: utf-8 -*-
"""
Markdown 代码块修复与重构工具 (markdown_repair.py)

本模块提供了用于查找、解析和重构 Markdown 文件中不规范代码块的功能。

功能特性 (新版):
- (新) 增加代码块内代码格式化功能 (实验性)，可自动处理缩进和操作符间距。
- (新) 增加代码块内容清理功能，自动移除错误的 `*...*` 和 `**...**` 强调格式。
- (新) 采用全新的、更稳健的解析引擎，能够正确处理代码块内部包含'---'分隔符的情况。
- (新) 增加预处理步骤，能够自动发现并拆分被错误合并的代码块分隔符。
- (新) 增加完整性检查，能够自动发现并修复未闭合的代码块。
- (新) 用户可以自定义用于自动修正的默认语言 (不再硬编码为 'c')。
- (已修复) 彻底重构了标题的验证逻辑，能够正确解析 '---' 块中的任意合法标题。
- (已修复) 彻底重构了代码块的解析逻辑，能正确处理同时包含语言和标题的格式。
- (新) 能够智能地将未命名代码块内容的第一行识别为语言类型。
- (新) 自动为修正后的代码块内容添加 '演示' 作为第一行标题。
- 完整保留代码块内部的所有格式。
- 支持交互式地为代码块指定语言类型。
"""

import re
import sys
from typing import Optional, Tuple


class CodeBlockProcessor:
    """
    一个用于查找、解析和重构 Markdown 代码块的类。
    """
    KNOWN_LANGUAGES = {
        'c', 'cpp', 'c++', 'python', 'py', 'java', 'javascript', 'js', 'html',
        'css', 'yaml', 'bash', 'shell', 'sh', 'sql', 'go', 'rust',
        'typescript', 'ts', 'markdown', 'json', 'xml', 'ruby', 'php'
    }

    def __init__(self):
        """初始化处理器状态。"""
        self.mode: Optional[str] = None
        self.target_lang_all: Optional[str] = None
        self.block_count: int = 0
        self.default_lang: str = 'c'  # 默认的备用语言
        self.format_code: bool = True  # (修改) 默认启用代码格式化
        self.block_finder_regex = re.compile(r"^```[\s\S]+?^```", re.MULTILINE)

    def _pre_process_fused_blocks(self, markdown_text: str) -> str:
        """
        (新增) 预处理文本，将紧邻的、可能是错误合并的代码块分隔符拆开。
        例如，将 ` ````` ` 修正为 ` ```\n``` `。
        """
        corrected_text = re.sub(r"^(```\s*)(```.*)$",
                                r"\1\n\2",
                                markdown_text,
                                flags=re.MULTILINE)
        if corrected_text != markdown_text:
            print("检测到并已分离错误合并的代码块分隔符。")

        return corrected_text

    def _validate_identifier(self, identifier: str, context: str) -> bool:
        """(已重构) 根据上下文，检查字符串是否为合法的语言或标题标识符。"""
        if not identifier:
            return True
        if not re.fullmatch(r'[a-zA-Z0-9_.-]+', identifier):
            return False
        if identifier.lower() == '演示':
            return True

        if context == 'first_part':
            return identifier.lower() in self.KNOWN_LANGUAGES

        if context == 'title_line':
            # 核心修正：对于标题行，任何合法的标识符都是有效的。
            return True

        # 若上下文无效，则返回 False
        return False

    def _process_dashed_content(self, content: str) -> str:
        """(新增) 处理一个 '---' 块的内部内容并将其转换为 ``` 块字符串。"""
        content = re.sub(r'\\\s*$', '', content, flags=re.MULTILINE).strip()
        lines = content.split('\n')
        lang, title = '', ''
        while lines and not lines[0].strip():
            lines.pop(0)
        if lines and self._validate_identifier(lines[0].strip(),
                                               context='first_part'):
            lang = lines.pop(0).strip()
        if lines and self._validate_identifier(lines[0].strip(),
                                               context='title_line'):
            title = lines.pop(0).strip()
        code_lines = lines
        lang_spec = lang
        if title:
            lang_spec += f" {title}"
        final_code = '\n'.join(code_lines)
        return f"```{lang_spec}\n{final_code}\n```"

    def _clean_code_content(self, code_text: str) -> str:
        """
        (新增) 清理代码块内部的文本，移除 Pandoc 错误添加的强调符号。
        """
        # 优先处理双星号（加粗），避免与单星号冲突
        # 例如：(void)**pvParameters**; -> (void)pvParameters;
        cleaned_text = re.sub(r'(?<!\w)\*\*(\w+)\*\*(?!\w)', r'\1', code_text)
        # 处理单星号（斜体）
        # 例如：(void)*pvParameters*; -> (void)pvParameters;
        cleaned_text = re.sub(r'(?<!\w)\*(\w+)\*(?!\w)', r'\1', cleaned_text)
        return cleaned_text

    def _format_code_content(self, code_text: str) -> str:
        """
        (新增-实验性) 对代码块内的代码进行格式化。
        - { } 内的代码行进行缩进。
        - =, +, -, / 符号前后添加空格。
        """
        formatted_lines = []
        indent_level = 0
        indent_size = 4

        lines = code_text.split('\n')

        for line in lines:
            # (新增) 检查是否为分隔线，如果是则不进行任何格式化
            trimmed_for_check = line.strip()
            if re.fullmatch(r'-{3,}', trimmed_for_check):
                formatted_lines.append(line)
                continue

            # ---- 操作符间距逻辑 ----
            # 1. 在所有目标操作符前后添加空格
            processed_line = re.sub(r'\s*([=+\-/])\s*', r' \1 ', line)

            # 2. 重新连接被意外分开的复合操作符
            processed_line = processed_line.replace('+ =', '+=')
            processed_line = processed_line.replace('- =', '-=')
            processed_line = processed_line.replace('* =', '*=')
            processed_line = processed_line.replace('/ =', '/=')
            processed_line = processed_line.replace('= =', '==')
            processed_line = processed_line.replace('! =', '!=')
            processed_line = processed_line.replace('+ +', '++')
            processed_line = processed_line.replace('- -', '--')

            trimmed_line = processed_line.strip()

            # ---- 缩进逻辑 ----
            # 如果行以 '}' 开头，则减少缩进
            if trimmed_line.startswith('}'):
                indent_level = max(0, indent_level - 1)

            current_indent = ' ' * (indent_level * indent_size)

            formatted_lines.append(current_indent + trimmed_line)

            # 根据大括号的数量更新下一行的缩进级别
            open_braces = trimmed_line.count('{')
            close_braces = trimmed_line.count('}')
            indent_level += (open_braces - close_braces)
            indent_level = max(0, indent_level)

        return '\n'.join(formatted_lines)

    def _deconstruct_block(self, block_text: str) -> Tuple[str, str]:
        """
        (已重构) 采用更稳健的逻辑解析代码块的第一行，正确处理语言和标题。
        """
        lines = block_text.split('\n')
        if lines and not lines[0].strip():
            lines.pop(0)
        if lines and not lines[-1].strip():
            lines.pop(-1)
        if not lines:
            return '', ''

        first_line = lines[0]
        original_lang = ''
        code_parts = []

        match = re.match(r'^```(\S*)\s*(.*)$', first_line)
        if match:
            first_part = match.group(1)
            second_part = match.group(2).strip()

            if self._validate_identifier(first_part, context='first_part'):
                original_lang = first_part
                if second_part:
                    if self._validate_identifier(second_part,
                                                 context='title_line'):
                        original_lang += f" {second_part}"
                    else:
                        code_parts.append(second_part)
            elif first_part.lower() == '演示':
                original_lang = '__DEMO__'
                if second_part:
                    code_parts.append(second_part)
            else:
                original_lang = '__INVALID__'
                full_content = f"{first_part} {second_part}".strip()
                if full_content:
                    code_parts.append(full_content)
        else:
            original_lang = '__INVALID__'
            code_parts.append(first_line)

        content_lines = lines[1:-1]

        if content_lines and not original_lang:
            potential_lang = content_lines[0].strip()
            is_valid_lang = (self._validate_identifier(potential_lang,
                                                       context='first_part')
                             and ' ' not in potential_lang)
            if is_valid_lang:
                original_lang = potential_lang
                content_lines.pop(0)

        is_simple_lang = (' ' not in original_lang
                          and original_lang not in ['__INVALID__', '__DEMO__'])
        if content_lines and original_lang and is_simple_lang:
            potential_title = content_lines[0].strip()
            if potential_title:
                if self._validate_identifier(potential_title,
                                             context='title_line'):
                    original_lang = f"{original_lang} {potential_title}"
                    content_lines.pop(0)

        code_parts.extend(content_lines)
        clean_code = '\n'.join(code_parts)
        return original_lang, clean_code

    def _get_target_language(self, original_lang: str, code: str) -> str:
        """根据用户选择的模式，获取代码块的目标语言。"""
        if self.mode == 'all':
            return self.target_lang_all or ''
        print("-" * 60)
        print(f"发现第 {self.block_count} 个代码块 (原语言: "
              f"{original_lang or '未指定'})")
        snippet = '\n'.join(code.split('\n')[:7])
        if len(code.split('\n')) > 7:
            snippet += '\n...'
        print("代码片段预览:")
        print(snippet)
        print("-" * 60)
        prompt = ("请输入此代码块的新语言 (如: java, python, c)。\n"
                  "直接按 Enter 会保留原样；输入 'none' 则移除语言标识: ")
        user_input = input(prompt).strip().lower()
        if user_input == 'none':
            return ''
        return user_input or original_lang

    def _replacement_callback(self, match: re.Match) -> str:
        """这是 re.sub 的核心回调函数，对每个匹配到的代码块进行处理。"""
        self.block_count += 1
        full_block_text = match.group(0)
        original_lang, clean_code = self._deconstruct_block(full_block_text)

        # 清理代码块内部的强调格式
        clean_code = self._clean_code_content(clean_code)

        # 根据用户选择，格式化代码
        if self.format_code:
            clean_code = self._format_code_content(clean_code)

        target_lang = original_lang
        final_code = clean_code

        needs_fixing = (original_lang in ['__INVALID__', '__DEMO__']
                        or not original_lang)
        if needs_fixing:
            if original_lang == '__INVALID__':
                message = "标识符不合法"
            elif original_lang == '__DEMO__':
                message = "'演示'占位符"
            else:
                message = "未命名"
            print("-" * 60)
            print(f"发现第 {self.block_count} 个代码块 ({message})，已自动修正。")
            target_lang = self.default_lang
            if not clean_code.strip().startswith('演示'):
                final_code = f"演示\n{clean_code}" if clean_code else "演示"
            else:
                final_code = clean_code
        else:
            target_lang = self._get_target_language(original_lang, clean_code)
            final_code = clean_code

        final_code = final_code.strip()
        if target_lang:
            return f"```{target_lang}\n{final_code}\n```"
        return f"```\n{final_code}\n```"

    def _fix_unterminated_blocks(self, markdown_text: str) -> str:
        """
        (新增) 查找并修复未闭合的代码块，作为最后一步的安全检查。
        """
        lines = markdown_text.split('\n')
        in_block = False
        fence = '```'

        for line in lines:
            is_fence = (line.strip().startswith(fence)
                        and len(line.strip().replace('`', '')) < 15)
            if is_fence:
                in_block = not in_block

        if in_block:
            print("-" * 60)
            print("警告: 检测到文件末尾存在一个未闭合的代码块。")
            print("已在文件末尾自动添加闭合标签 '```'。")
            return markdown_text.rstrip() + '\n```\n'

        return markdown_text

    def run(self, markdown_text: str) -> str:
        """(已重构) 运行处理器的主函数，采用更稳健的解析逻辑。"""
        while not self.mode:
            prompt = ("请选择操作模式:\n"
                      "  [A] - 将所有代码块转换为同一种语言\n"
                      "  [I] - 逐个决定每个代码块的语言\n"
                      "请输入 (A/I): ")
            choice = input(prompt).strip().lower()
            if choice in ['a', 'i']:
                self.mode = 'all' if choice == 'a' else 'individual'
            else:
                print("无效输入，请重新选择。")

        # (修改) 移除了格式化功能的询问，现在默认启用
        print("\n提示: 代码块自动格式化功能已默认启用。")

        if self.mode == 'all':
            prompt = "请输入统一的目标语言 (例如: java, python, c): "
            self.target_lang_all = input(prompt).strip().lower()
            print(f"好的，所有代码块将被转换为 `{self.target_lang_all}`。")
        else:  # 'individual' 模式
            prompt = ("请输入用于自动修正的默认语言 (例如: cpp, python)。\n"
                      "直接按 Enter 将默认为 'c': ")
            user_default = input(prompt).strip().lower()
            if user_default:
                self.default_lang = user_default
            print(f"好的，所有不规范的代码块将默认被修正为 `{self.default_lang}`。")

        # 步骤 1: 预处理，拆分错误合并的 ``` 代码块
        print("\n--- 正在预处理错误合并的代码块... ---\n")
        text = self._pre_process_fused_blocks(markdown_text)

        # 步骤 2: (新引擎) 手动解析并转换 '---' 块，避免歧义
        print("\n--- 正在预处理自定义 '---' 代码块... ---\n")
        lines = text.split('\n')
        output_parts = []
        buffer = []
        in_block_type = None  # Can be 'standard', 'dashed', or None
        dashed_delimiter_regex = re.compile(r"^\s*-{3,}[ \t]*$")

        for line in lines:
            is_standard_delimiter = (line.strip().startswith('```') and len(
                line.strip().replace('`', '')) < 15)
            is_dashed_delimiter = dashed_delimiter_regex.match(line)

            if in_block_type == 'standard':
                buffer.append(line)
                if is_standard_delimiter:
                    output_parts.append("\n".join(buffer))
                    buffer = []
                    in_block_type = None
            elif in_block_type == 'dashed':
                if is_dashed_delimiter:
                    full_content = "\n".join(buffer)
                    converted_block = self._process_dashed_content(
                        full_content)
                    output_parts.append(converted_block)
                    buffer = []
                    in_block_type = None
                else:
                    buffer.append(line)
            else:  # Not in any block
                if is_standard_delimiter:
                    in_block_type = 'standard'
                    buffer.append(line)
                elif is_dashed_delimiter:
                    in_block_type = 'dashed'
                else:
                    output_parts.append(line)

        if buffer:
            if in_block_type == 'standard':
                print("警告: 检测到文件末尾存在一个未闭合的 '```' 代码块。")
                output_parts.append("\n".join(buffer))
            elif in_block_type == 'dashed':
                print("警告: 检测到文件末尾存在一个未闭合的 '---' 代码块。")
                output_parts.append("-" * 40)
                output_parts.extend(buffer)

        preprocessed_text = "\n".join(output_parts)

        # 步骤 3: 处理所有标准的 '```' 代码块
        print("\n--- 开始处理标准的 '```' 代码块... ---\n")
        processed_text = self.block_finder_regex.sub(
            self._replacement_callback, preprocessed_text)

        # 步骤 4: 检查并修复未闭合的 '```' 代码块
        final_text = self._fix_unterminated_blocks(processed_text)

        return final_text


def process_file(input_filepath: str, output_filepath: str):
    """读取文件，使用处理器进行重构，然后写入新文件。"""
    try:
        print(f"正在读取文件: '{input_filepath}'...")
        with open(input_filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        processor = CodeBlockProcessor()
        corrected_content = processor.run(content)
        print(f"\n--- 处理完成 ---\n正在将结果写入: '{output_filepath}'...")
        with open(output_filepath, 'w', encoding='utf-8') as f:
            f.write(corrected_content)
        print("\n文件处理成功!")
        print(f"总共处理了 {processor.block_count} 个代码块。")
        print(f"输入文件: {input_filepath}")
        print(f"输出文件: {output_filepath}")
    except FileNotFoundError:
        print(f"\n错误: 输入文件未找到 '{input_filepath}'")
    except Exception as e:
        print(f"\n发生未知错误: {e}")


def main():
    """程序主入口，处理命令行参数。"""
    if len(sys.argv) != 3:
        print("--- Markdown 代码块重构工具 ---")
        print("本工具可以批量修正不规范的代码块格式，并支持交互式修改语言类型。")
        print("\n用法: python markdown_repair.py <输入文件路径> <输出文件路径>")
        sys.exit(1)
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    if input_file == output_file:
        print("\n警告: 输入和输出文件路径相同，这会覆盖您的原始文件。")
        confirm = input("您确定要继续吗? (y/n): ").lower()
        if confirm != 'y':
            print("操作已取消。")
            sys.exit(0)
    process_file(input_file, output_file)


if __name__ == "__main__":
    main()
