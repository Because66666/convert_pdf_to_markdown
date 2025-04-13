# PDF转Markdown工具

这个Python工具可以将PDF文件转换为Markdown格式，使用OpenAI的视觉模型来识别PDF中的内容。

## 功能特点

- 将PDF文件逐页转换为Markdown格式
- 使用OpenAI的GPT-4 Vision模型进行内容识别
- 所有页面内容合并到同一个Markdown文件中
- 每页内容独立处理，无历史记录关联

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
python pdf_to_markdown.py 你的PDF文件路径 [选项]
```

### 选项

- `-o, --output`: 指定输出的Markdown文件路径（可选，默认使用PDF文件名）
- `-k, --api-key`: 指定OpenAI API密钥（可选，也可通过环境变量设置）

### 环境变量

你可以通过设置以下环境变量来配置程序：

- `OPENAI_API_KEY`: OpenAI API密钥，用于调用视觉模型
- `MAX_WORKERS`: 最大并发线程数，控制PDF页面处理的并行度（默认为5）

这些环境变量可以直接在系统中设置，也可以通过项目根目录下的`.env`文件配置。

### 示例

```bash
# 基本用法
python pdf_to_markdown.py document.pdf

# 指定输出文件
python pdf_to_markdown.py document.pdf -o output.md

# 指定API密钥
python pdf_to_markdown.py document.pdf -k your_api_key_here
```

## 项目结构

- `pdf_to_markdown.py`: 主程序，处理命令行参数和PDF页面提取
- `vision_api.py`: 包含调用OpenAI视觉模型的函数
- `requirements.txt`: 项目依赖列表
- `.env`: 环境变量配置文件，用于设置API密钥和并发线程数

## 注意事项

- 需要有效的OpenAI API密钥
- 处理大型PDF文件可能需要较长时间
- 视觉模型的识别质量取决于PDF页面的清晰度和复杂性