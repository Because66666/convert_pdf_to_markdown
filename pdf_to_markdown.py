import os
import sys
import argparse
from pathlib import Path
import tempfile
import fitz  # PyMuPDF
import concurrent.futures
from vision_api import process_pdf_page
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


def process_single_page(page_data):
    """
    处理单个PDF页面
    
    Args:
        page_data: 包含页面处理所需数据的字典
        
    Returns:
        包含页码和处理结果的元组
    """
    page_num = page_data['page_num']
    page = page_data['page']
    temp_dir = page_data['temp_dir']
    api_key = page_data['api_key']
    total_pages = page_data['total_pages']
    
    print(f"处理第 {page_num + 1} 页，共 {total_pages} 页...")
    
    # 将页面渲染为图像
    image_path = os.path.join(temp_dir, f"page_{page_num + 1}.png")
    pix = page.get_pixmap()
    pix.save(image_path)
    
    # 调用OpenAI视觉模型处理图像
    page_text = process_pdf_page(image_path, api_key)
    
    # 返回页码和处理结果
    return page_num, f"\n\n{page_text}\n\n"


def convert_pdf_to_markdown(pdf_path: str, output_path: str = None, api_key: str = None, max_workers: int = None):
    """
    将PDF文件转换为Markdown格式
    
    Args:
        pdf_path: PDF文件路径
        output_path: 输出的Markdown文件路径，如果为None则使用PDF文件名
        api_key: OpenAI API密钥
        max_workers: 最大并发线程数，如果为None则从环境变量获取
    """
    # 如果未指定max_workers，则从环境变量获取，默认为5
    if max_workers is None:
        max_workers = int(os.environ.get("MAX_WORKERS", 5))

    # 检查PDF文件是否存在
    if not os.path.exists(pdf_path):
        print(f"错误：PDF文件 '{pdf_path}' 不存在")
        return

    # 如果未指定输出路径，则使用PDF文件名
    if output_path is None:
        output_path = os.path.splitext(pdf_path)[0] + ".md"
    # 打开PDF文件
    try:
        pdf_document = fitz.open(pdf_path)
    except Exception as e:
        print(f"打开PDF文件时出错: {str(e)}")
        return

    # 创建临时目录存储页面图像
    with tempfile.TemporaryDirectory() as temp_dir:
        # 准备页面处理任务
        total_pages = len(pdf_document)
        page_tasks = []
        
        for page_num, page in enumerate(pdf_document):
            page_tasks.append({
                'page_num': page_num,
                'page': page,
                'temp_dir': temp_dir,
                'api_key': api_key,
                'total_pages': total_pages
            })
        
        # 使用线程池并发处理页面
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务并获取Future对象
            future_to_page = {executor.submit(process_single_page, task): task for task in page_tasks}
            
            # 获取结果
            for future in concurrent.futures.as_completed(future_to_page):
                try:
                    page_num, page_content = future.result()
                    results.append((page_num, page_content))
                except Exception as e:
                    print(f"处理页面时出错: {str(e)}")
        
        # 按页码顺序组装Markdown内容
        results.sort(key=lambda x: x[0])  # 按页码排序
        markdown_content = ""
        for _, content in results:
            markdown_content += content

        # 关闭PDF文件
        pdf_document.close()

        # 写入Markdown文件
        with open(output_path, "w", encoding="utf-8") as md_file:
            md_file.write(markdown_content)

        print(f"转换完成！Markdown文件已保存到: {output_path}")


def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="将PDF文件转换为Markdown格式")
    parser.add_argument("pdf_path", help="PDF文件路径")
    parser.add_argument("-o", "--output", help="输出的Markdown文件路径")
    parser.add_argument("-k", "--api-key", help="OpenAI API密钥")

    args = parser.parse_args()

    # 调用转换函数
    convert_pdf_to_markdown(args.pdf_path, args.output, args.api_key)


if __name__ == "__main__":
    main()
