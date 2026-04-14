# 01 FastAPI Minimal Chat

一个适合作为后续学习模板的最小 LLM 服务。

## 功能

- `GET /health`: 查看服务和模型模式
- `POST /chat`: 普通对话接口
- `POST /stream_chat`: 流式对话接口（SSE）

## 目录

```text
01-fastapi-minimal-chat/
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
cd /Users/firetang/Documents/llm/projects/01-fastapi-minimal-chat
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

## 调试

```bash
curl http://127.0.0.1:8000/health
```

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"你好，做个自我介绍"}'
```

```bash
curl -N -X POST http://127.0.0.1:8000/stream_chat \
  -H "Content-Type: application/json" \
  -d '{"message":"请用一句话介绍 FastAPI"}'
```

## 真实模型调用

默认 `LLM_PROVIDER=auto`。

- 如果环境里有 `OPENAI_API_KEY`，会走真实 OpenAI Responses API
- 如果没有 key，会自动回退到本地 mock，方便先把接口和工程结构跑通
