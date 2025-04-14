import json
import os
from openai import OpenAI
from markitdown import MarkItDown
from config import API_KEY, API_BASE_URL, MODEL_NAMES, MAX_TOKENS, MAX_RETRY, SYSTEM_PROMPTS

# 创建OpenAI客户端
def create_client(api_key=None):
    """创建OpenAI客户端"""
    return OpenAI(
        base_url=API_BASE_URL,
        api_key=api_key or API_KEY
    )

def convert_pdf_to_markdown(pdf_file, output_dir):
    """将PDF转换为Markdown格式"""
    if pdf_file is None:
        raise ValueError("PDF文件不能为空")
    
    md_content = MarkItDown().convert(pdf_file)
    if md_content is None:
        raise ValueError("PDF转换失败，请检查文件格式")
    
    return md_content

def generate_summary(client, content, prompt_type):
    """生成内容摘要"""
    attempt = 0
    while attempt < MAX_RETRY:
        try:
            response = client.chat.completions.create(
                model=MODEL_NAMES[attempt],
                extra_body={},
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPTS[prompt_type]},
                    {"role": "user", "content": f"请按格式处理以下内容：\n\n{content}"}
                ],
                max_tokens=MAX_TOKENS
            )
            
            if not response or not response.choices:
                attempt += 1
                continue
                
            summary = response.choices[0].message.content
            if not summary:
                attempt += 1
                continue
            
            summary_obj = json.loads(summary)
            if not isinstance(summary_obj, dict) or not summary_obj:
                attempt += 1
                continue
                
            return summary_obj
            
        except Exception as e:
            attempt += 1
            if attempt >= MAX_RETRY:
                raise Exception(f"摘要生成失败：{str(e)}")
            continue
    
    raise Exception("处理超过最大重试次数")

def process_pdf_file(pdf_file, output_dir, api_key=None):
    """处理PDF文件并生成摘要"""
    try:
        # 创建客户端
        client = create_client(api_key)
        
        # 转换PDF到Markdown
        md_content = convert_pdf_to_markdown(pdf_file, output_dir)
        
        # 生成章节摘要
        chapter_summary = generate_summary(client, md_content, "chapter_summary")
        chapter_data = [[chapter, content] for chapter, content in chapter_summary.items()]
        
        # 生成人物志
        character_summary = generate_summary(client, md_content, "character_summary")
        character_data = [[name, feature] for name, feature in character_summary.items()]
        
        return chapter_data, character_data
        
    except Exception as e:
        return [["错误", str(e)]], [["错误", str(e)]]