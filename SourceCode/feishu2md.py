# -*- coding: utf-8 -*-
"""
Markdown 处理工具 - 图形界面版本 (main_gui.py)

本脚本提供图形化界面，方便用户进行 Markdown 处理操作。

功能:
1. Word 转 Markdown (docx_to_markdown.py)
2. 清理 HTML 格式 (markdown_cleaner.py)
3. 修正代码块 (markdown_repair.py)
4. 修正标题 (markdown_setting.py)
5. 文件拆分 (markdown_split.py)

用法:
    python main_gui.py

依赖:
    pip install python-docx
"""

import os
import sys
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
import threading
import subprocess
import platform


def is_admin():
    """
    检查是否以管理员权限运行（仅Windows）。
    使用Windows API检查进程令牌的提升状态。
    """
    if platform.system() != "Windows":
        print("[调试] 非Windows系统，返回False")
        return False

    print("\n[调试] 开始管理员权限检测...")

    try:
        import ctypes
        from ctypes import wintypes

        # Windows API常量
        TOKEN_QUERY = 0x0008
        TokenElevation = 20

        # 定义TOKEN_ELEVATION结构
        class TOKEN_ELEVATION(ctypes.Structure):
            _fields_ = [("TokenIsElevated", wintypes.DWORD)]

        kernel32 = ctypes.windll.kernel32
        advapi32 = ctypes.windll.advapi32

        process = kernel32.GetCurrentProcess()
        token = wintypes.HANDLE()

        print(f"[调试] 进程句柄: {process}")

        # 打开进程令牌
        result = advapi32.OpenProcessToken(
            process,
            TOKEN_QUERY,
            ctypes.byref(token)
        )

        print(f"[调试] OpenProcessToken返回值: {result}")

        if not result:
            error = kernel32.GetLastError()
            print(f"[调试] OpenProcessToken失败，错误码: {error}")
            return False

        # 查询令牌提升信息
        elevation = TOKEN_ELEVATION()
        size = wintypes.DWORD()

        result = advapi32.GetTokenInformation(
            token,
            TokenElevation,
            ctypes.byref(elevation),
            ctypes.sizeof(elevation),
            ctypes.byref(size)
        )

        print(f"[调试] GetTokenInformation返回值: {result}")

        # 关闭令牌句柄
        kernel32.CloseHandle(token)

        if not result:
            error = kernel32.GetLastError()
            print(f"[调试] GetTokenInformation失败，错误码: {error}")
            return False

        # 检查提升状态
        is_elevated = bool(elevation.TokenIsElevated)
        print(f"[调试] TokenIsElevated值: {elevation.TokenIsElevated}")
        print(f"[调试] 最终结果: {'有' if is_elevated else '无'}管理员权限\n")

        return is_elevated

    except Exception as e:
        print(f"[调试] 权限检测异常: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


def install_python_packages(packages):
    """安装Python包。"""
    for package in packages:
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", package],
                check=True,
                capture_output=True
            )
        except Exception as e:
            print(f"安装{package}失败: {e}")
            return False
    return True


def install_pandoc_with_choco():
    """使用Chocolatey安装Pandoc（需要管理员权限）。"""
    try:
        result = subprocess.run(
            ["choco", "install", "pandoc", "-y"],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Chocolatey安装失败: {e}")
        return False


def install_pandoc_with_winget():
    """使用winget安装Pandoc（Windows 10/11自带，无需管理员权限）。"""
    try:
        # 检查winget是否可用
        check_result = subprocess.run(
            ["winget", "--version"],
            capture_output=True,
            text=True
        )

        if check_result.returncode != 0:
            print("winget不可用")
            return False

        print(f"winget版本: {check_result.stdout.strip()}")

        # 使用winget安装Pandoc
        result = subprocess.run(
            ["winget", "install", "--source", "winget", 
             "--exact", "--id", "JohnMacFarlane.Pandoc", 
             "--silent", "--accept-package-agreements", "--accept-source-agreements"],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        print(f"winget安装返回码: {result.returncode}")
        if result.stdout:
            print(f"winget输出: {result.stdout}")
        
        return result.returncode == 0
    except FileNotFoundError:
        print("winget命令不存在")
        return False
    except Exception as e:
        print(f"winget安装失败: {e}")
        return False


def check_dependencies():
    """检测依赖，如果缺失则提示用户。"""
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
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口

        # 调试信息：显示权限检测结果
        admin_status = is_admin()
        choco_installed = shutil.which("choco") is not None
        winget_installed = shutil.which("winget") is not None
        print(f"\n{'='*50}")
        print(f"[调试信息]")
        print(f"{'='*50}")
        print(f"管理员权限: {admin_status}")
        print(f"Chocolatey已安装: {choco_installed}")
        print(f"winget已安装: {winget_installed}")
        print(f"Pandoc缺失: {pandoc_missing}")
        print(f"操作系统: {platform.system()}")
        print(f"{'='*50}\n")

        # 如果是Windows系统，Pandoc缺失，且以管理员权限运行，且安装了Chocolatey
        if (pandoc_missing and 
            platform.system() == "Windows" and 
            admin_status and 
            choco_installed):
            
            msg = "检测到Pandoc未安装。\n\n"
            msg += "✅ 检测到您正在以管理员权限运行\n"
            msg += "✅ 已安装Chocolatey包管理器\n\n"
            msg += "是否立即使用Chocolatey安装Pandoc？\n"
            msg += "(这将自动执行: choco install pandoc -y)\n\n"
            msg += f"调试信息：\n"
            msg += f"- 管理员权限: {admin_status}\n"
            msg += f"- Chocolatey: {choco_installed}"
            
            response = messagebox.askyesno("自动安装Pandoc", msg)
            
            if response:
                # 显示进度对话框
                progress_dialog = tk.Toplevel(root)
                progress_dialog.title("正在安装Pandoc")
                progress_dialog.geometry("400x150")
                progress_dialog.transient(root)
                progress_dialog.grab_set()
                
                tk.Label(progress_dialog, 
                        text="正在使用Chocolatey安装Pandoc...\n请稍候...",
                        font=('Arial', 11)).pack(pady=30)
                
                progress_bar = ttk.Progressbar(
                    progress_dialog, 
                    mode='indeterminate',
                    length=300
                )
                progress_bar.pack(pady=10)
                progress_bar.start()
                
                root.update()
                
                # 在后台线程中安装
                success = install_pandoc_with_choco()
                
                progress_bar.stop()
                progress_dialog.destroy()
                
                if success:
                    # 验证安装
                    if shutil.which("pandoc"):
                        pandoc_missing = False  # 安装成功
                        messagebox.showinfo(
                            "安装成功",
                            "Pandoc 安装成功！\n现在可以继续使用工具。"
                        )
                    else:
                        messagebox.showwarning(
                            "需要重启",
                            "Pandoc 安装完成，但需要重启程序才能生效。\n"
                            "请关闭并重新运行此程序。"
                        )
                        sys.exit(0)
                else:
                    messagebox.showerror(
                        "安装失败",
                        "Chocolatey 安装Pandoc失败。\n\n"
                        "可能的原因：\n"
                        "1. 网络连接问题\n"
                        "2. Chocolatey配置问题\n\n"
                        "请手动在PowerShell中运行：\n"
                        "choco install pandoc -y"
                    )
                    sys.exit(1)
        
        # 如果还有缺失的依赖（Python包或Pandoc未通过choco安装）
        if missing_deps or pandoc_missing:
            msg = "检测到缺失的依赖项：\n\n"
            
            if missing_deps:
                msg += f"Python 包: {', '.join(missing_deps)}\n"
            
            if pandoc_missing:
                msg += "Pandoc（必需的外部程序）\n"
                
                # 如果是Windows但没有以管理员权限运行或没有安装Chocolatey
                if platform.system() == "Windows":
                    msg += f"\n[检测状态]\n"
                    msg += f"- 管理员权限: {'✅ 是' if admin_status else '❌ 否'}\n"
                    msg += f"- Chocolatey: {'✅ 已安装' if choco_installed else '❌ 未安装'}\n"
                    
                    if not admin_status:
                        msg += "\n💡 提示：右键以管理员身份运行此程序\n"
                        msg += "可自动安装Pandoc（需要Chocolatey）\n"
                    elif not choco_installed:
                        msg += "\n💡 提示：安装Chocolatey后可自动安装Pandoc\n"
                        msg += "访问: https://chocolatey.org/install\n"
            
            msg += "\n是否现在自动安装缺失的依赖？"
            
            response = messagebox.askyesno("缺失依赖", msg)
            
            if response:
                # 显示安装进度
                progress_dialog = tk.Toplevel(root)
                progress_dialog.title("正在安装依赖")
                progress_dialog.geometry("450x200")
                progress_dialog.transient(root)
                progress_dialog.grab_set()
                
                status_label = tk.Label(
                    progress_dialog, 
                    text="正在安装依赖项...\n请稍候...",
                    font=('Arial', 11),
                    pady=20
                )
                status_label.pack()
                
                progress_bar = ttk.Progressbar(
                    progress_dialog, 
                    mode='indeterminate',
                    length=350
                )
                progress_bar.pack(pady=10)
                progress_bar.start()
                
                root.update()
                
                install_success = True
                error_msg = ""
                
                # 安装Python包
                if missing_deps:
                    status_label.config(text=f"正在安装Python包: {', '.join(missing_deps)}...")
                    root.update()
                    
                    if not install_python_packages(missing_deps):
                        install_success = False
                        error_msg += "Python包安装失败\n"
                
                # 安装Pandoc（Windows平台）
                if pandoc_missing and platform.system() == "Windows":
                    pandoc_installed = False
                    pandoc_install_method = None
                    
                    # 优先使用winget（Windows 10/11自带）
                    if winget_installed:
                        status_label.config(text="正在使用winget安装Pandoc...")
                        root.update()
                        
                        if install_pandoc_with_winget():
                            pandoc_installed = True
                            pandoc_install_method = "winget"
                            print("✓ winget安装完成")
                        else:
                            print("⚠️ winget安装失败，尝试Chocolatey...")
                    
                    # 如果winget不可用或失败，尝试Chocolatey
                    if not pandoc_installed and admin_status and choco_installed:
                        status_label.config(text="正在使用Chocolatey安装Pandoc...")
                        root.update()
                        
                        if install_pandoc_with_choco():
                            pandoc_installed = True
                            pandoc_install_method = "choco"
                            print("✓ Chocolatey安装完成")
                        else:
                            print("⚠️ Chocolatey安装也失败")
                    
                    # 如果成功安装，但需要重启才能生效
                    if pandoc_installed:
                        # 检查是否立即可用（已在PATH中）
                        if not shutil.which("pandoc"):
                            # 安装成功但未在PATH中，需要重启
                            install_success = True
                            error_msg += f"✓ Pandoc已通过{pandoc_install_method}安装\n"
                            error_msg += "⚠️ 需要重启程序以加载环境变量\n"
                    # 如果所有方法都失败
                    elif not pandoc_installed:
                        install_success = False
                        if not choco_installed and not winget_installed:
                            error_msg += "❌ 未安装Chocolatey或winget\n"
                            error_msg += "   建议：winget在Windows 10/11中内置\n"
                            error_msg += "   或手动安装Pandoc\n"
                        else:
                            error_msg += "❌ Pandoc自动安装失败\n"
                
                progress_bar.stop()
                progress_dialog.destroy()
                
                if install_success:
                    # 验证安装
                    all_installed = True
                    
                    # 重新检查Python包
                    for package_name in missing_deps:
                        import_name = 'docx' if package_name == 'python-docx' else package_name
                        try:
                            __import__(import_name)
                        except ImportError:
                            all_installed = False
                    
                    # 重新检查Pandoc
                    if pandoc_missing and not shutil.which("pandoc"):
                        all_installed = False
                        error_msg += "Pandoc未正确安装到PATH中\n"
                    
                    if all_installed:
                        messagebox.showinfo(
                            "安装成功",
                            "所有依赖安装完成！\n请重新运行此程序。"
                        )
                        sys.exit(0)
                    else:
                        messagebox.showwarning(
                            "需要重启",
                            "依赖已安装，但可能需要重启程序才能生效。\n"
                            "请关闭并重新运行此程序。"
                        )
                        sys.exit(0)
                else:
                    messagebox.showerror(
                        "安装失败",
                        f"部分依赖安装失败：\n\n{error_msg}\n"
                        f"请手动安装：\n"
                        f"- Python包: pip install {' '.join(missing_deps)}\n" if missing_deps else "" +
                        f"- Pandoc: choco install pandoc (需要管理员权限)"
                    )
                    sys.exit(1)
            else:
                messagebox.showwarning(
                    "提示",
                    "请先安装依赖，然后重新运行此程序。"
                )
                sys.exit(1)


# 首先检查依赖
check_dependencies()

# 导入各个处理模块
from docx_to_markdown import PandocConverter
from markdown_cleaner import MarkdownCleaner
from markdown_setting import GuiBoldHeaderCorrector
from markdown_split import MarkdownSplitter


class MarkdownProcessorGUI:
    """Markdown 处理器图形界面主类。"""

    def __init__(self, root):
        """初始化GUI。"""
        self.root = root
        self.root.title("Markdown 处理工具")
        self.root.geometry("1200x850")
        
        self.colors = {
            'bg': '#1a1a1a',  # 深黑色背景
            'fg': '#ffffff',  # 白色文字
            'button': '#ff69b4',  # 粉色按钮
            'button_hover': '#ff1493',  # 深粉色（悬停）
            'progress': '#00ff00',  # 绿色进度条
            'frame_bg': '#2a2a2a',  # 框架背景
            'entry_bg': '#3a3a3a',  # 输入框背景
            'text_bg': '#2a2a2a',  # 文本框背景
            'highlight': '#4a4a4a'  # 高亮色
        }
        
        # 配置样式
        self.setup_styles()
        
        self.root.configure(bg=self.colors['bg'])
        
        try:
            # self.root.iconbitmap('icon.ico')
            pass
        except Exception:
            pass
        
        # 变量
        self.input_file = tk.StringVar()
        self.output_dir = tk.StringVar(value='output')
        self.processing = False
        
        # 步骤选择变量
        self.step1_var = tk.BooleanVar(value=True)
        self.step2_var = tk.BooleanVar(value=True)
        self.step3_var = tk.BooleanVar(value=True)
        self.step4_var = tk.BooleanVar(value=True)
        self.step5_var = tk.BooleanVar(value=True)
        
        self.setup_ui()
    
    def setup_styles(self):
        """设置ttk样式。"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # 配置Frame
        style.configure('Dark.TFrame', background=self.colors['bg'])
        
        # 配置LabelFrame
        style.configure('Dark.TLabelframe', 
                       background=self.colors['frame_bg'],
                       bordercolor=self.colors['button'],
                       relief='flat')
        style.configure('Dark.TLabelframe.Label',
                       background=self.colors['frame_bg'],
                       foreground=self.colors['button'],
                       font=('Arial', 10, 'bold'))
        
        # 配置Label
        style.configure('Dark.TLabel',
                       background=self.colors['bg'],
                       foreground=self.colors['fg'],
                       font=('Arial', 10))
        style.configure('Title.TLabel',
                       background=self.colors['bg'],
                       foreground=self.colors['button'],
                       font=('Arial', 18, 'bold'))
        
        # 配置Button
        style.configure('Dark.TButton',
                       background=self.colors['button'],
                       foreground='white',
                       borderwidth=0,
                       relief='flat',
                       font=('Arial', 10, 'bold'),
                       padding=10)
        style.map('Dark.TButton',
                 background=[('active', self.colors['button_hover'])],
                 relief=[('pressed', 'flat')])
        
        # 配置Checkbutton
        style.configure('Dark.TCheckbutton',
                       background=self.colors['frame_bg'],
                       foreground=self.colors['fg'],
                       font=('Arial', 10))
        
        # 配置Entry
        style.configure('Dark.TEntry',
                       fieldbackground=self.colors['entry_bg'],
                       foreground=self.colors['fg'],
                       borderwidth=2,
                       relief='flat')
        
        # 配置Progressbar
        style.configure('Green.Horizontal.TProgressbar',
                       background=self.colors['progress'],
                       troughcolor=self.colors['frame_bg'],
                       borderwidth=0,
                       thickness=25)
        
    def setup_ui(self):
        """设置用户界面。"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="20", style='Dark.TFrame')
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # 标题
        title_label = ttk.Label(
            main_frame,
            text="✨ Markdown 处理工具 ✨", 
            style='Title.TLabel'
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=20)
        
        # 输入文件选择
        ttk.Label(main_frame, text="输入文件:", 
                 style='Dark.TLabel').grid(
            row=1, column=0, sticky=tk.W, pady=8)
        ttk.Entry(main_frame, textvariable=self.input_file, 
                 width=50, style='Dark.TEntry').grid(
            row=1, column=1, sticky=(tk.W, tk.E), pady=8, padx=5)
        ttk.Button(main_frame, text="浏览...", 
                  command=self.browse_input,
                  style='Dark.TButton').grid(
            row=1, column=2, pady=8)
        
        # 输出目录选择
        ttk.Label(main_frame, text="输出目录:", 
                 style='Dark.TLabel').grid(
            row=2, column=0, sticky=tk.W, pady=8)
        ttk.Entry(main_frame, textvariable=self.output_dir, 
                 width=50, style='Dark.TEntry').grid(
            row=2, column=1, sticky=(tk.W, tk.E), pady=8, padx=5)
        ttk.Button(main_frame, text="浏览...", 
                  command=self.browse_output,
                  style='Dark.TButton').grid(
            row=2, column=2, pady=8)
        
        # 步骤选择框架
        steps_frame = ttk.LabelFrame(main_frame, text="📋 处理步骤", 
                                    padding="15",
                                    style='Dark.TLabelframe')
        steps_frame.grid(row=3, column=0, columnspan=3, 
                        sticky=(tk.W, tk.E), pady=15)
        
        ttk.Checkbutton(steps_frame, text="步骤 1: Word 转 Markdown",
                       variable=self.step1_var,
                       style='Dark.TCheckbutton').grid(
            row=0, column=0, sticky=tk.W, pady=5)
        ttk.Checkbutton(steps_frame, text="步骤 2: 清理 HTML 格式",
                       variable=self.step2_var,
                       style='Dark.TCheckbutton').grid(
            row=1, column=0, sticky=tk.W, pady=5)
        ttk.Checkbutton(steps_frame, text="步骤 3: 修正代码块 (需要交互)",
                       variable=self.step3_var,
                       style='Dark.TCheckbutton').grid(
            row=2, column=0, sticky=tk.W, pady=5)
        ttk.Checkbutton(steps_frame, text="步骤 4: 修正标题 (需要交互)",
                       variable=self.step4_var,
                       style='Dark.TCheckbutton').grid(
            row=3, column=0, sticky=tk.W, pady=5)
        ttk.Checkbutton(steps_frame, text="步骤 5: 文件拆分",
                       variable=self.step5_var,
                       style='Dark.TCheckbutton').grid(
            row=4, column=0, sticky=tk.W, pady=5)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame, style='Dark.TFrame')
        button_frame.grid(row=4, column=0, columnspan=3, pady=15)
        
        self.start_button = ttk.Button(button_frame, text="🚀 开始处理", 
                                      command=self.start_processing,
                                      style='Dark.TButton')
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="✓ 全选步骤", 
                  command=self.select_all_steps,
                  style='Dark.TButton').pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="✗ 清除步骤", 
                  command=self.deselect_all_steps,
                  style='Dark.TButton').pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="⏹ 退出", 
                  command=self.root.quit,
                  style='Dark.TButton').pack(side=tk.LEFT, padx=5)
        
        # 日志框架
        log_frame = ttk.LabelFrame(main_frame, text="📝 处理日志", 
                                  padding="15",
                                  style='Dark.TLabelframe')
        log_frame.grid(row=5, column=0, columnspan=3, 
                      sticky=(tk.W, tk.E, tk.N, tk.S), pady=15)
        main_frame.rowconfigure(5, weight=1)
        
        # 日志文本框
        self.log_text = scrolledtext.ScrolledText(
            log_frame, 
            height=18, 
            wrap=tk.WORD,
            state='disabled',
            bg=self.colors['text_bg'],
            fg=self.colors['fg'],
            insertbackground=self.colors['button'],
            font=('Consolas', 10)
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # 进度条
        self.progress = ttk.Progressbar(
            main_frame, 
            mode='indeterminate',
            style='Green.Horizontal.TProgressbar'
        )
        self.progress.grid(row=6, column=0, columnspan=3, 
                          sticky=(tk.W, tk.E), pady=10)
        
        # 状态栏
        self.status_label = ttk.Label(
            main_frame, 
            text="⚡ 就绪",
            style='Dark.TLabel',
            relief=tk.FLAT,
            background=self.colors['frame_bg'],
            padding=10
        )
        self.status_label.grid(row=7, column=0, columnspan=3, 
                              sticky=(tk.W, tk.E))
    
    def browse_input(self):
        """浏览输入文件。"""
        filename = filedialog.askopenfilename(
            title="选择 Word 文档",
            filetypes=[("Word 文档", "*.docx"), ("所有文件", "*.*")]
        )
        if filename:
            self.input_file.set(filename)
            # 自动设置输出目录为输入文件所在目录下的output文件夹
            input_dir = os.path.dirname(filename)
            default_output = os.path.join(input_dir, "output")
            self.output_dir.set(default_output)
    
    def browse_output(self):
        """浏览输出目录。"""
        dirname = filedialog.askdirectory(title="选择输出目录")
        if dirname:
            self.output_dir.set(dirname)
    
    def select_all_steps(self):
        """全选所有步骤。"""
        self.step1_var.set(True)
        self.step2_var.set(True)
        self.step3_var.set(True)
        self.step4_var.set(True)
        self.step5_var.set(True)
    
    def deselect_all_steps(self):
        """取消选择所有步骤。"""
        self.step1_var.set(False)
        self.step2_var.set(False)
        self.step3_var.set(False)
        self.step4_var.set(False)
        self.step5_var.set(False)
    
    def log(self, message):
        """在日志框中添加消息。"""
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, message + '\n')
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
        self.root.update()
    
    def set_status(self, message):
        """更新状态栏。"""
        self.status_label.config(text=message)
        self.root.update()
    
    def process_code_blocks_gui(self, content):
        """
        GUI版本的代码块处理。
        在对话框中选择代码块语言，而不是命令行。
        """
        import re
        
        # 查找所有代码块
        block_pattern = re.compile(r'```(.*?)\n(.*?)\n```', flags=re.DOTALL)
        blocks = list(block_pattern.finditer(content))
        
        if not blocks:
            return content  # 没有代码块，直接返回
        
        # 询问处理模式
        mode_dialog = tk.Toplevel(self.root)
        mode_dialog.title("代码块处理模式")
        mode_dialog.geometry("500x300")
        mode_dialog.transient(self.root)
        mode_dialog.grab_set()
        mode_dialog.configure(bg=self.colors['bg'])
        
        mode_result = {'mode': None, 'lang': None}
        
        ttk.Label(mode_dialog, text="请选择代码块处理模式：",
                 font=('Arial', 12, 'bold'),
                 style='Dark.TLabel').pack(pady=30)
        
        ttk.Button(mode_dialog, text="统一语言模式\n(所有代码块设为同一语言)",
                  command=lambda: self._set_mode(mode_result, mode_dialog, 'all'),
                  style='Dark.TButton').pack(pady=8)
        ttk.Button(mode_dialog, text="逐个选择模式\n(为每个代码块选择语言)",
                  command=lambda: self._set_mode(mode_result, mode_dialog, 'individual'),
                  style='Dark.TButton').pack(pady=8)
        ttk.Button(mode_dialog, text="自动模式\n(使用默认C语言)",
                  command=lambda: self._set_mode(mode_result, mode_dialog, 'auto'),
                  style='Dark.TButton').pack(pady=8)
        
        mode_dialog.wait_window()
        
        if not mode_result['mode']:
            return content  # 用户取消
        
        # 如果选择统一语言，询问语言类型
        if mode_result['mode'] == 'all':
            lang_dialog = tk.Toplevel(self.root)
            lang_dialog.title("选择代码语言")
            lang_dialog.geometry("400x200")
            lang_dialog.transient(self.root)
            lang_dialog.grab_set()
            lang_dialog.configure(bg=self.colors['bg'])
            
            ttk.Label(lang_dialog, text="请输入代码语言：",
                     style='Dark.TLabel').pack(pady=20)
            lang_entry = ttk.Entry(lang_dialog, width=30,
                                  style='Dark.TEntry')
            lang_entry.pack(pady=10)
            lang_entry.insert(0, "c")
            
            def confirm_lang():
                mode_result['lang'] = lang_entry.get().strip().lower()
                lang_dialog.destroy()
            
            ttk.Button(lang_dialog, text="确定", 
                      command=confirm_lang,
                      style='Dark.TButton').pack(pady=15)
            lang_dialog.wait_window()
            
            if not mode_result['lang']:
                mode_result['lang'] = 'c'
        
        # 处理代码块
        new_content = content
        offset = 0
        
        for idx, match in enumerate(blocks, 1):
            original_lang = match.group(1).strip()
            code = match.group(2)
            
            if mode_result['mode'] == 'auto':
                # 自动模式：使用C语言
                new_lang = 'c'
                if not original_lang or original_lang in ['__INVALID__', '__DEMO__']:
                    code = f"演示\n{code}" if not code.strip().startswith('演示') else code
            elif mode_result['mode'] == 'all':
                # 统一语言模式
                new_lang = mode_result['lang']
            else:
                # 逐个选择模式
                new_lang = self._ask_code_block_lang_gui(idx, len(blocks), original_lang, code)
                if new_lang is None:
                    continue  # 用户跳过
            
            # 替换代码块
            old_block = match.group(0)
            new_block = f"```{new_lang}\n{code.strip()}\n```"
            
            start = match.start() + offset
            end = match.end() + offset
            new_content = new_content[:start] + new_block + new_content[end:]
            offset += len(new_block) - len(old_block)
        
        return new_content
    
    def _set_mode(self, result, dialog, mode):
        """设置处理模式并关闭对话框。"""
        result['mode'] = mode
        dialog.destroy()
    
    def _ask_code_block_lang_gui(self, current, total, original_lang, code):
        """在GUI中询问代码块语言。"""
        dialog = tk.Toplevel(self.root)
        dialog.title(f"代码块语言选择 ({current}/{total})")
        dialog.configure(bg=self.colors['bg'])
        
        window_width = 900
        window_height = 600
        
        # 计算窗口位置（居中在父窗口）
        self.root.update_idletasks()
        parent_x = self.root.winfo_x()
        parent_y = self.root.winfo_y()
        parent_width = self.root.winfo_width()
        parent_height = self.root.winfo_height()
        
        x = parent_x + (parent_width - window_width) // 2
        y = parent_y + (parent_height - window_height) // 2
        
        dialog.geometry(f"{window_width}x{window_height}+{x}+{y}")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)
        
        result = {'lang': None}
        
        # 显示信息
        info_frame = ttk.Frame(dialog, padding="15", style='Dark.TFrame')
        info_frame.pack(fill=tk.X)
        
        ttk.Label(info_frame, text=f"📝 代码块 {current} / {total}",
                 font=('Arial', 13, 'bold'),
                 style='Dark.TLabel').pack()
        ttk.Label(info_frame, text=f"原语言: {original_lang or '(未指定)'}",
                 style='Dark.TLabel').pack(pady=5)
        
        # 代码预览
        preview_frame = ttk.LabelFrame(dialog, text="📄 代码预览", 
                                      padding="15",
                                      style='Dark.TLabelframe')
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        preview_text = scrolledtext.ScrolledText(
            preview_frame, height=18, width=100, wrap=tk.NONE,
            bg=self.colors['text_bg'],
            fg=self.colors['fg'],
            insertbackground=self.colors['button'],
            font=('Consolas', 9)
        )
        preview_text.pack(fill=tk.BOTH, expand=True)
        
        # 显示代码预览（前20行）
        preview_lines = code.split('\n')[:20]
        preview_text.insert('1.0', '\n'.join(preview_lines))
        if len(code.split('\n')) > 20:
            preview_text.insert(tk.END, '\n...')
        preview_text.config(state='disabled')
        
        # 语言选择框架
        lang_select_frame = ttk.LabelFrame(dialog, text="🔧 语言选择", 
                                          padding="15",
                                          style='Dark.TLabelframe')
        lang_select_frame.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        # 语言输入行
        input_row = ttk.Frame(lang_select_frame, style='Dark.TFrame')
        input_row.pack(fill=tk.X, pady=5)
        
        ttk.Label(input_row, text="选择语言:",
                 style='Dark.TLabel').pack(side=tk.LEFT, padx=5)
        lang_entry = ttk.Entry(input_row, width=20, style='Dark.TEntry')
        lang_entry.pack(side=tk.LEFT, padx=5)
        lang_entry.insert(0, original_lang or "c")
        lang_entry.focus()
        
        # 快捷选择按钮行
        button_row = ttk.Frame(lang_select_frame, style='Dark.TFrame')
        button_row.pack(fill=tk.X, pady=10)
        
        ttk.Label(button_row, text="快捷选择:",
                 style='Dark.TLabel').pack(side=tk.LEFT, padx=5)
        common_langs = ['c', 'cpp', 'python', 'java', 'javascript']
        for lang in common_langs:
            ttk.Button(
                button_row,
                text=lang.upper(),
                width=10,
                style='Dark.TButton',
                command=lambda l=lang: (lang_entry.delete(0, tk.END),
                                       lang_entry.insert(0, l))
            ).pack(side=tk.LEFT, padx=3)
        
        # 操作按钮
        button_frame = ttk.Frame(dialog, padding="15", style='Dark.TFrame')
        button_frame.pack(fill=tk.X)
        
        def confirm():
            result['lang'] = lang_entry.get().strip().lower() or original_lang
            dialog.destroy()
        
        def skip():
            result['lang'] = None
            dialog.destroy()
        
        ttk.Button(button_frame, text="✓ 确定",
                  command=confirm, width=12,
                  style='Dark.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="⊗ 跳过",
                  command=skip, width=12,
                  style='Dark.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="↺ 保留原样", 
                  command=lambda: (lang_entry.delete(0, tk.END), 
                                  lang_entry.insert(0, original_lang or ""),
                                  confirm()), width=12,
                  style='Dark.TButton').pack(side=tk.LEFT, padx=5)
        
        # 绑定回车键
        lang_entry.bind('<Return>', lambda e: confirm())
        
        dialog.wait_window()
        return result['lang']
    
    def start_processing(self):
        """开始处理。"""
        # 验证输入
        if not self.input_file.get():
            messagebox.showerror("错误", "请选择输入文件！")
            return
        
        if not os.path.exists(self.input_file.get()):
            messagebox.showerror("错误", "输入文件不存在！")
            return
        
        # 检查是否至少选择了一个步骤
        if not any([self.step1_var.get(), self.step2_var.get(), 
                   self.step3_var.get(), self.step4_var.get(), 
                   self.step5_var.get()]):
            messagebox.showerror("错误", "请至少选择一个处理步骤！")
            return
        
        # 禁用开始按钮
        self.start_button.config(state='disabled')
        self.processing = True
        
        # 清空日志
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state='disabled')
        
        # 开始进度条
        self.progress.start()
        
        # 在新线程中执行处理
        thread = threading.Thread(target=self.process_files)
        thread.daemon = True
        thread.start()
    
    def process_files(self):
        """执行文件处理（在单独线程中运行）。"""
        try:
            docx_path = self.input_file.get()
            output_dir = self.output_dir.get()
            base_name = Path(docx_path).stem
            
            os.makedirs(output_dir, exist_ok=True)
            
            # 定义文件路径
            step1_output = os.path.join(output_dir, f"{base_name}.md")
            step2_output = os.path.join(output_dir, 
                                       f"{base_name}_cleaned.md")
            step3_output = os.path.join(output_dir, 
                                       f"{base_name}_repaired.md")
            step4_output = os.path.join(output_dir, 
                                       f"{base_name}_repaired_corrected.md")
            step5_output_dir = os.path.join(output_dir, 
                                           f"{base_name}_split")
            
            self.log("=" * 60)
            self.log("开始处理...")
            self.log("=" * 60)
            
            # 步骤 1: Word 转 Markdown
            if self.step1_var.get():
                self.set_status("步骤 1/5: Word 转 Markdown...")
                self.log("\n[步骤 1] Word 转 Markdown")
                try:
                    converter = PandocConverter(docx_path, output_dir)
                    md_path = converter.convert()
                    self.log(f"✓ 成功: {md_path}")
                except Exception as e:
                    self.log(f"✗ 错误: {e}")
                    raise
            
            # 步骤 2: 清理 HTML
            if self.step2_var.get():
                self.set_status("步骤 2/5: 清理 HTML 格式...")
                self.log("\n[步骤 2] 清理 HTML 格式")
                try:
                    cleaner = MarkdownCleaner(step1_output, step2_output)
                    cleaner.clean()
                    self.log(f"✓ 成功: {step2_output}")
                except Exception as e:
                    self.log(f"✗ 错误: {e}")
                    raise
            
            # 步骤 3: 修正代码块（GUI交互）
            if self.step3_var.get():
                self.set_status("步骤 3/5: 修正代码块...")
                self.log("\n[步骤 3] 修正代码块")
                try:
                    with open(step2_output, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 使用GUI版本的代码块处理器
                    corrected_content = self.process_code_blocks_gui(content)
                    
                    with open(step3_output, 'w', encoding='utf-8') as f:
                        f.write(corrected_content)
                    self.log(f"✓ 成功: {step3_output}")
                except Exception as e:
                    self.log(f"✗ 错误: {e}")
                    raise
            
            # 步骤 4: 修正标题（GUI交互）
            if self.step4_var.get():
                self.set_status("步骤 4/5: 修正标题...")
                self.log("\n[步骤 4] 修正标题")
                try:
                    corrector = GuiBoldHeaderCorrector(
                        step3_output, step4_output, self)
                    corrector.correct()
                    self.log(f"✓ 成功: {step4_output}")
                except InterruptedError:
                    self.log("⊘ 用户取消了标题修正")
                except Exception as e:
                    self.log(f"✗ 错误: {e}")
                    raise

            # 步骤 5: 文件拆分
            if self.step5_var.get():
                self.set_status("步骤 5/5: 文件拆分...")
                self.log("\n[步骤 5] 文件拆分")
                try:
                    splitter = MarkdownSplitter(step4_output, 
                                               step5_output_dir)
                    splitter.split(split_by="##", show_progress=False)
                    self.log(f"✓ 成功: {step5_output_dir}")
                except Exception as e:
                    self.log(f"✗ 错误: {e}")
                    raise

            # 完成
            self.log("\n" + "=" * 60)
            self.log("✓ 所有步骤完成！")
            self.log("=" * 60)
            self.log(f"\n最终输出:")
            if self.step4_var.get():
                self.log(f"  - 完整文件: {step4_output}")
            if self.step5_var.get():
                self.log(f"  - 拆分文件: {step5_output_dir}")

            self.root.after(0, lambda: messagebox.showinfo(
                "完成", "处理完成！请查看输出目录。"))
            self.set_status("处理完成")

        except Exception as e:
            self.log(f"\n发生错误: {e}")
            self.root.after(0, lambda: messagebox.showerror(
                "错误", f"处理失败:\n{e}"))
            self.set_status("处理失败")

        finally:
            # 停止进度条并重新启用按钮
            self.progress.stop()
            self.start_button.config(state='normal')
            self.processing = False


def main():
    """主函数。"""
    root = tk.Tk()
    app = MarkdownProcessorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
