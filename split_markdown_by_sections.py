import os
import re
import argparse
from pathlib import Path


def sanitize_filename(name: str) -> str:
    """
    将标题文本转换为适合文件系统的安全文件名

    参数:
        name: 原始标题文本

    返回:
        适合在Windows文件系统保存的文件名字符串
    """
    invalid_chars = r"\\/:*?\"<>|"
    # 替换非法字符为下划线，并去除首尾空白
    sanitized = "".join("_" if ch in invalid_chars else ch for ch in name).strip()
    # 将连续空白压缩为单个空格
    sanitized = re.sub(r"\s+", " ", sanitized)
    return sanitized


def split_markdown_by_heading(input_path: str, output_dir: str, heading_level: int = 3) -> list:
    """
    按指定层级的Markdown标题(如"### 1.1 标题")拆分文件,为每个节生成一个独立的md文件

    参数:
        input_path: 源Markdown文件的绝对/相对路径,仅读取不修改
        output_dir: 输出目录; 若不存在则自动创建
        heading_level: 标题层级数字(默认3,匹配以`###`开头的节)

    返回:
        创建的节文件的绝对路径列表(按出现顺序)
    """
    level_hashes = "#" * heading_level
    # 形如: ### 1.1 佐恩引理
    header_pattern = re.compile(rf"^\s*{re.escape(level_hashes)}\s+([0-9]+(?:\.[0-9]+)*)\s+(.*)$")

    input_path = Path(input_path)
    output_dir_path = Path(output_dir)
    output_dir_path.mkdir(parents=True, exist_ok=True)

    if not input_path.exists():
        raise FileNotFoundError(f"源文件不存在: {input_path}")

    created_files = []

    with input_path.open("r", encoding="utf-8") as f:
        lines = f.readlines()

    current_section = None  # (number, title, content_lines)
    sections = []

    for line in lines:
        m = header_pattern.match(line)
        if m:
            # 推入上一节
            if current_section is not None:
                sections.append(current_section)
            number = m.group(1).strip()
            title = m.group(2).strip()
            current_section = (number, title, [line])
        else:
            if current_section is not None:
                current_section[2].append(line)
            else:
                # 还未遇到第一节标题的前置内容，跳过保留或后续根据需要处理
                # 为保持与需求一致(仅按节输出)，此处不生成文件
                pass

    # 最后一节
    if current_section is not None:
        sections.append(current_section)

    # 写出各节到文件
    for idx, (number, title, content_lines) in enumerate(sections, start=1):
        fname = sanitize_filename(f"{number} {title}.md")
        out_path = output_dir_path / fname
        with out_path.open("w", encoding="utf-8") as out:
            out.writelines(content_lines)
        created_files.append(str(out_path))

    return created_files


def main():
    """
    命令行入口: 将Markdown按`###`节标题拆分到指定目录

    用法示例:
        python split_markdown_by_sections.py -i \
            "d:/python/from_pdf_to_markdown/files/markdown/泛函分析2025.md" \
            -o "d:/python/from_pdf_to_markdown/files/markdown/split/泛函分析2025"
    """
    parser = argparse.ArgumentParser(description="按章节(###)拆分Markdown为多个文件")
    parser.add_argument("-i", "--input", required=True, help="输入Markdown文件路径(只读)")
    parser.add_argument("-o", "--output", required=False, help="输出目录路径(自动创建)")
    parser.add_argument("-l", "--level", type=int, default=3, help="标题层级(默认3,匹配###)")

    args = parser.parse_args()

    input_path = args.input
    if args.output:
        output_dir = args.output
    else:
        # 默认输出到 files/markdown/split/<源文件名(不含扩展)>
        base = Path(input_path).stem
        default_dir = Path(__file__).parent / "files" / "markdown" / "split" / base
        output_dir = str(default_dir)

    created = split_markdown_by_heading(input_path, output_dir, args.level)
    print(f"已创建 {len(created)} 个章节文件 到: {output_dir}")
    for p in created:
        print(p)


if __name__ == "__main__":
    main()