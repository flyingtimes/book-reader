from typing import List, Dict, Any, Optional
from openai import OpenAI
from config import MODEL_NAMES, MAX_RETRY, MAX_TOKENS

def handle_openai_response(response: Any) -> Optional[str]:
    """处理OpenAI API的响应
    
    Args:
        response: OpenAI API的响应对象
        
    Returns:
        str: 响应内容，如果响应无效则返回None
    """
    if not response or not response.choices:
        return None
    
    content = response.choices[0].message.content
    if not content:
        return None
    
    return content

def retry_api_call(client: OpenAI, content: str, system_prompt: str = None) -> Optional[str]:
    """使用重试机制调用OpenAI API
    
    Args:
        client: OpenAI客户端实例
        content: 需要处理的内容
        system_prompt: 系统提示词，默认为None
        
    Returns:
        str: API调用结果
        
    Raises:
        Exception: 当所有重试都失败时抛出异常
    """
    for attempt in range(MAX_RETRY):
        try:
            messages = [
                {"role": "user", "content": content}
            ]
            
            if system_prompt:
                messages.insert(0, {"role": "system", "content": system_prompt})
            
            print(f"正在使用模型：{MODEL_NAMES[attempt]}")
            response = client.chat.completions.create(
                model=MODEL_NAMES[attempt],
                messages=messages,
                max_tokens=MAX_TOKENS
            )
            
            result = handle_openai_response(response)
            if result:
                return result
            print(response)    
            print(f"响应无效，尝试使用下一个模型：{MODEL_NAMES[attempt]}")
            
        except Exception as e:
            if attempt >= MAX_RETRY - 1:
                raise Exception(f"API调用失败：{str(e)}")
            print(f"调用失败，尝试使用下一个模型：{MODEL_NAMES[attempt]}，错误信息：{str(e)}")
            
    raise Exception("处理超过最大重试次数")

def split_content(text: str, max_length: int = 30000) -> List[str]:
    """将文本按段落分割成不超过指定长度的片段
    
    Args:
        text: 需要分割的文本
        max_length: 每个片段的最大长度，默认为30000
        
    Returns:
        List[str]: 分割后的文本片段列表
    """
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = []
    current_length = 0
    
    for para in paragraphs:
        para_length = len(para)
        if current_length + para_length <= max_length:
            current_chunk.append(para)
            current_length += para_length
        else:
            if current_chunk:
                chunks.append('\n\n'.join(current_chunk))
                print(f"当前片段长度：{current_length}")
            current_chunk = [para]
            current_length = para_length
    
    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))
    
    print(f"将文档切分为{len(chunks)}个片段")
    return chunks

def update_progress(progress: Any, value: float, desc: str = None) -> None:
    """更新进度条
    
    Args:
        progress: gradio的进度条对象
        value: 进度值（0-1之间）
        desc: 进度描述，默认为None
    """
    if desc:
        progress(value, desc=desc)
    else:
        progress(value)