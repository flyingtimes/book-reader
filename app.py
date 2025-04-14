import os
import gradio as gr
from utils import process_pdf_file
from styles import THEME_CONFIG, TABLE_CONFIG
from config import ENABLE_CACHE

# 创建输出目录
output_dir = os.path.join(os.getcwd(), "output")
os.makedirs(output_dir, exist_ok=True)

def process_pdf(pdf_file, api_key=None, enable_cache=ENABLE_CACHE):
    """处理PDF文件，转换为Markdown并生成摘要"""
    return process_pdf_file(pdf_file, output_dir, api_key, enable_cache)

# 创建Gradio界面
with gr.Blocks(**THEME_CONFIG) as demo:
    gr.Markdown("# 图书AI拆解工具")
    gr.Markdown("上传PDF文件，自动转换为Markdown格式并生成内容摘要。")
    
    with gr.Row():
        pdf_input = gr.File(label="上传PDF文件", file_types=[".pdf"])
        api_key = gr.Textbox(
            label="OpenRouter API密钥（可选）",
            placeholder="如果未设置环境变量，请在此输入您的OpenRouter API密钥",
            type="password"
        )
        enable_cache = gr.Checkbox(label="缓存加速", value=ENABLE_CACHE)
        submit_btn = gr.Button("开始处理")
        
    with gr.Tabs() as tabs:
        with gr.TabItem("内容摘要"):
            summary_output = gr.Dataframe(**TABLE_CONFIG["summary_table"])

        with gr.TabItem("人物志"):
            summary_charaters = gr.Dataframe(**TABLE_CONFIG["character_table"])
    
    submit_btn.click(
        fn=process_pdf,
        inputs=[pdf_input, api_key, enable_cache],
        outputs=[summary_output, summary_charaters]
    )
    
    gr.Markdown("""
    ## 使用说明
    1. 上传PDF格式的图书或文档
    2. 如果未通过环境变量设置OpenAI API密钥，请在文本框中输入
    3. 点击"开始处理"按钮
    4. 等待处理完成后，可下载转换后的Markdown文件并查看AI生成的摘要
    
    **注意**: 转换后的Markdown文件将保存在项目的output目录中
    """)

if __name__ == "__main__":
    demo.launch()