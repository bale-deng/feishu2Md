# -*- coding: utf-8 -*-
"""
Markdown 清理与修复工具 (markdown_cleaner.py)

本模块提供了一个命令行工具和一个可导入的类，用于清理和修复由 Pandoc
转换后产生的 Markdown 文件。经过多次迭代，本版本在代码结构、性能和
可读性上进行了全面优化。

功能特性:
- (最终修复) 将所有注释清理逻辑移至代码块处理函数中，从根本上解决上下文错误问题。
- (新) 增加专门规则，用于清理 `*// ... *` 格式的单行注释。
- (原) 彻底重写了错误注释块的识别逻辑，完美处理 `*/* ... */*` 等多种复杂格式。
- (新) 自动格式化代码块，为操作符 (`=`, `+`, `>`) 和符号 (`,`, `;`) 添加规范空格，同时自动处理缩进。
- (新) 全局移除 Pandoc 错误添加的多余转义反斜杠 (`\`)。
- (新) 移除代码块内错误的 Markdown 加粗 (`**...**`) 格式。
- (新) 移除代码块内每行末尾由 Pandoc 错误添加的 `\` 符号。
- (新) 修复注释块内部被错误转义的星号 `\*`。
- (新) 采用更强大的正则表达式，修复并清理图片链接，确保生成跨平台兼容的相对路径。
- (新) 智能处理 `<td>` 标签，避免对已有代码块进行重复转换。
- (原) 移除 <em>, <br> 等不必要的 HTML 标签。
- (新) 采用更稳健的回调方式修复 `---` 构成的非标准代码块。
- (新) 清理代码块内部 `\[` 和 `\]` 形式的转义。

如何使用:

1. 作为独立的命令行脚本:
    在终端中运行此文件，并提供输入和输出文件的路径。
    用法: python markdown_cleaner.py <输入文件.md> <输出文件.md>

2. 作为可导入的模块:
    在您自己的 Python 脚本中导入 `MarkdownCleaner` 类来使用其核心功能。
"""

import argparse
import re
import sys
from typing import Match


class MarkdownCleaner:
    """
    一个用于清理和转换 Markdown 文件中特定 HTML 标签和 Pandoc 格式问题的类。
    本类通过一系列预编译的正则表达式和模块化的方法，实现高效、可靠的清理。
    """

    def __init__(self, input_file: str, output_file: str):
        """
        初始化 MarkdownCleaner。

        Args:
            input_file: 要处理的输入 Markdown 文件的路径。
            output_file: 保存处理后内容的输出文件路径。
        """
        self.input_file = input_file
        self.output_file = output_file

    # ==========================================================================
    # 预编译正则表达式以提升性能
    # ==========================================================================

    # 匹配由 '---' 分隔的非标准代码块
    _DASHED_BLOCK_PATTERN = re.compile(r'^\s*-{3,}\s*\n(.*?)\n^\s*-{3,}\s*$',
                                       flags=re.MULTILINE | re.DOTALL)

    # 匹配并修复带有 Pandoc 属性和绝对路径的图片链接
    _IMAGE_LINK_PATTERN = re.compile(
        r'(!\[.*?\]\().*?(media[\\/]media[\\/][^)]+)\)\s*\{.*?\}',
        flags=re.DOTALL)

    # 匹配 <td>...</td> 标签，用于后续智能转换
    _TD_TAG_PATTERN = re.compile(r'<td[^>]*>(.*?)</td>',
                                 flags=re.IGNORECASE | re.DOTALL)

    # 匹配标准代码块，用于内部内容的清理和格式化
    _CODE_BLOCK_PATTERN = re.compile(r'```(.*?)\n(.*?)\n```', flags=re.DOTALL)

    # (已重写) 匹配多种由于 Pandoc 错误转换产生的 C 语言注释格式
    _start = r'(?:\*\s*/\*|\*/\s*\*)'
    _end = r'(?:\*/\s*\*|\*\s*/\*)'
    _MALFORMED_COMMENT_PATTERN = re.compile(
        fr'^\s*({_start})\s*(.*?)\s*({_end})\s*$',
        flags=re.MULTILINE | re.DOTALL)

    # 新增：匹配被错误添加了星号的单行注释
    _SINGLE_LINE_COMMENT_EMPHASIS_PATTERN = re.compile(r'^\s*\*(//.*)\*\s*$',
                                                       flags=re.MULTILINE)

    # ==========================================================================
    # 私有静态辅助方法 (Callbacks & Helpers)
    # ==========================================================================

    @staticmethod
    def _clean_malformed_comment(match: Match) -> str:
        """回调：将多种格式错误的注释块修正为标准的 /* ... */ 格式。"""
        content = match.group(2).strip()
        return f'/* {content} */'

    @staticmethod
    def _format_line_spacing(line: str) -> str:
        """为代码行内的操作符和符号添加规范的空格，会忽略字符串字面量内容。"""
        parts = re.split(r'(".*?")', line)
        formatted_parts = []
        for i, part in enumerate(parts):
            if i % 2 == 1:
                formatted_parts.append(part)
                continue
            formatted_part = part
            formatted_part = formatted_part.replace('->', 'TEMP_ARROW')
            operators = [
                '==', '!=', '<=', '>=', '&&', '||', '+=', '-=', '*=', '/=',
                '%=', '&=', '|=', '^=', '<<=', '>>=', '=', '>', '<', '+', '-',
                '/', '%', '&', '|', '^', '?', ':'
            ]
            for op in operators:
                formatted_part = re.sub(r'\s*' + re.escape(op) + r'\s*',
                                        f' {op} ', formatted_part)
            formatted_part = re.sub(r'\s*,\s*', ', ', formatted_part)
            formatted_part = re.sub(r'\s*;\s*', '; ', formatted_part)
            formatted_part = formatted_part.replace('TEMP_ARROW', '->')
            formatted_part = re.sub(r'\b(if|for|while|switch)\s*\(', r'\1 (',
                                    formatted_part)
            formatted_parts.append(formatted_part)
        result = "".join(formatted_parts)
        return re.sub(r'\s{2,}', ' ', result).strip()

    @staticmethod
    def _format_code_indentation(code_text: str) -> str:
        """对代码块应用基于花括号的缩进，并格式化符号间距。"""
        indented_code = []
        indent_level = 0
        indent_size = 4
        for line in code_text.split('\n'):
            clean_line = line.strip()
            if not clean_line:
                indented_code.append("")
                continue
            formatted_line = MarkdownCleaner._format_line_spacing(clean_line)
            if clean_line.startswith('}') or clean_line.startswith(
                    'case ') or clean_line.startswith('default:'):
                indent_level = max(0, indent_level - 1)
            current_indent = ' ' * (indent_level * indent_size)
            indented_code.append(current_indent + formatted_line)
            if clean_line.endswith('{') or clean_line.endswith(':'):
                indent_level += 1
        return '\n'.join(indented_code)

    @staticmethod
    def _convert_dashed_block(match: Match) -> str:
        """回调：将 `---` 分隔的块转换为标准代码块。"""
        content = match.group(1).strip()
        lines = content.split('\n')
        lang = ''
        if lines:
            first_line = lines[0].strip()
            lang_match = re.fullmatch(r'([a-zA-Z0-9+#.-]+)', first_line)
            if lang_match:
                lang = lang_match.group(1).lower()
                content = '\n'.join(lines[1:])
            else:
                content = '\n'.join(lines)
        return f'```{lang}\n{content.strip()}\n```'

    @staticmethod
    def _clean_image_path(match: Match) -> str:
        """回调：清理图片链接，确保是正确的相对路径。"""
        alt_text_and_start = match.group(1)
        relative_path = match.group(2)
        web_path = relative_path.replace('\\', '/')
        return f'{alt_text_and_start}{web_path})'

    @staticmethod
    def _clean_code_block_content(match: Match) -> str:
        """回调：清理和格式化已识别的标准代码块内部。"""
        lang = (match.group(1) or '').lower()
        content = match.group(2)

        # 步骤 1: 移除由 Pandoc 添加的多余行尾反斜杠
        cleaned_content = re.sub(r'\\\s*$', '', content, flags=re.MULTILINE)

        # 步骤 2: (移入此函数) 优先修复所有格式错误的注释块
        cleaned_content = MarkdownCleaner._MALFORMED_COMMENT_PATTERN.sub(
            MarkdownCleaner._clean_malformed_comment, cleaned_content)

        # 步骤 3: (新增) 修复被错误强调的单行注释
        cleaned_content = (
            MarkdownCleaner._SINGLE_LINE_COMMENT_EMPHASIS_PATTERN.sub(
                r'\1', cleaned_content))

        # 步骤 4: 清理转义的方括号
        cleaned_content = cleaned_content.replace(r'\[',
                                                  '[').replace(r'\]', ']')

        # 步骤 5: 移除代码块内错误的 Markdown 加粗
        cleaned_content = re.sub(r'\*\*(.*?)\*\*',
                                 r'\1',
                                 cleaned_content,
                                 flags=re.DOTALL)

        # 步骤 6: (新逻辑) 保护注释，然后清理错误的斜体
        # 这是一个更稳健的方法，可以防止清理规则意外破坏 C 风格的注释

        # 匹配 C 风格的注释 (块注释和行注释)
        comment_pattern = re.compile(r'/\*.*?\*/|//.*', re.DOTALL)
        comments = []

        # 定义一个回调函数，用于将注释替换为占位符
        def comment_replacer(m):
            comments.append(m.group(0))
            return f"__COMMENT_PLACEHOLDER_{len(comments)-1}__"

        # 用占位符替换所有注释
        content_without_comments = comment_pattern.sub(comment_replacer,
                                                       cleaned_content)

        # 现在，在没有注释的文本上，可以安全地移除错误的斜体格式了
        # 只移除内容不含中文字符的星号对
        content_without_comments = re.sub(r'\*([^\u4e00-\u9fa5*]+)\*', r'\1',
                                          content_without_comments)

        # 将注释恢复到原文中
        cleaned_content_final = content_without_comments
        for i, comment in enumerate(comments):
            cleaned_content_final = cleaned_content_final.replace(
                f"__COMMENT_PLACEHOLDER_{i}__", comment)

        cleaned_content = cleaned_content_final

        # 步骤 7 (原步骤 6): 对特定语言应用自动缩进和间距格式化
        c_family_langs = [
            'c', 'cpp', 'c++', 'java', 'javascript', 'js', 'c#', 'cs'
        ]
        if lang in c_family_langs:
            formatted_content = MarkdownCleaner._format_code_indentation(
                cleaned_content)
            return f'```{lang}\n{formatted_content.strip()}\n```'

        return f'```{lang}\n{cleaned_content.strip()}\n```'

    @staticmethod
    def _handle_td_tag(match: Match) -> str:
        """回调：智能地处理 <td> 标签，避免重复转换。"""
        content = match.group(1).strip()
        if content.startswith('```'):
            return content
        return f'\n```\n{content}\n```\n'

    # ==========================================================================
    # 主清理逻辑
    # ==========================================================================

    @staticmethod
    def _is_table_line(line: str) -> bool:
        """检查一行是否是Markdown表格或文本表格的一部分"""
        stripped = line.strip()
        
        # 检测标准Markdown表格（使用 | 符号）
        if '|' in stripped:
            # 表格分隔行的特征：包含 | 和 - 以及可能的 :
            if re.match(r'^\s*\|[\s\-:|]+\|\s*$', stripped):
                return True
            # 普通表格行：包含 | 分隔的内容
            if stripped.startswith('|') or stripped.endswith('|'):
                return True
            # 行中有多个 | 符号
            if stripped.count('|') >= 2:
                return True
        
        # 检测飞书文本表格格式
        # 1. 表格边框行：主要由 - 字符组成，可能有空格分隔
        if re.match(r'^\s*[-\s]+[-]+[-\s]*$', stripped) and len(stripped) > 10:
            # 至少10个字符长，主要由 - 和空格组成
            dash_count = stripped.count('-')
            if dash_count >= 5:  # 至少5个短横线
                return True
        
        # 2. 表格数据行：前面有空格缩进，包含多个空格分隔的列
        # 这种行通常有多个连续空格用于列对齐
        if re.search(r'\s{3,}', line):  # 包含3个或更多连续空格
            # 进一步检查：不是代码块或其他特殊格式
            if not stripped.startswith('#') and not stripped.startswith('>'):
                return True
        
        return False

    @staticmethod
    def _is_code_block_marker(border_line: str, next_line: str = '') -> bool:
        """检测是否是代码块的边框标记"""
        stripped_border = border_line.strip()
        
        # 代码块边框：连续的短横线，没有空格分隔
        if re.match(r'^-{3,}$', stripped_border):
            # 进一步检查下一行是否是编程语言名称
            if next_line:
                next_stripped = next_line.strip().lower()
                # 常见编程语言列表
                code_langs = [
                    'c', 'cpp', 'c++', 'java', 'python', 'javascript', 'js',
                    'typescript', 'ts', 'go', 'rust', 'ruby', 'php', 'swift',
                    'kotlin', 'scala', 'perl', 'shell', 'bash', 'sh', 'sql',
                    'html', 'css', 'xml', 'json', 'yaml', 'markdown', 'md',
                    'text', 'txt', 'cs', 'c#', 'vb', 'matlab', 'r', 'lua'
                ]
                if next_stripped in code_langs:
                    return True
            return True  # 纯连续短横线也视为代码块
        return False

    @staticmethod
    def _convert_text_table_to_markdown(text: str) -> str:
        """将飞书文本表格转换为标准Markdown表格"""
        lines = text.split('\n')
        result_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            
            # 检测短横线边框
            if re.match(r'^[-\s]+[-]+[-\s]*$', stripped) and len(stripped) > 10:
                dash_count = stripped.count('-')
                if dash_count >= 5:
                    # 检查是否是代码块而非表格
                    next_line = lines[i + 1].strip() if i + 1 < len(lines) else ''
                    if MarkdownCleaner._is_code_block_marker(stripped, next_line):
                        # 这是代码块，不是表格，直接添加
                        result_lines.append(line)
                        i += 1
                        continue
                    
                    # 检查边框格式：表格边框通常有空格分隔
                    if ' ' not in stripped:
                        # 没有空格的连续短横线更可能是代码块
                        result_lines.append(line)
                        i += 1
                        continue
                    
                    # 确认是表格，收集表格内容
                    table_rows = []
                    i += 1  # 跳过开始边框
                    
                    # 收集表格行直到遇到结束边框
                    while i < len(lines):
                        current_line = lines[i]
                        current_stripped = current_line.strip()
                        
                        # 检查是否是结束边框
                        if re.match(r'^[-\s]+[-]+[-\s]*$', current_stripped):
                            break
                        
                        # 收集非空行
                        if current_stripped:
                            table_rows.append(current_stripped)
                        
                        i += 1
                    
                    # 转换表格行为Markdown格式
                    if table_rows:
                        markdown_rows = []
                        for row in table_rows:
                            # 使用多个空格分割列（至少3个连续空格）
                            columns = re.split(r'\s{3,}', row.strip())
                            # 过滤空列
                            columns = [col.strip() for col in columns if col.strip()]
                            if columns:
                                markdown_row = '| ' + ' | '.join(columns) + ' |'
                                markdown_rows.append(markdown_row)
                        
                        if markdown_rows:
                            # 添加转换后的表格
                            result_lines.extend(markdown_rows)
                            # 添加表格分隔行（根据列数）
                            if markdown_rows:
                                first_row_cols = markdown_rows[0].count('|') - 1
                                separator = '| ' + ' | '.join(['---'] * first_row_cols) + ' |'
                                # 在第一行后插入分隔符
                                result_lines.insert(len(result_lines) - len(markdown_rows) + 1, separator)
                    
                    i += 1  # 跳过结束边框
                    continue
            
            # 非表格行，直接添加
            result_lines.append(line)
            i += 1
        
        return '\n'.join(result_lines)

    @staticmethod
    def clean_string(md_text: str) -> str:
        """
        按优化顺序，执行所有清理和修复操作。

        Args:
            md_text: 原始的 Markdown 文本。

        Returns:
            清理和修复后的 Markdown 文本。
        """
        # 步骤 0.5: 转换飞书文本表格为Markdown表格
        text = MarkdownCleaner._convert_text_table_to_markdown(md_text)
        
        # 步骤 1: 结构性修复与转换
        text = MarkdownCleaner._DASHED_BLOCK_PATTERN.sub(
            MarkdownCleaner._convert_dashed_block, text)
        text = MarkdownCleaner._TD_TAG_PATTERN.sub(
            MarkdownCleaner._handle_td_tag, text)

        # 步骤 2: 关键内容修复 (图片和转义)
        text = MarkdownCleaner._IMAGE_LINK_PATTERN.sub(
            MarkdownCleaner._clean_image_path, text)
        text = re.sub(r'^\s*\\\*', r' *', text, flags=re.MULTILINE)

        # 步骤 2.5: 智能移除反斜杠 - 保护表格行
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            if MarkdownCleaner._is_table_line(line):
                # 保护表格行，不移除反斜杠
                cleaned_lines.append(line)
            else:
                # 非表格行，移除多余的转义反斜杠
                cleaned_lines.append(line.replace('\\', ''))
        text = '\n'.join(cleaned_lines)

        # 步骤 3: 代码块内部处理 (包含所有注释修复和格式化)
        text = MarkdownCleaner._CODE_BLOCK_PATTERN.sub(
            MarkdownCleaner._clean_code_block_content, text)

        # 步骤 4: 通用 HTML 和格式清理
        text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
        text = re.sub(r'</?(em|strong)>', '', text, flags=re.IGNORECASE)
        text = re.sub(r'&amp;', '&', text, flags=re.IGNORECASE)
        remaining_tags = r'</?(?:td|tr|tbody|table|colgroup|col)[^>]*>'
        text = re.sub(remaining_tags, '', text, flags=re.IGNORECASE)
        text = re.sub(r'\n{3,}', '\n\n', text)

        # 最终步骤：全局清理任何残留的非法星号格式
        # (已注释掉) 这个规则过于宽泛，可能会错误地修改合法的 Markdown 格式，
        # 例如将 `**中文**` 破坏。正确的做法是仅在代码块内部进行此类清理。
        # text = re.sub(r'\*([^\u4e00-\u9fa5*]+)\*', r'\1', text)

        return text.strip()

    def clean(self) -> None:
        """
        执行文件读取、清理和写入操作。
        """
        try:
            print(f"正在读取输入文件: {self.input_file}")
            with open(self.input_file, 'r', encoding='utf-8') as f_in:
                markdown_content = f_in.read()
            cleaned_result = self.clean_string(markdown_content)
            print(f"正在将处理后的内容写入输出文件: {self.output_file}")
            with open(self.output_file, 'w', encoding='utf-8') as f_out:
                f_out.write(cleaned_result)
            print("文件处理完成！")
        except FileNotFoundError:
            print(f"错误: 输入文件未找到 -> {self.input_file}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"处理文件时发生未知错误: {e}", file=sys.stderr)
            sys.exit(1)


def main() -> None:
    """
    主函数，用于解析命令行参数并执行文件清理操作。
    """
    parser = argparse.ArgumentParser(
        description="清理并修复 Markdown (.md) 文件中的特定 HTML 标签和格式问题。")
    parser.add_argument("input_file", help="要处理的输入 Markdown 文件路径。")
    parser.add_argument("output_file", help="保存处理后内容的输出文件路径。")
    args = parser.parse_args()
    cleaner = MarkdownCleaner(args.input_file, args.output_file)
    cleaner.clean()


if __name__ == "__main__":
    main()
