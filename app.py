import os
import gradio as gr
from pathlib import Path
from dotenv import load_dotenv
from pdf_to_markdown import process_files, process_file

# 加载环境变量
load_dotenv()

def process_files_ui(files, output_dir=None):
    """
    处理上传的文件（PDF或图片）并转换为Markdown
    
    Args:
        files: 上传的文件列表
        output_dir: 输出目录（已废弃，保留参数是为了兼容性）
        
    Returns:
        转换结果信息和生成的Markdown文件路径列表
    """
    if not files or len(files) == 0:
        return "请上传文件（支持PDF和常见图片格式）", None
    
    # 创建上传和输出目录
    upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "files", "upload")
    markdown_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "files", "markdown")
    
    os.makedirs(upload_dir, exist_ok=True)
    os.makedirs(markdown_dir, exist_ok=True)
    
    # 从环境变量获取API密钥
    api_key = os.environ.get("OPENAI_API_KEY")
    
    # 处理每个上传的文件
    processed_files = []
    result_messages = []
    
    for file in files:
        try:
            # 获取文件名和路径
            original_file_path = file.name
            file_name = os.path.basename(original_file_path)
            
            # 保存上传的文件到指定目录
            file_path = os.path.join(upload_dir, file_name)
            
            # 如果上传的文件不在指定目录，复制一份到指定目录
            if original_file_path != file_path:
                import shutil
                shutil.copy2(original_file_path, file_path)
            
            # 确定输出路径
            output_path = os.path.join(markdown_dir, os.path.splitext(file_name)[0] + ".md")
            
            # 调用处理函数
            process_file(file_path, output_path, api_key)
            
            result_messages.append(f"文件 '{file_name}' 转换成功！")
            processed_files.append(output_path)
            
        except Exception as e:
            result_messages.append(f"处理文件 '{file.name}' 时出错: {str(e)}")
    
    # 如果有多个文件，返回所有处理结果
    if len(processed_files) > 0:
        result_message = "\n".join(result_messages)
        return result_message, processed_files[0] if processed_files else None
    else:
        return "所有文件处理失败", None

def view_markdown(markdown_path):
    """
    查看生成的Markdown文件内容
    
    Args:
        markdown_path: Markdown文件路径
        
    Returns:
        Markdown文件内容
    """
    if not markdown_path or not os.path.exists(markdown_path):
        return "没有可用的Markdown文件"
    
    try:
        with open(markdown_path, "r", encoding="utf-8") as f:
            content = f.read()
        return content
    except Exception as e:
        return f"读取Markdown文件时出错: {str(e)}"

# 创建Gradio界面
with gr.Blocks(title="PDF转Markdown工具") as app:
    gr.Markdown("<div style='text-align: center;'><h1>PDF转Markdown工具</h1></div>")
    gr.Markdown("""<div style='text-align: center;'>作者: <a href="https://github.com/because66666">Because66666</a></div>""")
    gr.Markdown("<div style='text-align: center;'>使用LLM视觉模型将PDF文件转换为Markdown格式</div>")
    
    with gr.Row():
        with gr.Column():
            file_input = gr.File(label="上传文件", file_types=[".pdf", ".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff"], file_count="multiple")
            convert_btn = gr.Button("开始转换", variant="primary")
            result = gr.Textbox(label="转换结果", lines=5)
        
        with gr.Column():
            markdown_output = gr.Textbox(label="Markdown源码", lines=20)
        
        with gr.Column():
            # 创建Markdown渲染组件
            markdown_render = gr.Markdown(label="Markdown渲染预览", elem_id="markdown-render")
            
            # 添加自定义CSS样式，使Markdown渲染区域与文本框样式一致
            gr.HTML("""
            <style>
            #markdown-render {
                border: 1px solid rgba(0, 0, 0, 0.1);
                border-radius: 4px;
                padding: 10px;
                background-color: white;
                height: 400px;
                overflow-y: auto;
                margin-top: 5px;
            }
            </style>
            """)
    
    # 设置事件处理
    def process_and_display(files):
        result_message, md_path = process_files_ui(files, None)
        md_content = ""
        if md_path and os.path.exists(md_path):
            md_content = view_markdown(md_path)
        return result_message, md_content, md_content
    
    convert_btn.click(
        process_and_display, 
        inputs=[file_input], 
        outputs=[result, markdown_output, markdown_render]
    )
    
    gr.Markdown("""
    ## 使用说明
    1. 上传文件（支持PDF和常见图片格式：JPG、PNG、BMP、GIF、TIFF等）
    2. 可以一次上传多个文件进行批量处理
    3. 点击"开始转换"按钮
    4. 转换完成后，右侧会显示生成的Markdown内容（显示第一个成功处理的文件）
    
    **文件存储位置**:
    - 上传的文件将保存在 `files/upload` 目录
    - 生成的Markdown文件将保存在 `files/markdown` 目录
    
    **注意**: 
    - 请确保已在.env文件中设置了OPENAI_API_KEY环境变量
    - 图片文件将直接处理，PDF文件会按页处理并合并结果
    """)

# 启动应用
if __name__ == "__main__":
    app.launch(server_name="127.0.0.1", share=False)