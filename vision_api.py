import os
import base64
from typing import Optional, List
from zhipuai import ZhipuAI
from dotenv import load_dotenv
import concurrent.futures
from pathlib import Path

# 加载.env文件中的环境变量
load_dotenv()

def process_pdf_page(image_path: str, api_key: Optional[str] = None) -> str:
    """
    使用OpenAI视觉模型处理图像文件（PDF页面或其他图像格式）
    
    Args:
        image_path: 图像文件路径
        api_key: OpenAI API密钥，如果为None则从环境变量获取
        
    Returns:
        视觉模型的文本输出
    """
    # 设置API密钥
    api_key = api_key or os.environ.get("OPENAI_API_KEY")
        
    if not api_key:
        raise ValueError("OpenAI API密钥未提供，请通过参数传入或设置OPENAI_API_KEY环境变量")
    
    try:
        # 创建ZhipuAI客户端
        client = ZhipuAI(api_key=api_key)
        
        # 打开并读取图像文件
        with open(image_path, "rb") as image_file:
            # 将图像编码为base64
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            # 调用ZhipuAI视觉模型API
            response = client.chat.completions.create(
                temperature=0.0,  # 控制输出的随机性，0.0为确定输出，1.0为最大随机性
                model="glm-4v-plus-0111",  # 使用支持视觉的模型
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": base64_image
                                }
                            },
                            {"type": "text", "text": "请原文输出，不需要解释。请忽略页码、页眉和页脚以及页面下方关于夸克扫描王的有关内容。公式等字符使用标准latex格式进行输出。如果页面为英文，请"}
                        ]
                    }
                ],
                max_tokens=4096
            )
        
        # 提取并返回模型的回答
        return response.choices[0].message.content
    
    except Exception as e:
        return f"处理图像时出错: {str(e)}"


def process_single_image(image_data):
    """
    处理单个图像文件
    
    Args:
        image_data: 包含图像处理所需数据的字典
        
    Returns:
        包含图像索引和处理结果的元组
    """
    image_index = image_data['image_index']
    image_path = image_data['image_path']
    api_key = image_data['api_key']
    total_images = image_data['total_images']
    
    print(f"处理图像 {image_index + 1}/{total_images}: {image_path}")
    
    # 调用OpenAI视觉模型处理图像
    image_text = process_pdf_page(image_path, api_key)
    
    # 返回图像索引和处理结果
    return image_index, image_text


def process_images(image_paths: List[str], api_key: Optional[str] = None, max_workers: Optional[int] = None) -> List[str]:
    """
    并发处理多个图像文件
    
    Args:
        image_paths: 图像文件路径列表
        api_key: OpenAI API密钥，如果为None则从环境变量获取
        max_workers: 最大并发线程数，如果为None则从环境变量获取
        
    Returns:
        处理结果列表，按原始顺序排列
    """
    # 如果未指定max_workers，则从环境变量获取，默认为5
    if max_workers is None:
        max_workers = int(os.environ.get("MAX_WORKERS", 5))
    
    # 准备图像处理任务
    total_images = len(image_paths)
    image_tasks = []
    
    for image_index, image_path in enumerate(image_paths):
        # 检查图像文件是否存在
        if not os.path.exists(image_path):
            print(f"错误：图像文件 '{image_path}' 不存在")
            continue
            
        image_tasks.append({
            'image_index': image_index,
            'image_path': image_path,
            'api_key': api_key,
            'total_images': total_images
        })
    
    # 使用线程池并发处理图像
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务并获取Future对象
        future_to_image = {executor.submit(process_single_image, task): task for task in image_tasks}
        
        # 获取结果
        for future in concurrent.futures.as_completed(future_to_image):
            try:
                image_index, image_content = future.result()
                results.append((image_index, image_content))
            except Exception as e:
                print(f"处理图像时出错: {str(e)}")
    
    # 按原始顺序排序结果
    results.sort(key=lambda x: x[0])
    
    # 返回处理结果列表
    return [content for _, content in results]