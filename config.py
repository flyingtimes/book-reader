import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# API配置
API_KEY = os.getenv("OPENROUTER_API_KEY")
API_BASE_URL = "https://openrouter.ai/api/v1"

# 模型配置
MODEL_NAMES = [
    "openrouter/optimus-alpha",
    "openrouter/optimus-alpha",
    "openrouter/optimus-alpha", 
    "meta-llama/llama-4-scout:free"
]

# 摘要生成配置
MAX_LENGTH = 500000
MAX_TOKENS = 50000
MAX_RETRY = 4

# 缓存配置
ENABLE_CACHE = True

# 系统提示词
SYSTEM_PROMPTS = {
    "chapter_summary": """
    你是一个专业的图书摘要生成助手，请对提供的内容,给每个章节生成中文简述，以及生成全文中文总结。以json格式输出，格式如下：
    {
        "第1章": "第1章的摘要...",
        "第2章": "第2章的摘要...",
        ...,
        "总结": "本书的全文摘要总结..."
    }
    注意：摘要的内容要求是中文，每个摘要的长度约为200字，返回信息必须是标准的json格式，不要带其他信息。
    """,
    "character_summary": """
    你是一个专业的图书摘要生成助手，请对提供的内容,给每个人物生成中文的背景、性格特点、书中人物关系、角色特点的简述，以json格式输出，格式如下：
    {
        "rose": "rose的背景、性格特点、书中人物关系、角色特点的简述...",
        "小王": "小王的背景、性格特点、书中人物关系、角色特点的简述...",
        ...,
        "小明": "小明的背景、性格特点、书中人物关系、角色特点的简述..."
    }
    注意：简述的内容必须是中文，每个摘要的长度约为200字，返回信息必须是标准的json格式，不要带其他信息。
    """
}