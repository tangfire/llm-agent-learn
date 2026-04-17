# 02 RAG Knowledge Assistant

第 2 个学习项目，目标是从最小 FastAPI 模板进入 RAG 闭环。

## 当前完成的范围

- 复用 `01-fastapi-minimal-chat` 的工程骨架
- 文本入库
- chunk 切分
- embedding
- qdrant 本地向量检索
- 基于检索结果生成回答
- 返回 citations 与 retrieved_chunks

## 当前说明

今天这版已经不是纯骨架，而是第一版可运行 RAG。

- `POST /documents/text`：接收文本，切分 chunk，生成 embedding，并写入本地 qdrant
- `POST /ask`：对问题生成 query embedding，做向量检索，再返回 `answer`、`citations`、`retrieved_chunks`
- 配置了 `OPENAI_API_KEY` 时，embedding 走 OpenAI API，answer 走 OpenAI Responses API
- 没有配置 key 时，embedding 走本地 hash fallback，answer 走本地 fallback

## RAG 流程

```text
POST /documents/text
  -> chunker
  -> embeddings
  -> qdrant local upsert

POST /ask
  -> question embedding
  -> qdrant vector search
  -> LLM answer
  -> citations + retrieved_chunks
```

## 这一阶段必须会讲的 3 个概念

### 1. RAG 为什么比微调更适合知识库问答

RAG 更适合知识库问答，核心原因是知识库内容会频繁变化，而模型参数不会自动跟着变。

- RAG 的思路是“先检索，再回答”，文档更新后只要重新入库，不需要重新训练模型
- 微调更适合改变模型的风格、格式、任务习惯，不适合频繁注入一批会变化的业务知识
- 知识库问答最重要的是“能跟最新资料同步”，这一点 RAG 成本更低、迭代更快
- RAG 还能把命中的原文片段一起返回，方便检查答案是不是有依据

一句话讲法：
知识库问答的重点是“知识要新、要可追溯、要方便更新”，所以通常优先选 RAG，而不是先做微调。

### 2. 为什么要 chunk，而不是整篇文档一起喂

因为整篇文档通常太长、信息太杂，直接整篇喂给模型和向量检索都会变差。

- 一篇文档里往往有多个主题，整篇做 embedding 会把不同主题混在一起，检索不够精准
- 切成 chunk 后，每个片段语义更集中，向量检索更容易找到真正相关的内容
- chunk 还能减少 prompt 长度，避免把大量无关内容塞给模型，降低成本
- 后续做 citations 也更自然，因为可以明确告诉用户答案来自哪一段

一句话讲法：
chunk 的目的不是“拆着玩”，而是为了让检索更准、上下文更短、引用更清楚。

### 3. 为什么回答里必须带 citations

因为知识库问答不是只要“像对了”就行，而是要让人知道答案依据来自哪里。

- citations 可以让用户快速核对答案是否真的来自文档，而不是模型自己编的
- 当答案不完整或有争议时，引用能帮助继续追查原文
- 做项目展示时，带 citations 会明显体现这是“检索增强问答”，而不是普通聊天机器人
- 后面做效果评估时，也可以通过 citations 判断检索是否命中了正确片段

一句话讲法：
citations 是 RAG 的“可验证性”来源，没有引用，用户很难信任答案。

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

填入 `OPENAI_API_KEY` 后，可以切到真实 API 模式。

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
    "text": "Redis 是一个基于内存的数据结构存储系统，常用于缓存、消息队列、排行榜和分布式锁。"
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
