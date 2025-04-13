import os
import base64
from typing import Optional
from openai import OpenAI
from dotenv import load_dotenv

# 加载.env文件中的环境变量
load_dotenv()

def process_pdf_page(image_path: str, api_key: Optional[str] = None) -> str:
    """
    使用OpenAI视觉模型处理PDF页面图像
    
    Args:
        image_path: PDF页面的图像路径
        api_key: OpenAI API密钥，如果为None则从环境变量获取
        
    Returns:
        视觉模型的文本输出
    """
    # 设置API密钥
    api_key = api_key or os.environ.get("OPENAI_API_KEY")
        
    if not api_key:
        raise ValueError("OpenAI API密钥未提供，请通过参数传入或设置OPENAI_API_KEY环境变量")
    
    try:
        # 创建OpenAI客户端
        client = OpenAI(api_key=api_key, base_url="https://open.bigmodel.cn/api/paas/v4/")
        
        # 打开并读取图像文件
        with open(image_path, "rb") as image_file:
            # 将图像编码为base64
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            # 调用OpenAI视觉模型API
            response = client.chat.completions.create(
                model="glm-4v-plus-0111",  # 使用支持视觉的模型
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "请原文输出，不需要解释。请忽略页码、页眉和页脚。"},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                            }
                        ]
                    }
                ],
                max_tokens=4096
            )
        
        # 提取并返回模型的回答
        return response.choices[0].message.content
    
    except Exception as e:
        return f"处理图像时出错: {str(e)}"