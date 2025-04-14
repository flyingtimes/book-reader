# Gradio界面样式配置
THEME_CONFIG = {
    "title": "图书AI拆解工具",
    "theme": "soft",
    "css": """
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
    """
}

# 数据表格配置
TABLE_CONFIG = {
    "summary_table": {
        "headers": ["章节", "摘要"],
        "label": "内容摘要",
        "col_count": (2, "fixed"),
        "wrap": True,
        "column_widths": ["25%", "75%"]
    },
    "character_table": {
        "headers": ["人物姓名", "人物特点"],
        "label": "人物志",
        "col_count": (2, "fixed"),
        "wrap": True,
        "column_widths": ["25%", "75%"]
    }
}