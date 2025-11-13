# Markdown 处理工具集 V1.0.01

> 一个功能强大的 Markdown 文件处理工具集，专为 Word 到 Markdown 的完整转换流程设计

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](https://github.com)

## ✨ 主要特性

- 🎨 **现代化深色主题 GUI 界面** - 基于 tkinter 的原生图形界面
- 📝 **智能表格处理** - 自动转换飞书文本表格为 Markdown 格式
- 🔧 **代码块智能识别** - 自动区分代码块和表格格式
- 🚀 **一键式处理流程** - CLI 命令行或 GUI 图形界面，双模式支持
- 🛡️ **格式保护机制** - 智能保护 Markdown 表格不被破坏
- 📦 **依赖自动安装** - 一键检测并安装所有依赖
- 💡 **轻量级设计** - 使用 Python 内置库

## 🔧 技术栈

### 核心技术

- **CLI (Command Line Interface)** - 命令行工具

  - 使用 Python 标准库实现
  - 支持批量处理和自动化
  - 跨平台兼容

- **GUI (Graphical User Interface)** - 图形界面
  - 基于 **tkinter** (Python 内置 GUI 库)
  - 原生外观，体积小巧
  - 完美跨平台支持

## 📋 处理流程

```mermaid
graph LR
    A[Word文档] --> B[步骤1: 转换为Markdown]
    B --> C[步骤2: 清理HTML + 转换表格]
    C --> D[步骤3: 修正代码块]
    D --> E[步骤4: 修正标题]
    E --> F[步骤5: 按标题拆分]
    F --> G[规范的Markdown文件]
```

### 五步处理详解

| 步骤 | 模块                  | 功能描述                               |
| ---- | --------------------- | -------------------------------------- |
| 1️⃣   | `docx_to_markdown.py` | 提取图片到 `media/media/` 并转换文档   |
| 2️⃣   | `markdown_cleaner.py` | 清理 HTML 标签，转换飞书表格，保护格式 |
| 3️⃣   | `markdown_repair.py`  | 交互式修正代码块语言和格式             |
| 4️⃣   | `markdown_setting.py` | 交互式修正加粗标题为标准标题           |
| 5️⃣   | `markdown_split.py`   | 按二级标题智能拆分为多个文件           |

## 🎯 快速开始

### 方法零：使用打包版本（最简单）⭐

**Windows 用户可直接使用打包的 exe 文件：**

1. 下载 `feishu2md.exe`
2. 双击运行，无需安装 Python
3. 选择文件，开始处理

**优势：**

- 🚀 开箱即用，无需配置环境
- 💼 独立运行，不依赖 Python
- 🎨 精美图标，专业外观
- 📦 单文件版本，便于分发

> **注意：** exe 版本仍需要安装 Pandoc 才能正常工作
>
> **推荐使用 Chocolatey 安装（需要管理员权限）：**
>
> ```bash
> # 以管理员身份打开 PowerShell 或 CMD，然后运行：
> choco install pandoc
> ```
>
> ⚠️ **重要提示**：使用 Chocolatey 安装需要以管理员身份运行终端！

---

### 方法一：图形界面（Python 版本）

```bash
# 启动图形界面
python feishu2md.py
```

**界面特色：**

- 🎨 深色主题，现代化设计（1200×850 分辨率）
- 🎯 可视化文件选择和步骤管理
- 📊 实时日志显示和进度条
- 🔄 灵活的步骤选择（可跳过任意步骤）
- 💡 适合所有用户，无需命令行经验

### 方法二：命令行（推荐高级用户）

```bash
# 一键完成所有步骤
python main.py document.docx

# 指定输出目录
python main.py document.docx output_folder

# 示例
python main.py "我的文档.docx" "D:\输出"
```

**命令行特点：**

- ⚡ 快速批量处理
- 🎛️ 交互式步骤选择
- 📈 实时进度显示
- 🔧 灵活的参数配置

## 📦 安装

### 自动安装（强烈推荐）

```bash
# 交互式安装所有依赖
python install_dependencies.py

# 静默安装模式
python install_dependencies.py --auto

# 仅检测依赖状态
python install_dependencies.py --check-only
```

自动安装工具会：

- ✅ 检测 Python 包（tqdm、python-docx）
- ✅ 检测 Pandoc 是否安装
- ✅ 自动安装缺失的依赖
- ✅ 跨平台支持（Windows/macOS/Linux）

### 手动安装

#### 1. Python 依赖

```bash
pip install -r requirements.txt
```

或单独安装：

```bash
pip install tqdm python-docx
```

#### 2. Pandoc 安装

**Windows（推荐使用 Chocolatey）:**

```bash
# 方式1: Chocolatey (强烈推荐) ⚠️ 需要管理员权限
# 右键点击 PowerShell/CMD，选择"以管理员身份运行"，然后执行：
choco install pandoc

# 方式2: Winget (无需管理员权限)
winget install --source winget --exact --id JohnMacFarlane.Pandoc
```

> 💡 **为什么推荐 Chocolatey？**
>
> - ✅ 自动配置环境变量
> - ✅ 一键安装，无需手动下载
> - ✅ 便于后续更新维护
> - ✅ 与其他开发工具集成良好
>
> ⚠️ **重要提示**：
>
> - Chocolatey 安装需要**管理员权限**
> - 请右键点击 PowerShell 或 CMD，选择"以管理员身份运行"
> - 如果不想使用管理员权限，可以选择 Winget 或手动下载安装

**macOS:**

```bash
brew install pandoc
```

**Linux:**

```bash
sudo apt-get update && sudo apt-get install -y pandoc
```

## 🆕 V1.0 新特性

### 🎨 深色主题 UI

- 统一的深色配色方案
- 粉色按钮 (#ff69b4) + 绿色进度条 (#00ff00)
- 高对比度文字显示
- 现代化图标装饰

### 📊 智能表格处理

**飞书文本表格自动转换：**

```
输入（飞书格式）：
---------- ----------
  列1       列2
  数据1     数据2
---------- ----------

输出（Markdown格式）：
| 列1 | 列2 |
| --- | --- |
| 数据1 | 数据2 |
```

**保护机制：**

- ✅ 识别并保护 Markdown 表格 (`|` 分隔符)
- ✅ 识别并保护飞书文本表格
- ✅ 智能处理反斜杠（仅在非表格行移除）

### 🔍 代码块与表格智能区分

**检测规则：**

- 纯连续短横线 (`-------`) → 代码块
- 空格分隔短横线 (`----- -----`) → 表格
- 检测编程语言名称（支持 30+种语言）

## 📖 详细使用指南

### 分步执行

#### 步骤 1: Word 转 Markdown

```bash
python docx_to_markdown.py input.docx output_folder
```

**输出：**

- `output_folder/input.md`
- `output_folder/media/media/` (图片文件夹)

#### 步骤 2: 清理 HTML 并转换表格

```bash
python markdown_cleaner.py input.md output_cleaned.md
```

**处理内容：**

- 移除 `<em>`, `<br>`, `<td>` 等 HTML 标签
- 转换飞书文本表格为 Markdown
- 修复图片链接路径
- 清理转义字符
- 保护 Markdown 表格格式

#### 步骤 3: 修正代码块

```bash
python markdown_repair.py input_cleaned.md output_repaired.md
```

**交互式选项：**

- **模式 A** - 所有代码块使用统一语言
- **模式 I** - 逐个设置代码块语言
- **自动格式化** - 缩进和符号间距

#### 步骤 4: 修正标题

```bash
python markdown_setting.py input_repaired.md
```

**功能：**

- 识别 `**加粗标题**` 格式
- 交互式选择标题级别 (H1-H6)
- 自动生成 `_corrected.md` 文件
- 显示已处理标题的树状结构

#### 步骤 5: 拆分文件

```bash
python markdown_split.py input_corrected.md output_split_folder
```

**输出：**

- 按二级标题 (`##`) 拆分
- 每个标题生成独立文件
- 前言保存为 `00_前言.md`

## 🎨 GUI 界面预览

### 主界面

- 文件选择器
- 步骤复选框
- 实时日志显示
- 进度条和状态栏

### 交互对话框

- **代码块语言选择** - 预览代码，选择语言
- **标题级别选择** - 查看标题树，设置级别
- **模式选择** - 统一/逐个/自动模式

## 📁 项目结构

```
markdown_improved/
├── 📄 README.md                    # 项目文档
├── 📄 requirements.txt             # Python依赖
├── 📄 .gitignore                   # Git忽略规则
│
├── 🔧 install_dependencies.py      # 依赖安装工具
├── ⭐ main.py                      # 命令行集成脚本
├── ⭐ feishu2md.py                 # 图形界面版本（飞书转Markdown）
│
├── 📝 docx_to_markdown.py          # 步骤1: Word转换
├── 📝 markdown_cleaner.py          # 步骤2: HTML清理+表格转换
├── 📝 markdown_repair.py           # 步骤3: 代码块修复
├── 📝 markdown_setting.py          # 步骤4: 标题修正
├── 📝 markdown_split.py            # 步骤5: 文件拆分
│
└── 📁 output/                      # 默认输出目录
```

## 🎯 完整示例

### 使用 GUI（最简单）

1. 运行 `python feishu2md.py`
2. 点击"浏览"选择 Word 文档
3. 选择需要执行的步骤
4. 点击"开始处理"
5. 查看实时日志和进度
6. 完成后查看输出目录

### 使用命令行

```bash
# 方法1: 一键完成（推荐）
python main.py document.docx output

# 方法2: 分步执行
python docx_to_markdown.py document.docx output
python markdown_cleaner.py output/document.md output/document_cleaned.md
python markdown_repair.py output/document_cleaned.md output/document_repaired.md
python markdown_setting.py output/document_repaired.md
python markdown_split.py output/document_repaired_corrected.md output/split
```

## 🔧 系统要求

- **Python:** 3.7 或更高版本
- **Pandoc:** 最新版本
- **操作系统:** Windows 10/11, macOS 10.14+, Linux (Ubuntu 18.04+)
- **内存:** 建议 2GB 以上
- **磁盘空间:** 取决于文档大小和图片数量

## 📦 依赖库

| 库            | 用途       | 必需        |
| ------------- | ---------- | ----------- |
| `tqdm`        | 进度条显示 | ✅ 是       |
| `python-docx` | GUI 支持   | ⚠️ GUI 需要 |
| `Pandoc`      | 文档转换   | ✅ 是       |

## 🛠️ 故障排除

### 常见问题

**Q: Pandoc 未找到**

```bash
# 方式1: 使用 Chocolatey (推荐，需要管理员权限)
# 右键点击 PowerShell/CMD，选择"以管理员身份运行"
choco install pandoc

# 方式2: 使用 Winget (无需管理员权限)
winget install --source winget --exact --id JohnMacFarlane.Pandoc

# 验证安装
pandoc --version
```

> 💡 **提示**：
>
> - 如果尚未安装 Chocolatey，访问 https://chocolatey.org/install
> - Chocolatey 需要管理员权限，请以管理员身份运行终端
> - 不想使用管理员权限？选择 Winget 或手动下载

**Q: tqdm 库缺失**

```bash
pip install tqdm
```

**Q: GUI 无法启动**

```bash
# 安装GUI依赖
pip install python-docx
```

**Q: 编码错误**

- 确保所有文件使用 UTF-8 编码
- 检查文件名是否包含特殊字符

**Q: 图片无法显示**

- 确保 `media/media/` 目录存在
- 检查图片路径是否正确

### 获取帮助

```bash
# 查看帮助信息
python main.py --help
python docx_to_markdown.py --help
python markdown_cleaner.py --help
```

## 💡 最佳实践

1. **使用绝对路径** - 避免路径相关问题
2. **定期备份** - 处理前备份原始文档
3. **按顺序执行** - 遵循 5 步流程获得最佳效果
4. **检查输出** - 每步完成后检查结果
5. **保留图片** - 不要删除 `media/media/` 文件夹
6. **使用 GUI** - 新手推荐使用图形界面

## 📝 注意事项

- ⚠️ 每个步骤生成新文件，不会覆盖原文件
- ⚠️ 步骤 3 和步骤 4 需要交互式输入
- ⚠️ 图片自动提取到 `media/media/` 目录
- ⚠️ 建议按顺序执行所有步骤
- ⚠️ 处理大文件时需要更多时间

## ⚠️ 已知限制

### 飞书格式支持限制

本工具在处理飞书文档时，对以下格式的支持存在限制：

**1. 项目符号列表（•格式）**

```
飞书格式：
• 第一项
• 第二项
• 第三项

处理结果：
可能会丢失项目符号，仅保留文本内容
```

**2. 编号项目列表（•1, •2 格式）**

```
飞书格式：
•1. 第一项
•2. 第二项
•3. 第三项

处理结果：
可能会丢失编号符号，仅保留文本内容
```

**建议解决方案：**

1. 在飞书中导出前，手动将列表格式转换为标准 Markdown 格式
2. 或在转换后手动补充列表格式：
   ```markdown
   - 第一项
   - 第二项
   - 第三项
   ```
3. 使用有序列表：
   ```markdown
   1. 第一项
   2. 第二项
   3. 第三项
   ```

**技术说明：**

- 这是 Pandoc 转换器的已知限制
- Markdown 本身支持列表格式
- 问题出现在 Word→Markdown 转换阶段
- 后续版本可能会改进此功能

> **提示：** 如果您的文档包含大量列表，建议在转换后手动检查和修复列表格式。

## 🚀 高级用法

### 批量处理

```bash
# 批量处理多个文档
for file in *.docx; do
    python main.py "$file" "output_${file%.docx}"
done
```

### 自定义配置

修改各模块的参数以适应特殊需求：

- 调整表格检测规则
- 修改代码块格式化选项
- 自定义分隔标题级别

## 📊 性能指标

- 10MB Word 文档 → 约 30 秒（包含 50 张图片）
- 代码块格式化 → 实时处理
- 表格转换 → 毫秒级
- GUI 响应 → 流畅无卡顿

## 🔄 版本历史

### V1.0.03 (2025-11-13)

- 🐛 **修复 exe 环境依赖安装问题**
  - 修复 feishu2md.exe 在无源代码环境下无法安装依赖的问题
  - 将依赖安装逻辑完全集成到 feishu2md.py 中
  - 移除对外部 install_dependencies.py 的依赖
  - exe 版本现在可以完全独立运行，自动安装所有依赖
- 🔧 **优化依赖安装流程**
  - 统一的 GUI 安装进度显示
  - 更完善的错误提示和解决方案
  - 自动验证安装结果
- 📚 **架构说明**
  - install_dependencies.py：独立工具，适合有源代码的开发者
  - feishu2md.py 内置检测：自动化安装，适合 exe 用户
  - 双层保障机制，确保所有场景都能顺利安装

### V1.1.0.02 (2025-11-13) ---> 未发布

- 🔧 **优化 Pandoc 安装逻辑**
  - Windows 平台统一推荐使用 Chocolatey 安装
  - 添加管理员权限检测和自动安装功能
  - feishu2md.exe 支持启动时自动安装 Pandoc（需管理员权限是 choco）
  - feishu2md.exe 支持启动时自动安装 Pandoc（无需管理员权限是 winget）
  - 优化 install_dependencies.py 的错误提示和引导
- 📚 **文档更新**
  - 更新 Pandoc 安装说明，强调管理员权限要求
  - 简化安装流程说明，减少用户困惑
  - 添加多处管理员权限相关提示
  - 优先使用 WINGET 进行安装 Pandoc

### V1.0.01 (2025-11)

- ✨ 全新深色主题 GUI 界面
- ✨ 飞书表格自动转换功能
- ✨ 智能表格格式保护
- ✨ 代码块与表格智能区分
- ✨ 依赖自动安装工具
- 🐛 修复多个已知问题
- 📚 完善文档和注释

## 📧 技术支持

- **问题反馈:** 提交 GitHub Issue
- **功能建议:** 欢迎 Pull Request
- **使用咨询:** 查看文档或提交 Issue

## 🤝 贡献

欢迎贡献代码、报告问题或提出建议！

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

---

<p align="center">
  <b>⭐ 如果这个项目对您有帮助，请给个星标支持！</b>
</p>

<p align="center">
  Made with ❤️ by Markdown Processing Tools
</p>
