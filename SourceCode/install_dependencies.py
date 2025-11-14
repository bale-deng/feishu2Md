# -*- coding: utf-8 -*-
"""
依赖检测与安装工具 (install_dependencies.py)

本脚本用于检测并安装项目所需的所有依赖项，包括：
1. Python 依赖包 (tqdm, python-docx)
2. 外部程序 Pandoc

用法:
    python install_dependencies.py [选项]

选项:
    --check-only    仅检测依赖，不安装
    --auto          自动安装所有缺失的依赖（不询问）
"""

import os
import sys
import subprocess
import shutil
import platform
import argparse


class DependencyChecker:
    """依赖检测和安装工具类。"""

    def __init__(self, auto_install=False, check_only=False):
        """
        初始化依赖检查器。

        Args:
            auto_install: 是否自动安装缺失的依赖
            check_only: 是否仅检查不安装
        """
        self.auto_install = auto_install
        self.check_only = check_only
        self.missing_packages = []
        self.installed_packages = []
        self.pandoc_installed = False

    def print_header(self, text):
        """打印标题。"""
        print("\n" + "=" * 70)
        print(text)
        print("=" * 70)

    def print_section(self, text):
        """打印小节标题。"""
        print("\n" + "-" * 70)
        print(text)
        print("-" * 70)

    def check_python_package(self, package_name):
        """
        检查Python包是否已安装。

        Args:
            package_name: 包名称

        Returns:
            bool: 是否已安装
        """
        try:
            __import__(package_name.replace('-', '_'))
            return True
        except ImportError:
            return False

    def check_all_python_packages(self):
        """检查所有Python依赖包。"""
        self.print_section("检查 Python 依赖包")

        # 定义需要检查的包
        packages = {
            'tqdm': 'tqdm',
            'python-docx': 'docx'  # python-docx的导入名是docx
        }

        for package_name, import_name in packages.items():
            if self.check_python_package(import_name):
                print(f"✓ {package_name:15} - 已安装")
                self.installed_packages.append(package_name)
            else:
                print(f"✗ {package_name:15} - 未安装")
                self.missing_packages.append(package_name)

        if not self.missing_packages:
            print("\n✓ 所有 Python 依赖包都已安装！")
        else:
            print(f"\n⚠ 发现 {len(self.missing_packages)} 个缺失的包")

    def check_pandoc(self):
        """检查Pandoc是否已安装。"""
        self.print_section("检查外部程序 Pandoc")

        if shutil.which("pandoc") is not None:
            try:
                result = subprocess.run(["pandoc", "--version"],
                                        capture_output=True,
                                        text=True,
                                        encoding='utf-8')
                version_line = result.stdout.split('\n')[0]
                print(f"✓ Pandoc 已安装: {version_line}")
                self.pandoc_installed = True
            except Exception as e:
                print(f"✗ Pandoc 检测出错: {e}")
                self.pandoc_installed = False
        else:
            print("✗ Pandoc 未安装")
            self.pandoc_installed = False

    def install_python_packages(self):
        """安装缺失的Python包。"""
        if not self.missing_packages:
            return

        self.print_section("安装 Python 依赖包")

        if self.check_only:
            print("仅检查模式，跳过安装。")
            return

        if not self.auto_install:
            print(f"\n需要安装以下包: {', '.join(self.missing_packages)}")
            choice = input("是否现在安装? (y/n): ").lower().strip()
            if choice != 'y':
                print("已跳过 Python 包安装。")
                return

        print("\n开始安装 Python 包...")
        for package in self.missing_packages:
            print(f"\n正在安装 {package}...")
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", package],
                    check=True)
                print(f"✓ {package} 安装成功")
            except subprocess.CalledProcessError as e:
                print(f"✗ {package} 安装失败: {e}")
            except Exception as e:
                print(f"✗ 发生错误: {e}")

    def download_and_install_pandoc_windows(self):
        """在Windows上安装Pandoc（优先使用winget）。"""
        print("=" * 70)
        print("Windows 系统安装 Pandoc")
        print("=" * 70)

        # 优先尝试 winget（Windows 10/11 自带，无需管理员权限）
        if shutil.which("winget"):
            try:
                print("\n✓ 检测到 winget 包管理器")
                print("💡 winget 是 Windows 10/11 自带的包管理器，无需管理员权限")
                print("\n正在使用 winget 安装 Pandoc...")

                install_cmd = [
                    "winget", "install", "--id", "JohnMacFarlane.Pandoc", "-e",
                    "--silent", "--accept-package-agreements",
                    "--accept-source-agreements"
                ]
                result = subprocess.run(install_cmd,
                                        check=True,
                                        capture_output=True,
                                        text=True,
                                        encoding='utf-8')

                print("✓ Pandoc 通过 winget 安装完成！")
                return True

            except subprocess.CalledProcessError as e:
                print(f"\n⚠ winget 安装失败: {e}")
                print("正在尝试备用方案（Chocolatey）...")
            except Exception as e:
                print(f"\n⚠ winget 安装出错: {e}")
                print("正在尝试备用方案（Chocolatey）...")

        # 备用方案：使用 Chocolatey（需要管理员权限）
        if shutil.which("choco"):
            try:
                print("\n✓ 检测到 Chocolatey 包管理器")
                print("\n" + "⚠" * 35 + " 重要提示 " + "⚠" * 35)
                print("使用 Chocolatey 安装 Pandoc 需要管理员权限！")
                print("如果当前终端不是以管理员身份运行，安装将会失败。")
                print("=" * 70)

                print("\n正在使用 Chocolatey 安装 Pandoc...")

                install_cmd = ["choco", "install", "pandoc", "-y"]
                result = subprocess.run(install_cmd,
                                        check=True,
                                        capture_output=True,
                                        text=True,
                                        encoding='utf-8')

                print("✓ Pandoc 通过 Chocolatey 安装完成！")
                print("\n安装日志摘要：")
                output_lines = result.stdout.split('\n')
                for line in output_lines[-5:]:
                    if line.strip():
                        print(f"  {line}")

                return True

            except subprocess.CalledProcessError as e:
                print("\n" + "=" * 70)
                print("✗ Chocolatey 安装失败")
                print("=" * 70)
                print(f"错误信息: {e.stderr if e.stderr else e}")
                print("\n最常见的失败原因：需要以管理员身份运行！")
                print("\n" + "─" * 70)
                print("解决方案：")
                print("─" * 70)
                print("\n请以管理员身份运行：")
                print("  1. 关闭当前终端")
                print("  2. 右键点击 PowerShell 或 CMD")
                print("  3. 选择 '以管理员身份运行'")
                print("  4. 运行以下命令安装 Pandoc：")
                print("\n     choco install pandoc -y")
                print("\n安装完成后，即可正常使用本工具。")
                print("─" * 70)
                return False
            except Exception as e:
                print(f"✗ Chocolatey 安装出错: {e}")
                return False

        # 如果两个包管理器都不可用
        print("\n✗ 未检测到 winget 或 Chocolatey 包管理器")
        print("\n" + "─" * 70)
        print("📦 推荐的安装方式")
        print("─" * 70)

        print("\n方式1: 使用 winget（推荐，无需管理员权限）")
        print("  • winget 是 Windows 10/11 自带的包管理器")
        print("  • 如果不可用，请从 Microsoft Store 安装 '应用安装程序'")
        print("  • 安装命令: winget install --id JohnMacFarlane.Pandoc -e")

        print("\n方式2: 使用 Chocolatey（需要管理员权限）")
        print("  • 访问 https://chocolatey.org/install 安装 Chocolatey")
        print("  • 以管理员身份运行: choco install pandoc -y")

        print("\n方式3: 手动下载安装")
        print("  • 访问 https://pandoc.org/installing.html")
        print("  • 下载并安装 Pandoc for Windows")

        print("─" * 70)
        return False

    def download_and_install_pandoc_macos(self):
        """在macOS上下载并安装Pandoc。"""
        import urllib.request
        import tempfile

        print("正在下载 Pandoc for macOS...")

        # Pandoc macOS安装包下载链接（多个镜像源）
        pandoc_version = "3.1.11"
        download_urls = [
            # 清华大学镜像（推荐，国内速度快）
            f"https://mirrors.tuna.tsinghua.edu.cn/github-release/jgm/pandoc/v{pandoc_version}/pandoc-{pandoc_version}-x86_64-macOS.pkg",
            # 南京大学镜像
            f"https://mirror.nju.edu.cn/github-release/jgm/pandoc/v{pandoc_version}/pandoc-{pandoc_version}-x86_64-macOS.pkg",
            # Pandoc官方直链
            f"https://github.com/jgm/pandoc/releases/download/{pandoc_version}/pandoc-{pandoc_version}-x86_64-macOS.pkg",
        ]

        for idx, download_url in enumerate(download_urls, 1):
            try:
                with tempfile.TemporaryDirectory() as temp_dir:
                    installer_path = os.path.join(temp_dir,
                                                  "pandoc-installer.pkg")

                    # 下载安装包
                    if idx == 1:
                        print("使用清华大学镜像下载...")
                    elif idx == 2:
                        print(f"尝试备用镜像 {idx}...")
                    else:
                        print("尝试官方源...")

                    print(f"下载地址: {download_url}")
                    urllib.request.urlretrieve(download_url, installer_path)
                    print("✓ 下载完成")

                    print("正在安装 Pandoc（需要管理员权限）...")
                    install_cmd = [
                        "sudo", "installer", "-pkg", installer_path, "-target",
                        "/"
                    ]
                    subprocess.run(install_cmd, check=True)

                    print("✓ Pandoc 安装完成！")
                    return True

            except Exception as e:
                print(f"✗ 该镜像下载失败: {e}")
                if idx < len(download_urls):
                    print("正在尝试下一个下载源...")
                    continue
                else:
                    print("✗ 所有下载源均失败")
                    return False

        return False

    def install_pandoc(self):
        """安装Pandoc。"""
        if self.pandoc_installed:
            return

        self.print_section("安装 Pandoc")

        if self.check_only:
            print("仅检查模式，跳过安装。")
            return

        system = platform.system()
        print(f"检测到操作系统: {system}")

        if not self.auto_install:
            print("\nPandoc 是必需的外部程序。")
            choice = input("是否尝试自动下载并安装 Pandoc? (y/n): ").lower().strip()
            if choice != 'y':
                print("\n已跳过 Pandoc 安装。")
                print("请手动从以下网址下载安装:")
                print("https://pandoc.org/installing.html")
                return

        try:
            success = False

            if system == "Windows":
                # Windows优先使用winget，备用Chocolatey
                print("\n正在尝试安装 Pandoc（优先使用 winget）...")
                success = self.download_and_install_pandoc_windows()

            elif system == "Darwin":  # macOS
                # macOS推荐使用Homebrew，但也支持直接下载
                print("\n正在尝试安装 Pandoc...")
                success = self.download_and_install_pandoc_macos()

            elif system == "Linux":
                # Linux优先使用包管理器
                if shutil.which("apt-get"):
                    print("使用 apt-get 安装 Pandoc...")
                    subprocess.run(["sudo", "apt-get", "update"], check=True)
                    subprocess.run(
                        ["sudo", "apt-get", "install", "-y", "pandoc"],
                        check=True)
                    success = True
                elif shutil.which("dnf"):
                    print("使用 dnf 安装 Pandoc...")
                    subprocess.run(["sudo", "dnf", "install", "-y", "pandoc"],
                                   check=True)
                    success = True
                elif shutil.which("yum"):
                    print("使用 yum 安装 Pandoc...")
                    subprocess.run(["sudo", "yum", "install", "-y", "pandoc"],
                                   check=True)
                    success = True
                else:
                    print("✗ Linux 系统需要使用包管理器安装。")
                    print("请使用您的包管理器手动安装: sudo apt install pandoc")
                    return
            else:
                print(f"✗ 不支持的操作系统: {system}")
                print("请从 https://pandoc.org/installing.html 手动安装。")
                return

            if success:
                print("\n" + "=" * 70)
                print("✓ Pandoc 安装完成！")
                print("=" * 70)

                # 验证安装
                print("\n正在验证安装...")
                if shutil.which("pandoc"):
                    result = subprocess.run(["pandoc", "--version"],
                                            capture_output=True,
                                            text=True,
                                            encoding='utf-8')
                    version_info = result.stdout.split(chr(10))[0]
                    print(f"✓ 验证成功: {version_info}")
                    print("\n您现在可以使用 Markdown 处理工具了！")
                else:
                    print("⚠ 安装完成，但 Pandoc 仍未在 PATH 中找到。")
                    print("\n可能的解决方案：")
                    print("  1. 重启终端窗口")
                    print("  2. 重新打开 VSCode")
                    print("  3. 注销并重新登录")
                    print("  4. Windows 用户：重启计算机（确保环境变量生效）")
            else:
                print("\n" + "=" * 70)
                print("✗ Pandoc 自动安装未成功")
                print("=" * 70)
                if system == "Windows":
                    print("\n推荐的安装步骤：")
                    print("\n方式1 (推荐): 使用 winget（无需管理员权限）")
                    print(
                        "  • 命令: winget install --id JohnMacFarlane.Pandoc -e")
                    print("\n方式2: 使用 Chocolatey（需要管理员权限）")
                    print(
                        "  1. 安装 Chocolatey (https://chocolatey.org/install)")
                    print("  2. 以管理员身份打开 PowerShell/CMD")
                    print("  3. 运行: choco install pandoc -y")
                    print("\n安装完成后，即可正常使用本工具。")
                else:
                    print("\n请访问以下网址手动安装：")
                    print("  https://pandoc.org/installing.html")

        except subprocess.CalledProcessError as e:
            print(f"\n✗ Pandoc 安装失败: {e}")
        except Exception as e:
            print(f"\n✗ 发生错误: {e}")

    def print_summary(self):
        """打印检测摘要。"""
        self.print_header("依赖检测摘要")

        print("\nPython 依赖包:")
        print(f"  已安装: {len(self.installed_packages)}")
        print(f"  缺失:   {len(self.missing_packages)}")

        if self.missing_packages:
            print(f"  缺失的包: {', '.join(self.missing_packages)}")

        print(f"\nPandoc: {'✓ 已安装' if self.pandoc_installed else '✗ 未安装'}")

        all_ready = (not self.missing_packages) and self.pandoc_installed

        print("\n" + "=" * 70)
        if all_ready:
            print("✓ 所有依赖都已准备就绪！可以开始使用工具了。")
        else:
            print("⚠ 还有依赖项未安装。")
            if self.check_only:
                print("请运行以下命令安装:")
                print("  python install_dependencies.py")
            else:
                print("请根据上述提示完成安装。")
        print("=" * 70 + "\n")

    def run(self):
        """运行依赖检测和安装流程。"""
        self.print_header("Markdown 处理工具 - 依赖检测与安装")

        # 检查Python包
        self.check_all_python_packages()

        # 检查Pandoc
        self.check_pandoc()

        # 安装缺失的依赖
        if not self.check_only:
            if self.missing_packages:
                self.install_python_packages()

            if not self.pandoc_installed:
                self.install_pandoc()

            # 重新检查
            print("\n重新检测依赖状态...")
            self.missing_packages = []
            self.installed_packages = []
            self.check_all_python_packages()
            self.check_pandoc()

        self.print_summary()


def main():
    """主函数。"""
    parser = argparse.ArgumentParser(description="检测并安装 Markdown 处理工具所需的依赖项")
    parser.add_argument('--check-only', action='store_true', help='仅检测依赖，不安装')
    parser.add_argument('--auto', action='store_true', help='自动安装所有缺失的依赖（不询问）')

    args = parser.parse_args()

    try:
        checker = DependencyChecker(auto_install=args.auto,
                                    check_only=args.check_only)
        checker.run()
    except KeyboardInterrupt:
        print("\n\n用户中断操作。")
        sys.exit(1)
    except Exception as e:
        print(f"\n发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
