# Quick Start

## 安装 LLM（选一个）

### Ollama（免费）
```bash
# 下载安装：https://ollama.com/download
ollama pull llama3.2
```

### DeepSeek（超便宜）
注册：https://platform.deepseek.com/

## 配置

复制 `env.example` 为 `.env`，选择你的 LLM：

```env
# Ollama
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.2

# 或 DeepSeek
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=你的key

# 或 OpenAI
LLM_PROVIDER=openai
OPENAI_API_KEY=你的key

PROJECT1_API_URL=http://localhost:8000
```

## 启动

```bash
python -m src.main serve
```

打开：http://127.0.0.1:5000

## 使用

1. 输入 ticker（如 AAPL）
2. 点击生成
3. 审查关系
4. 批准并提交

完成！

