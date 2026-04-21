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
- `GET /documents` 文档元信息列表
- chunk 参数配置化与接口展示
- 基础日志、错误分类、lifespan 初始化

## 当前说明

今天这版已经从“能跑的 RAG V1”推进到了“Phase 2B 工程化版”。

- `POST /documents/text`：接收文本，切分 chunk，生成 embedding，并写入本地 qdrant
- `GET /documents`：聚合已入库文档的元信息，返回文档数、标签、chunk 数、字符数、入库时间
- `POST /ask`：对问题生成 query embedding，做向量检索，再返回 `answer`、`citations`、`retrieved_chunks`
- `/health` 和 `/documents/text` 会展示当前生效的 `chunk_size` / `chunk_overlap`
- 启动改成 `lifespan + app factory`，避免 import 时过早初始化本地 qdrant
- 加了基础请求日志与更清晰的错误分类，便于排障和测试
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

## Phase 2B 这次补了什么

### 1. 文档列表与元信息

现在不只是“把 chunk 塞进向量库”，而是能通过 `GET /documents` 看见已经入库了哪些文档。

- 每个文档会聚合 `document_id`、`title`、`source`、`tags`
- 会返回 `chunk_count` 和 `total_char_count`
- 会记录 `ingested_at`

这一步的价值是：

- 你终于能回答“现在库里到底有什么”
- 后面做 metadata filter、版本管理、eval 时都有基础
- 面试里可以证明你不是只做了一个黑盒检索 demo

### 2. chunk 参数不再只是藏在配置里

以前虽然已经有 `CHUNK_SIZE` 和 `CHUNK_OVERLAP`，但外部看不出来当前服务到底按什么参数在工作。

现在：

- `chunk_size` / `chunk_overlap` 仍然由 `.env` 控制
- `/health` 会直接返回当前 chunk 配置
- `/documents/text` 的响应也会返回本次服务生效的 chunk 配置

这一步的价值是：

- 调参时更容易定位“现在到底跑的是哪套参数”
- 后面写 README 里的 tradeoff 和优化对比会更顺

### 3. 初始化、日志、错误分类更工程化

这一版把最容易在本地开发里踩的坑也顺手补上了。

- 用 `create_app()` + `lifespan` 初始化 `RAGService`
- 避免 import 模块时就抢先打开本地 qdrant
- 加了请求级日志，能看到方法、路径、状态码、耗时
- 增加了统一错误响应结构，区分客户端输入、存储层、上游模型调用等问题

这一步的价值是：

- 本地开发和测试更稳定
- 失败时更容易知道是“我参数错了”“向量库坏了”还是“模型调用失败了”

## 当前接口

- `GET /health`
- `GET /documents`
- `POST /documents/text`
- `POST /ask`

## 关键模块拆分

- `app/main.py`：应用工厂、lifespan 初始化、HTTP 日志
- `app/api/routes.py`：接口层，只负责接请求和调 service
- `app/services/rag.py`：RAG 主流程，负责 ingest / retrieve / answer
- `app/services/vector_store.py`：qdrant 适配与文档元信息聚合
- `app/services/chunker.py`：chunk 切分策略
- `app/core/config.py`：配置管理
- `app/core/errors.py`：统一错误分类与响应

## 架构说明

```text
client
  -> FastAPI router
  -> RAGService
      -> TextChunker
      -> Embedding (OpenAI or local hash)
      -> QdrantVectorStore
      -> Answer generation (OpenAI or local fallback)
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

## 再补 5 个 Phase 2 面试常见点

### 1. chunk size / overlap 怎么权衡

- `chunk_size` 太小：语义上下文不够，检索可能只命中碎片信息
- `chunk_size` 太大：不同主题混在一起，召回会变钝，还会抬高 prompt 成本
- `chunk_overlap` 太小：上下文衔接可能断掉
- `chunk_overlap` 太大：会带来重复内容、增加索引体积

现在这版默认值是：

- `CHUNK_SIZE=500`
- `CHUNK_OVERLAP=100`

这是一组偏保守、适合入门验证的参数：既保证 chunk 不会过碎，又给相邻内容留一点重叠。

### 2. embedding 在检索里干什么

embedding 的作用是把文本映射成向量，让“语义相近”的内容在向量空间里更接近。

- 文档 chunk 先转成向量并入库
- 用户问题也会转成 query 向量
- 检索阶段本质是在向量空间里找“谁和这个问题更近”

所以 embedding 不是直接回答问题，而是负责把“可能相关的上下文”先找出来。

### 3. top_k 的作用和副作用

- `top_k` 太小：可能漏掉关键证据
- `top_k` 太大：可能把噪声一起塞给模型，反而降低回答稳定性

所以 `top_k` 不是越大越好，而是在“召回更多候选”和“减少噪声干扰”之间找平衡。

### 4. 为什么回答错先看检索，不先怪模型

RAG 的错误通常分两段：

1. 没检到对的内容
2. 检到了，但模型没用好

如果第一段就错了，模型再强也只能基于错误上下文作答。所以排查顺序通常是：

- 先看 `retrieved_chunks` 命中的内容对不对
- 再看 `score`、`top_k`、chunk 配置是否合理
- 最后才看生成提示词和回答模型

### 5. 为什么“检索质量”和“生成质量”要分开看

- 检索质量关注：有没有把真正相关的 chunk 找回来
- 生成质量关注：模型有没有忠实、清楚地利用这些 chunk 回答

这两个问题混在一起看，就很难定位系统到底是“召回差”还是“生成差”。

一句话讲法：
RAG 不是一个黑盒，它至少有“检索”和“生成”两层，所以调优也要分层看。

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

关键配置：

- `LOG_LEVEL`：日志级别，默认 `INFO`
- `CHUNK_SIZE`：chunk 大小
- `CHUNK_OVERLAP`：chunk 重叠长度

## 错误分类

当前接口会尽量把错误归到更清晰的类别：

- 客户端输入问题：返回 `400` 或 `422`
- 向量库存取问题：返回 `503`
- OpenAI 调用问题：返回 `502`
- 其他未预期问题：返回 `500`

统一错误结构示例：

```json
{
  "error": {
    "code": "vector_store_upsert_failed",
    "message": "Failed to persist document chunks into qdrant."
  }
}
```

## 为什么这版更适合开发和测试

- 服务实例不再在 import 阶段创建，而是在 app 启动时创建
- `create_app(settings)` 可以在测试里传入临时 `qdrant_path`
- 已补一组最小接口测试，覆盖 `/health`、`/documents`、空白问题校验

运行测试：

```bash
cd /Users/firetang/Documents/llm/projects/02-rag-knowledge-assistant
source .venv/bin/activate
python -m unittest discover -s tests -v
```

## Curl

```bash
curl http://127.0.0.1:8001/health
```

```bash
curl http://127.0.0.1:8001/documents
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
