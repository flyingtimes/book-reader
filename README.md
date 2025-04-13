# 图书AI拆解工具

这是一个基于Gradio的WebUI程序，可以将PDF格式的图书或文档转换为Markdown格式，并使用OpenAI API生成内容摘要。

## 功能特点

- 上传PDF文件并转换为Markdown格式
- 使用[markitdown](https://github.com/microsoft/markitdown)库进行PDF到Markdown的转换
- 调用OpenAI API对文档内容进行智能摘要
- 保存转换后的Markdown文件到本地
- 简洁直观的用户界面

## 安装步骤

1. 克隆仓库

```bash
git clone https://github.com/yourusername/book-reader.git
cd book-reader
```

2. 安装依赖

```bash
pip install -r requirements.txt
```

3. 配置OpenAI API密钥

将`.env.example`文件复制为`.env`，并填入您的OpenAI API密钥：

```bash
cp .env.example .env
```

然后编辑`.env`文件，填入您的API密钥：

```
OPENAI_API_KEY=your_openai_api_key_here
```

## 使用方法

1. 启动应用

```bash
python app.py
```

2. 在浏览器中打开显示的URL（通常是 http://127.0.0.1:7860）

3. 上传PDF文件，点击"开始处理"按钮

4. 等待处理完成后，可下载转换后的Markdown文件并查看AI生成的摘要

## 注意事项

- 转换后的Markdown文件将保存在项目的`output`目录中
- 如果未通过环境变量设置OpenRouter API密钥，可以在界面中直接输入
- 处理大型PDF文件可能需要较长时间
- 摘要生成使用的是OpenRouter的optimus-alpha模型

## 依赖项

- gradio: 用于创建WebUI界面
- openai: OpenRouter API客户端
- markitdown: 用于PDF到Markdown的转换
- python-dotenv: 用于加载环境变量
- PyPDF2: 用于PDF处理

## 许可证

MIT