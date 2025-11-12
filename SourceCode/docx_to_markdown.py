# -*- coding: utf-8 -*-
"""
第一步功能模块：使用 Pandoc 将 Word (.docx) 文件高质量转换为 Markdown。

本模块既可以作为一个独立的命令行工具直接运行，也可以被其他 Python 脚本
作为模块导入来使用其核心的 `PandocConverter` 类。

新增功能: 如果检测到 Pandoc 未安装，会提示用户并尝试自动安装。

如何作为独立脚本使用:
    在终端中运行此文件，并提供 Word 文件和输出文件夹的路径。

    用法:
    python docx_to_markdown.py <输入文件.docx> <输出文件夹名称>

    示例:
    python docx_to_markdown.py my_report.docx my_markdown_output
"""

import os
import re
import sys
import shutil
import platform
import subprocess


class PandocConverter:
    """
    使用 Pandoc 将 .docx 文件转换为包含有序图片的 Markdown 的类。
    """

    def __init__(self, docx_path: str, output_dir: str):
        """
        初始化 PandocConverter。

        Args:
            docx_path: 输入的 Word (.docx) 文件路径。
            output_dir: 用于存放中间文件的临时输出目录。
        """
        if not os.path.isfile(docx_path):
            raise FileNotFoundError(f"错误: Word 文件未找到 -> {docx_path}")
        self.docx_path = docx_path
        self.output_dir = output_dir
        self.md_filename = os.path.splitext(os.path.basename(
            self.docx_path))[0] + '.md'
        self.md_output_path = os.path.join(self.output_dir, self.md_filename)

    def convert(self) -> str:
        """
        执行 Pandoc 转换，返回生成的 Markdown 文件路径。
        """
        # Pandoc 会将图片提取到 `media` 文件夹
        media_temp_dir = os.path.join(self.output_dir, 'media')

        # 构建 Pandoc 命令
        command = [
            'pandoc', self.docx_path, '-f', 'docx', '-t', 'markdown',
            '--extract-media', media_temp_dir, '-o', self.md_output_path
        ]

        # 运行 Pandoc
        try:
            print("正在运行 Pandoc 命令...")
            subprocess.run(command,
                           check=True,
                           capture_output=True,
                           text=True,
                           encoding='utf-8')
            print("Pandoc 转换成功。")
        except FileNotFoundError:
            raise RuntimeError("Pandoc 未安装或未在系统路径中。")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Pandoc 转换失败: {e.stderr}")

        # --- 创建 media/media 结构并更新链接 ---
        print("正在处理提取出的图片...")
        final_media_dir = os.path.join(media_temp_dir, 'media')
        if os.path.isdir(media_temp_dir):
            os.makedirs(final_media_dir, exist_ok=True)
            for item in os.listdir(media_temp_dir):
                item_path = os.path.join(media_temp_dir, item)
                if os.path.isfile(item_path):
                    shutil.move(item_path, final_media_dir)

        if os.path.isfile(self.md_output_path):
            with open(self.md_output_path, 'r+', encoding='utf-8') as f:
                content = f.read()
                # 将 ![](media/...) 替换为 ![](media/media/...)
                updated_content = re.sub(r'!\[(.*?)\]\(media/',
                                         r'![\1](media/media/', content)
                f.seek(0)
                f.truncate()
                f.write(updated_content)
        print("图片路径和链接已更新。")
        return self.md_output_path


def install_pandoc() -> bool:
    """
    根据检测到的操作系统，尝试自动安装 Pandoc。

    Returns:
        bool: 如果安装过程成功启动，则返回 True，否则返回 False。
    """
    system = platform.system()
    print(f"检测到操作系统: {system}")

    try:
        if system == "Windows":
            if not shutil.which("winget"):
                print("错误: Windows 系统需要 winget 包管理器来进行自动安装。")
                print("请从 https://pandoc.org/installing.html 手动下载并安装 Pandoc。")
                return False
            print("检测到 winget，将尝试使用 winget 安装 Pandoc...")
            command = [
                "winget", "install", "--id=JohnMacFarlane.Pandoc", "-e",
                "--accept-source-agreements", "--accept-package-agreements"
            ]
            subprocess.run(command, check=True)

        elif system == "Darwin":  # macOS
            if not shutil.which("brew"):
                print("错误: macOS 系统需要 Homebrew 包管理器来进行自动安装。")
                print("请先访问 https://brew.sh 安装 Homebrew，然后重新运行此脚本。")
                return False
            print("检测到 Homebrew，将尝试使用 brew 安装 Pandoc...")
            subprocess.run(["brew", "install", "pandoc"], check=True)

        elif system == "Linux":
            print("将尝试使用系统包管理器安装 Pandoc (可能需要管理员权限)...")
            if shutil.which("apt-get"):
                print("检测到 apt-get，正在更新包列表...")
                subprocess.run(["sudo", "apt-get", "update"], check=True)
                print("正在安装 pandoc...")
                subprocess.run(["sudo", "apt-get", "install", "-y", "pandoc"],
                               check=True)
            elif shutil.which("dnf"):
                print("检测到 dnf，正在安装 pandoc...")
                subprocess.run(["sudo", "dnf", "install", "-y", "pandoc"],
                               check=True)
            elif shutil.which("yum"):
                print("检测到 yum，正在安装 pandoc...")
                subprocess.run(["sudo", "yum", "install", "-y", "pandoc"],
                               check=True)
            else:
                print("错误: 未能找到 apt-get, dnf 或 yum。")
                print("请使用您的 Linux 发行版的包管理器手动安装 Pandoc。")
                return False
        else:
            print(f"不支持的操作系统: {system}。")
            print("请从 https://pandoc.org/installing.html 手动下载并安装 Pandoc。")
            return False

        print("Pandoc 安装命令已成功执行。")
        return True

    except subprocess.CalledProcessError as e:
        print(f"\nPandoc 安装过程中发生错误: {e}", file=sys.stderr)
        return False
    except FileNotFoundError:
        print("\n错误: 命令执行失败。请确保相关工具已正确安装并位于系统 PATH 中。", file=sys.stderr)
        return False
    except Exception as e:
        print(f"\n发生未知错误: {e}", file=sys.stderr)
        return False


def main() -> None:
    """
    脚本的主入口点，处理命令行参数。
    """
    if len(sys.argv) != 3:
        print("错误：参数不足！")
        usage = (
            f"用法: python {sys.argv[0]} <Word文件名.docx> <输出文件夹名称>\n"
            r"示例: python docx_to_markdown.py my_doc.docx my_markdown_output")
        print(usage)
        sys.exit(1)

    docx_file: str = sys.argv[1]
    output_directory: str = sys.argv[2]

    try:
        # 检查 pandoc 是否安装
        if shutil.which("pandoc") is None:
            print("警告: 核心依赖 'Pandoc' 未在系统中找到。")
            choice = input("是否尝试为您自动安装 Pandoc? (y/n): ").lower().strip()
            if choice == 'y':
                if not install_pandoc():
                    raise RuntimeError(
                        "自动安装 Pandoc 失败。请从 pandoc.org 手动下载并安装，然后重试。")

                # 再次验证安装
                if shutil.which("pandoc") is None:
                    raise RuntimeError(
                        "Pandoc 安装后仍然无法找到。请检查您的系统 PATH 环境变量或重启终端后重试。")

                print("\nPandoc 已成功安装！请继续操作。")
            else:
                raise RuntimeError("用户取消。请先从 pandoc.org 手动下载并安装 Pandoc，然后重试。")

        print(f"输入文件: {docx_file}")
        print(f"输出目录: {output_directory}")
        os.makedirs(output_directory, exist_ok=True)

        converter = PandocConverter(docx_file, output_directory)
        md_file_path = converter.convert()

        print("\n" + "=" * 50)
        print("转换全部完成！")
        print(f"最终 Markdown 文件路径: {os.path.abspath(md_file_path)}")
        print("=" * 50)

    except (FileNotFoundError, RuntimeError) as e:
        print(f"\n错误: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n发生未知错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
