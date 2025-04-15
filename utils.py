import json
import os
from typing import List, Dict, Any, Tuple, Optional
from openai import OpenAI
from markitdown import MarkItDown
from config import API_KEY, API_BASE_URL, MODEL_NAMES, MAX_TOKENS, MAX_RETRY, SYSTEM_PROMPTS, MAX_LENGTH
import gradio as gr
from database import PDFCache
from helpers import split_content, retry_api_call, update_progress

def translate_content(client: OpenAI, content: str, progress: Any) -> str:
    """将内容翻译成中文
    
    Args:
        client: OpenAI客户端实例
        content: 需要翻译的内容
        progress: gradio进度条对象
        
    Returns:
        str: 翻译后的中文内容
        
    Raises:
        Exception: 当翻译失败时抛出异常
    """
    if len(content) <= 30000:
        return retry_api_call(
            client,
            content,
            "你是一个专业的翻译助手，请将提供的内容翻译成中文，保持原文的格式和结构。"
        )
    
    content_chunks = split_content(content)
    total_chunks = len(content_chunks)
    translations = []
    
    for i, chunk in enumerate(content_chunks):
        print(f"正在翻译第{i + 1}/{total_chunks}个片段...")
        update_progress(progress, 0.5 + (i + 1)/total_chunks/2, "正在翻译...")
        
        translation = retry_api_call(
            client,
            chunk,
            "你是一个专业的翻译助手，请将提供的内容翻译成中文，保持原文的格式和结构。"
        )
        translations.append(translation)
        print(f"第{i + 1}/{total_chunks}个片段翻译完成")
    
    print("所有片段翻译完成，正在合并结果...")
    return '\n\n'.join(translations)

def create_client(api_key: Optional[str] = None) -> OpenAI:
    """创建OpenAI客户端
    
    Args:
        api_key: API密钥，默认为None，将使用配置文件中的密钥
        
    Returns:
        OpenAI: OpenAI客户端实例
    """
    return OpenAI(
        base_url=API_BASE_URL,
        api_key=api_key or API_KEY
    )

def convert_pdf_to_markdown(pdf_file: str, output_dir: str) -> str:
    """将PDF转换为Markdown格式
    
    Args:
        pdf_file: PDF文件路径
        output_dir: 输出目录
        
    Returns:
        str: 转换后的Markdown内容
        
    Raises:
        ValueError: 当PDF文件为空或转换失败时抛出异常
    """
    if pdf_file is None:
        raise ValueError("PDF文件不能为空")
    
    md_content = MarkItDown().convert(pdf_file)
    if md_content is None:
        raise ValueError("PDF转换失败，请检查文件格式")
    
    return str(md_content)

def decode_json(json_str: str) -> Optional[Dict]:
    """解码JSON字符串
    
    Args:
        json_str: JSON字符串
        
    Returns:
        Dict: 解析后的JSON对象，解析失败时返回None
    """
    json_str = json_str.strip()
    
    # 确保文本以 { 开始 } 结束
    if not (json_str.startswith('{') and json_str.endswith('}')):
        lines = json_str.split('\n')
        result = []
        run = False
        for line in lines:
            if line.startswith('{'):
                run = True
            if run:
                result.append(line)
            if line.startswith('}'):
                run = False
        try:
            return json.loads(''.join(result))
        except json.JSONDecodeError:
            print(f"JSON解码失败：\n{result}")
            return None
            
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        print(f"JSON解码失败：\n{json_str}")
        return None
def generate_summary(client: OpenAI, content: str, prompt_type: str) -> Dict:
    """生成内容摘要
    
    Args:
        client: OpenAI客户端实例
        content: 需要生成摘要的内容
        prompt_type: 摘要类型，对应SYSTEM_PROMPTS中的键
        
    Returns:
        Dict: 生成的摘要内容
        
    Raises:
        Exception: 当摘要生成失败时抛出异常
    """
    if len(content) > MAX_LENGTH:
        content = content[:MAX_LENGTH]
    for attempt in range(MAX_RETRY):    
        response = retry_api_call(
            client,
            f"请按格式处理以下内容：\n\n{content}",
            SYSTEM_PROMPTS[prompt_type]
        )
        
        print(f"模型返回长度:{len(response)}")
        summary_obj = decode_json(response)
        if summary_obj is not None:
            break
        
    return summary_obj

def process_pdf_file(pdf_file: str, output_dir: str, api_key: Optional[str] = None, enable_cache: bool = True) -> Tuple[List[List[str]], List[List[str]], str, str]:
    """处理PDF文件并生成摘要
    
    Args:
        pdf_file: PDF文件路径
        output_dir: 输出目录
        api_key: API密钥，默认为None
        enable_cache: 是否启用缓存，默认为True
        
    Returns:
        Tuple[List[List[str]], List[List[str]], str, str]: 
            - 章节数据：[章节名, 摘要内容]
            - 人物数据：[人物名, 人物特征]
            - Markdown内容
            - 翻译内容
    """
    try:
        progress = gr.Progress()
        cache = PDFCache()
        cache_result = cache.get_cache(pdf_file)
        
        if cache_result:
            update_progress(progress, 0.2, "从缓存加载内容")
            md_content = cache_result[0]
        else:
            update_progress(progress, 0, "开始转换PDF到Markdown")
            md_content = convert_pdf_to_markdown(pdf_file, output_dir)
            update_progress(progress, 0.2, f"PDF转换完成，内容长度：{len(md_content)}")
        if not (enable_cache and cache_result):
            client = create_client(api_key)
            
            update_progress(progress, 0.3, "正在生成章节摘要")
            chapter_summary =  generate_summary(client, md_content, "chapter_summary")
            chapter_data = [[chapter, content] for chapter, content in chapter_summary.items()]
            
            update_progress(progress, 0.5, "正在生成人物志")
            character_summary =  generate_summary(client, md_content, "character_summary")
            character_data = [[name, feature] for name, feature in character_summary.items()]
            
            update_progress(progress, 0.6, "正在翻译内容")
            translation =  translate_content(client, md_content, progress)
            
            update_progress(progress, 0.9, "正在保存缓存")
            cache.save_cache(pdf_file, md_content, chapter_data, character_data, translation)
            update_progress(progress, 1.0, "处理完成")
        else:
            md_content, chapter_data, character_data, translation = cache_result
            
        return chapter_data, character_data, md_content, translation
        
    except Exception as e:
        error_msg = str(e)
        return [["错误", error_msg]], [["错误", error_msg]], "", ""