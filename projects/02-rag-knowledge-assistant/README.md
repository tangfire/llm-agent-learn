# 02 RAG Knowledge Assistant

第 2 个学习项目，目标是从最小 FastAPI 模板进入 RAG 闭环。

## 今天完成的范围

- 复用 `01-fastapi-minimal-chat` 的工程骨架
- 新建 RAG 项目目录与核心模块
- 定义 3 个接口：
  - `GET /health`
  - `POST /documents/text`
  - `POST /ask`
- 定义文档入库与问答的请求/响应 schema

## 当前说明

今天这版是“接口与工程骨架版”。

- `POST /documents/text`：已能接收文本、切分 chunk，并返回 chunk 预览
- `POST /ask`：已能返回 `answer`、`citations`、`retrieved_chunks`
- 检索目前是便于联调的预览实现，下一步再接 embedding + qdrant 正式检索

## 目录

```text
02-rag-knowledge-assistant/
├── app/
│   ├── api/
│   ├── core/
│   ├── schemas/
│   ├── services/
│   └── main.py
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

## 启动

```bash
cd /Users/firetang/Documents/llm/projects/02-rag-knowledge-assistant
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8001
```

## Curl

```bash
curl http://127.0.0.1:8001/health
```

```bash
curl -X POST http://127.0.0.1:8001/documents/text \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Redis Notes",
    "source": "redis-notes.md",
    "text": "Redis 是一个基于内存的数据结构存储系统，常用于缓存、消息队列和排行榜。"
  }'
```

```bash
curl -X POST http://127.0.0.1:8001/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Redis 常见应用场景有哪些？",
    "top_k": 3
  }'
```
