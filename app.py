import os
import gradio as gr
from openai import OpenAI
from markitdown import MarkItDown
from dotenv import load_dotenv
import tempfile

# 加载环境变量
load_dotenv()
api_key=os.getenv("OPENROUTER_API_KEY")
# 创建OpenAI客户端
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key
)

# 创建输出目录
output_dir = os.path.join(os.getcwd(), "output")
os.makedirs(output_dir, exist_ok=True)

def process_pdf(pdf_file, api_key=None):
    """处理PDF文件，转换为Markdown并生成摘要"""
    import json
    global client
    print(client.api_key)
    # 验证PDF文件输入
    if pdf_file is None:
        print("Error: PDF file is None")
        return [["错误", "请上传PDF文件"]]
    try:
        md_content = MarkItDown().convert(pdf_file)
        if md_content is None:
            print("Error: Failed to convert PDF to Markdown")
            return [["错误", "PDF转换失败，请检查文件格式"]]
        print(md_content)
        md_file_path = os.path.join(output_dir, "output.md")
        max_retry = 4
        attempt = 0
        modelnames = ["meta-llama/llama-4-scout:free","meta-llama/llama-4-scout:free","openrouter/optimus-alpha", "moonshotai/kimi-vl-a3b-thinking:free"]
        while attempt < max_retry:
            attempt += 1
            try:
                response = client.chat.completions.create(
                    model=modelnames[attempt-1],
                    extra_body={},
                    messages=[
                        {"role": "system", "content": '''
                        你是一个专业的图书摘要生成助手，请对提供的内容,给每个章节生成中文摘要，以及生成全文中文总结。以json格式输出，格式如下：
                        {
                            "第1章": "第1章的摘要",
                            "第2章": "第2章的摘要",
                            ...,
                            "总结": "本书的全文摘要总结"
                        }
                        注意：摘要的内容是中文，每个摘要的长度约为200字，返回信息必须是json格式。
                        '''},
                        {"role": "user", "content": f"请按格式处理以下内容：\n\n{md_content}"}
                    ],
                    max_tokens=10000
                )
                print("API Response:", response)
                if not response or not response.choices:
                    print("Error: Invalid API response - No choices available")
                    continue
                    
                summary = response.choices[0].message.content
                print("Raw summary content:", summary)
                if not summary:
                    print("Error: Empty summary content from API")
                    continue
                
                try:
                    summary_obj = json.loads(summary)
                    if not isinstance(summary_obj, dict):
                        print("Error: Summary is not a valid JSON object")
                        continue
                except json.JSONDecodeError as je:
                    print(f"JSON parsing error: {je}")
                    continue
                except Exception as e:
                    print(f"Unexpected error parsing summary: {e}")
                    continue
                
                if not summary_obj:
                    print("Error: Empty summary object after parsing")
                    continue
                    
                table_data = [[chapter, content] for chapter, content in summary_obj.items()]
                return table_data
            except Exception as m:
                print(f"Error processing PDF: {m}")
                if attempt >= max_retry:
                    return [["错误", "摘要生成失败，请重试"]]
                continue
        return [["错误", "处理超过最大重试次数"]]
    except Exception as e:
        print(f"Error processing PDF2: {e}")
        return [["错误", "PDF处理过程出错"]]

# 创建Gradio界面
with gr.Blocks(title="图书AI拆解工具", theme="soft", css="""
body { background: #f6f8fa; font-family: 'Inter', 'PingFang SC', Arial, sans-serif; color: #23272f; }
.gr-block.gr-markdown { background: white; border-radius: 12px; box-shadow: 0 2px 12px 0 rgba(32,42,54,.09); margin-bottom:18px; }
.gr-box { background: white !important; border-radius: 12px !important; box-shadow: 0 4px 20px 0 rgba(35, 39, 47, 0.07) !important; }
.gr-input, input[type="password"], textarea { border-radius: 8px !important; border: 1.2px solid #e5e7eb !important; background: #f8fafb !important; font-size: 16px !important; }
.gr-button { background: linear-gradient(90deg, #007aff 0%, #20a8ea 100%); color: #fff !important; font-weight: 500; border-radius: 8px !important; box-shadow: 0 2px 8px 0 rgba(32,42,54,.08); font-size: 16px !important; }
.gr-button:hover { background: linear-gradient(90deg, #3191e2 0%, #22c1c3 100%); }
.gr-datatable { background: #fff; border-radius: 10px; box-shadow: 0 2px 8px 0 rgba(35, 39, 47, 0.07); font-size: 15px; }
.gr-datatable th, .gr-datatable td { padding: 10px 16px; }
.gr-datatable thead { background: #f3f6fa; }
.gr-input label, .gr-textbox label { font-weight: 500; color: #22223f; }
::-webkit-scrollbar { width: 8px; background: #e9ebf0; }
::-webkit-scrollbar-thumb { background: #d5dbe7; border-radius: 6px; }
""") as demo:
    gr.Markdown("# 图书AI拆解工具")
    gr.Markdown("上传PDF文件，自动转换为Markdown格式并生成内容摘要。")
    
    with gr.Row():
        pdf_input = gr.File(label="上传PDF文件", file_types=[".pdf"])
        api_key = gr.Textbox(label="OpenRouter API密钥（可选）", placeholder="如果未设置环境变量，请在此输入您的OpenRouter API密钥", type="password")
        submit_btn = gr.Button("开始处理")
        
    with gr.Row():
        summary_output = gr.Dataframe(
            headers=["章节", "摘要"],
            label="内容摘要",
            col_count=(2, "fixed"),
            wrap=True,
            column_widths=["25%", "75%"],
            height=600
        )
    
    submit_btn.click(
        fn=process_pdf,
        inputs=[pdf_input, api_key],
        outputs=[summary_output]
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