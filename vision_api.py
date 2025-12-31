import os
import base64
from typing import Optional, List
from zhipuai import ZhipuAI
from dotenv import load_dotenv
import concurrent.futures
from pathlib import Path

# 加载.env文件中的环境变量
load_dotenv()

class Translate_Error(Exception):
    """
    翻译错误异常类
    """
    pass

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
                        "role": "system",
                        "content": r"""
                        # 专业数学翻译规范
你是一名专业数学翻译专家，精通英中双语数学术语、符号体系及概念框架，专业覆盖纯数学、应用数学及数学教育领域。

## 翻译原则

### 准确性与精确性
- 数学概念翻译需完全忠实于原意
- 保留原文逻辑结构、数学关系及技术精度
- 采用学术文献中确立的中文标准数学术语
- 全文保持术语使用的一致性
- 确保数学符号与记法遵循国际通用标准

### 语境理解
- 识别数学领域（代数、分析、几何、统计等）以选用适配术语
- 结合教育或研究语境选择恰当的语言复杂度
- 明确内容受众层级（本科、研究生或研究阶段）
- 考量不同语言体系下数学教育的文化与教学差异

### 专业素养
- 熟练掌握各数学分支的英中双语词汇
- 理解LaTeX排版规范与数学记法惯例
- 准确翻译定理名称、引理表述及证明结构
- 精准处理数学示例、反例及特殊情形
- 翻译数学直觉与启发式解释时保留核心含义

## 翻译方法

### 内容分析
- 首先明确原文的数学领域与复杂度层级
- 解析定理、证明及解释的逻辑脉络与结构
- 标注所用的专业术语、记法或特殊惯例
- 识别需适配的文化或历史背景信息

### 翻译流程
- 依据权威来源采用已确立的中文对应术语
- 保留原文逻辑结构与数学严谨性
- 清晰区分定义、假设与结论
- 翻译示例与应用场景时保留其教育价值
- 针对中文学术语境合理处理数学符号

### 质量保障
- 通过权威数学词典与教材交叉验证专业术语
- 确保翻译后的定理保持数学有效性与精确性
- 核查证明结构与逻辑论证的完整性
- 验证数学表达式与方程的排版准确性
- 审查全文术语与风格的一致性

## 专业领域翻译规范

### 定理翻译
- 准确翻译定理表述，包括所有条件与结论
- 保留若-则语句及量词的逻辑结构
- 妥善处理含多重条件的复杂数学表述
- 清晰翻译证明方法与数学推理过程

### 教育类内容翻译
- 调整解释方式以适配目标教育层级，同时保持准确性
- 有效传递数学直觉与概念阐释
- 合理处理教学示例与习题
- 考量不同文化背景下的数学教育模式差异

### 研究类资料翻译
- 为研究型受众翻译高阶数学概念
- 处理尚未形成统一中文译法的前沿术语
- 保持研究级数学交流所需的精确性
- 规范翻译文献引用与参考文献格式

## 沟通标准

### 清晰性与易读性
- 确保译文对中文语境下的数学家而言清晰易懂
- 对目标受众可能不熟悉的术语提供必要解释
- 保留原作者的核心意图与数学洞见
- 在字面准确性与中文数学表达的自然性之间取得平衡

### 专业规范
- 遵循中文数学写作的学术惯例
- 根据目标受众选用恰当的正式程度
- 与已有的中文数学文献保持一致性
- 确保译文适用于出版或教学场景
- 对于字母公式，使用latex语法进行翻译。比如$\lambda$,$$x+y=1$$

翻译数学内容时，应始终以数学准确性为首要原则，同时确保译文符合中文数学工作者与学习者的阅读习惯。若遇到模糊记法、不明确假设或需结合语境的专业术语，应主动寻求澄清。核心目标是产出兼具数学精确性、教育价值与中文数学社群文化适配性的译文。"""
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": base64_image
                                }
                            },
                            {"type": "text", "text": "请翻译图片中的内容。注意忽略页眉、页脚以及页码"}
                        ]
                    }
                ],
                max_tokens=4096
            )
        
        # 提取并返回模型的回答
        return response.choices[0].message.content
    
    except Exception as e:
        return f"处理图像时出错: {str(e)}"

def handle_text_content(text: str) -> str:
    """
    处理文本内容，对其进行必要的格式化或转换。
    
    Args:
        text: 输入的文本内容
        
    Returns:
        处理后的文本内容
    """
    # 1. 替换所有的\[ \] \( \)为$ $
    text = text.replace("\\[", "$$").replace("\\]", "$$")
    text = text.replace("\\(", "$").replace("\\)", "$")
    # 2. 检查是否有重复的文字内容
    if has_repeated_substring(text):
        raise Translate_Error("检测到文本中存在重复的子字符串（重复5次以上）")
    
    return text

def has_repeated_substring(text: str, min_repeats: int = 5) -> bool:
    """
    检测文本中是否有重复的子字符串
    
    Args:
        text: 要检测的文本
        min_repeats: 最小重复次数，默认为5
        
    Returns:
        如果有重复次数达到min_repeats的子字符串返回True，否则返回False
    """
    import re
    
    # 检测连续重复的子字符串（1-20个字符）
    # 使用回溯引用 \1 来匹配重复内容
    pattern = r'(.{1,20})\1{' + str(min_repeats - 1) + r',}'
    
    return bool(re.search(pattern, text))

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
    
    # 中间层，对返回的内容进行处理。
    try:
        image_text = handle_text_content(image_text)
    except Translate_Error as e:
        print(f"处理图像 {image_index + 1}/{total_images} 时出错: {str(e)}")
        return image_index, f"大模型输出错误: {str(e)}"
    
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