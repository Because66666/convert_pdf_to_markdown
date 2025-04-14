# PDF转Markdown工具

这个Python工具可以将PDF文件或图片文件转换为Markdown格式，使用智谱AI的视觉模型来识别文件中的内容。支持批量处理多个文件，并通过并发处理提高转换效率。

## 功能特点

- 支持PDF文件逐页转换为Markdown格式
- 支持多种图片格式（JPG、PNG、BMP等）转换为Markdown
- 支持批量处理多个文件
- 使用智谱AI的GLM-4V视觉模型进行内容识别
- 所有页面内容合并到同一个Markdown文件中
- 每页内容独立处理，无历史记录关联
- 通过并发处理提高转换效率

## 安装

1. 克隆或下载此仓库
2. 安装依赖包：

```bash
pip install -r requirements.txt
```

## 使用方法

### gradio前端使用（推荐）

```bash
python app.py
```

### 命令行使用

```bash
python pdf_to_markdown.py 文件路径 [选项]
```

### 选项

- `-o, --output`: 指定输出的Markdown文件路径（可选，默认使用输入文件名）
- `-d, --output-dir`: 指定输出目录（可选，批量处理时使用）
- `-k, --api-key`: 指定智谱AI API密钥（可选，也可通过环境变量设置）
- `-w, --max-workers`: 指定最大并发线程数（可选，也可通过环境变量设置）
- 可以指定多个文件路径进行批量处理

### 环境变量

你可以通过设置以下环境变量来配置程序：

- `OPENAI_API_KEY`: 智谱AI API密钥，用于调用视觉模型
- `MAX_WORKERS`: 最大并发线程数，控制文件处理的并行度（默认为5）

这些环境变量可以直接在系统中设置，也可以通过项目根目录下的`.env`文件配置。

### 示例

```bash
# 基本用法 - 处理PDF文件
python pdf_to_markdown.py document.pdf

# 处理图片文件
python pdf_to_markdown.py image.jpg

# 指定输出文件
python pdf_to_markdown.py document.pdf -o output.md

# 批量处理多个文件
python pdf_to_markdown.py document1.pdf document2.pdf image1.jpg

# 批量处理并指定输出目录
python pdf_to_markdown.py document1.pdf document2.pdf -d output_folder

# 指定API密钥
python pdf_to_markdown.py document.pdf -k your_api_key_here

# 指定最大并发线程数
python pdf_to_markdown.py document.pdf -w 10
```

## 项目结构

- `pdf_to_markdown.py`: 主程序，处理命令行参数、文件处理和转换逻辑
- `vision_api.py`: 包含调用智谱AI视觉模型的函数和图像处理逻辑，如果需要更换厂商，可以改写这部分代码。
- `app.py`: Gradio前端界面程序
- `requirements.txt`: 项目依赖列表
- `.env`: 环境变量配置文件，用于设置API密钥和并发线程数
- `start_app.bat`: Windows批处理文件，用于快速启动Gradio前端

## 注意事项

- 需要有效的智谱AI API密钥
- 处理大型PDF文件或高分辨率图片可能需要较长时间
- 视觉模型的识别质量取决于文件页面的清晰度和复杂性
- 支持的图片格式包括：JPG、JPEG、PNG、BMP、GIF、TIFF等