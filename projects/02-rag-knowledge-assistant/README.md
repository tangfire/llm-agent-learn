# 02 RAG Knowledge Assistant

第 2 个学习项目，目标是从最小 FastAPI 模板进入 RAG 闭环。

## 当前完成的范围

- 复用 `01-fastapi-minimal-chat` 的工程骨架
- 文本入库
- 本地文件路径入库，支持多种常见文本格式
- chunk 切分
- embedding
- qdrant 本地向量检索
- 基于检索结果生成回答
- 返回 citations 与 retrieved_chunks
- `GET /documents` 文档元信息列表
- `/ask` 支持 `tags` / `document_ids` 检索范围过滤
- ingest 去重 / replace 策略
- query trace 导出与最近决策回看
- chunk 参数配置化与接口展示
- 基础日志、错误分类、lifespan 初始化
- 低相关度拒答
- `status + debug` 检索调试信息
- `8-10` 条测试问题、golden set、failure cases、可复现本地 eval

## 当前说明

今天这版已经从“能跑的 RAG V1”推进到了 `Phase 2F` 的第一轮 hardening，更接近一个“可控、可回归、可继续扩展”的小型 RAG。

- `POST /documents/text`：接收 inline text，支持 `ingest_strategy`，切分 chunk 并写入本地 qdrant
- `POST /documents/file-path`：从本地文件路径读取内容，做格式归一化后再入库
- `GET /documents`：聚合已入库文档的元信息，返回文档数、标签、`source_type`、chunk 数、字符数、入库时间
- `POST /ask`：对问题生成 query embedding，支持 `tags` / `document_ids` 过滤，再返回 `answer`、`citations`、`retrieved_chunks`
- `/ask` 增加 `status`，并支持通过 `return_debug=true` 返回检索调试信息和过滤范围
- 每次 `/ask` 都会落一条 query trace，本地可通过 `GET /traces` 回看最近决策
- 当 top1 score 低于阈值时会触发低相关度拒答，不再强行回答
- 重复导入时可以选择 `keep_both`、`reject_duplicate`、`replace_existing`
- `/health` 和 `/documents/text` 会展示当前生效的 `chunk_size` / `chunk_overlap`
- 启动改成 `lifespan + app factory`，避免 import 时过早初始化本地 qdrant
- 加了基础请求日志与更清晰的错误分类，便于排障和测试
- 已把失败 case 纳入本地 eval 和 hardening regression，不再只看“能不能答对”
- 配置了 `OPENAI_API_KEY` 时，embedding 走 OpenAI API，answer 走 OpenAI Responses API
- 没有配置 key 时，embedding 走本地 hash fallback，answer 走本地 fallback

## RAG 流程

```text
POST /documents/text or /documents/file-path
  -> loader / normalize
  -> duplicate check (source / content sha256)
  -> ingest strategy (keep_both / reject_duplicate / replace_existing)
  -> chunker
  -> embeddings
  -> qdrant local upsert

POST /ask
  -> question embedding
  -> qdrant vector search (+ optional document_ids / tags filter)
  -> rerank / top_k crop
  -> answered / no_hit / low_confidence decision
  -> query trace export
  -> LLM answer
  -> citations + retrieved_chunks + debug
```

## Phase 2B 这次补了什么

### 1. 文档列表与元信息

现在不只是“把 chunk 塞进向量库”，而是能通过 `GET /documents` 看见已经入库了哪些文档。

- 每个文档会聚合 `document_id`、`title`、`source`、`source_type`、`tags`
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

## Phase 2C 这次补了什么

### 1. 低相关度拒答

现在 `/ask` 不会再默认“检到一点东西就回答”，而是会先看最相关 chunk 的 score。

- 当前默认阈值是 `LOW_CONFIDENCE_SCORE_THRESHOLD=0.25`
- 如果 top1 score 低于阈值，就返回 `status=low_confidence`
- 这时 `citations` 会清空，避免把不靠谱的命中结果包装成“有依据的答案”

这一步的价值是：

- 避免模型基于噪声上下文硬编答案
- 让系统从“像是会答”变成“知道什么时候不该答”

### 2. `status + debug` 调试信息

`/ask` 现在多了一层显式决策信息：

- `status=answered`：正常回答
- `status=no_hit`：知识库里没有命中内容
- `status=low_confidence`：有召回，但相关度不够高

如果请求里带上 `return_debug=true`，还会返回：

- `requested_top_k`
- `candidate_limit`
- `best_score`
- `low_confidence_score_threshold`
- `decision`
- `rejection_reason`

这一步的价值是：

- 你可以更快判断是 `top_k`、阈值还是文档质量出了问题
- 后面做阈值调优、rerank 对比、失败 case 复盘时更方便

### 3. 测试问题、golden set 和本地 eval

现在仓库里已经有一套可复现的最小评测资产：

- `eval/fixtures/sample_documents.json`
- `eval/test_questions.json`
- `eval/golden_set.json`
- `scripts/run_local_eval.py`
- `eval/results/local_eval_baseline.json`

这一步的价值是：

- 不再只靠“我感觉效果还行”
- 你可以在改 chunk、阈值、rerank 后快速回归
- 这已经开始接近真正工程项目里的最小 eval 闭环

### 4. 一次真实的阈值调优记录

这版不是拍脑袋把拒答阈值写死，而是做过一轮很小但真实的调优。

- 之前阈值设为 `0.30` 时，问题“Redis 常见应用场景有哪些？”会被误拒，`best_score=0.2778`
- 调到 `0.25` 之后，这个 Redis 问题能正常回答
- 同时无关问题“怎么烤一个戚风蛋糕？”的 `best_score=0.2193`，依然会被拒答

这说明阈值调优不是越高越好，而是要在“减少误答”和“减少误拒”之间找平衡。

## Phase 2F 这次补了什么

### 1. `/ask` 支持 `tags / document_ids` 过滤

现在问答接口不再只能“全库检索”，而是可以显式缩小检索范围。

- `document_ids`：只在指定文档里检索
- `tags`：只在命中指定标签的文档里检索
- `return_debug=true` 时会回传 `filtered_document_ids` 和 `filtered_tags`

这一步的价值是：

- 可以模拟真实知识库里的“租户隔离 / 资料域隔离 / 指定文档问答”
- 当回答不准时，能更清楚地区分是“范围给错了”还是“召回质量不够”

### 2. ingest 去重 / replace 策略

现在重复导入不再默认把脏数据一层层堆进库里，而是先做冲突判断。

- 冲突依据：相同 `source` 或相同内容的 `content_sha256`
- `keep_both`：都保留
- `reject_duplicate`：直接拒绝重复导入
- `replace_existing`：先删旧文档再写新文档
- 响应会回传 `dedupe_action` 和 `ingest_strategy`

这一步的价值是：

- 避免重复 chunk 污染检索结果
- 让“重传同一份资料”从危险操作变成可控操作

### 3. 不再只支持 inline text，已经补了多格式本地文件导入

为了先把 ingest 做实，这版增加了 `POST /documents/file-path`。

- 当前支持：`.txt`、`.md`、`.markdown`、`.log`、`.yaml`、`.yml`
- 也支持：`.json`、`.jsonl`、`.csv`、`.html`、`.htm`
- loader 会把 `json / jsonl / csv / html` 归一化成更适合 chunk 的纯文本
- 返回结果里会带 `source_type`，例如 `file:.csv`

这一步的价值是：

- 项目已经不再局限于“只能手动贴一段文本”
- 你开始接触真实 RAG 里很重要的一层：文档加载和清洗

### 4. failure cases 被纳入回归，而不只是口头说明

这版增加了明确的失败样例和 hardening regression。

- `eval/failure_cases.json` 里记录了至少 `3` 个失败 case
- `scripts/run_local_eval.py` 会同时跑测试问题、golden set、failure cases
- `tests/test_hardening.py` 覆盖了过滤检索、replace、reject duplicate、CSV file-path ingest

这一步的价值是：

- 不只是“答对几个例子”，也能验证“错的时候怎么错”
- 以后改 chunk、阈值、rerank、loader 时有最小回归底座

### 5. query trace export，不再只靠日志猜问题

现在每次 `/ask` 的关键决策都会落到本地 trace 文件里。

- 记录字段包括问题、过滤条件、`top_k`、`best_score`、决策状态、拒答原因、citations
- `return_debug=true` 时，响应里的 `debug.trace_id` 可以和 trace 记录对上
- 新增 `GET /traces?limit=20`，可以回看最近几次检索决策

这一步的价值是：

- 出现误答、误拒或过滤范围问题时，不再只能翻日志猜测
- 后面做阈值调优、loader 对比、rerank 实验时更容易复盘

### 6. 当前边界也要讲清楚

这版已经比最小 demo 扎实很多，但它还不是完整生产级 RAG。

- 还没有浏览器 multipart 上传
- 还没有 `PDF / DOCX` 解析器
- 还没有异步 ingest pipeline、删除重建索引、版本管理
- 还没有 hybrid retrieval、真正的 reranker、query rewrite
- citations 还是 chunk 级，还没做到句子级 grounding

这正好也是下一轮最值得补的方向。

## 当前接口

- `GET /health`
- `GET /documents`
- `GET /traces`
- `POST /documents/text`
- `POST /documents/file-path`
- `POST /ask`

## 关键模块拆分

- `app/main.py`：应用工厂、lifespan 初始化、HTTP 日志
- `app/api/routes.py`：接口层，只负责接请求和调 service
- `app/services/rag.py`：RAG 主流程，负责 ingest / retrieve / answer
- `app/services/vector_store.py`：qdrant 适配与文档元信息聚合
- `app/services/document_loader.py`：本地文件读取、格式归一化与基础清洗
- `app/services/query_trace.py`：本地 query trace 导出与最近记录读取
- `app/services/chunker.py`：chunk 切分策略
- `app/core/config.py`：配置管理
- `app/core/errors.py`：统一错误分类与响应
- `eval/`：样例知识库、测试问题、golden set、baseline 结果
- `eval/failure_cases.json`：失败 case 回归集
- `scripts/run_local_eval.py`：本地可复现评测脚本
- `tests/test_hardening.py`：Phase 2F hardening 回归测试

## 架构说明

```text
client
  -> FastAPI router
  -> RAGService
      -> LocalDocumentLoader
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
- `LOW_CONFIDENCE_SCORE_THRESHOLD`：低相关度拒答阈值，默认 `0.25`
- `QUERY_TRACE_PATH`：本地 query trace 导出文件路径

## 当前文档加载能力

当前项目支持两种 ingest 入口：

- `POST /documents/text`：直接传文本
- `POST /documents/file-path`：传本地绝对路径或相对路径，由服务端读取文件

当前 `file-path` loader 支持：

- `txt / md / markdown / log / yaml / yml`
- `json / jsonl / csv / html / htm`

这里故意先做 `file-path ingest`，而不是直接上浏览器上传，有两个工程上的考虑：

- 当前依赖里还没有 `python-multipart`，先把 ingest 核心链路做扎实更划算
- 先解决“文档怎么加载、怎么清洗、怎么去重”的核心问题，再加 HTTP upload 只是接口形态扩展

当前仍不支持：

- `PDF / DOCX` 解析
- 对象存储下载
- 浏览器表单上传

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
- 已补一组最小接口测试，覆盖 `/health`、`/documents`、空白问题校验、低相关度拒答
- 已补 hardening 回归，覆盖过滤检索、去重 / replace、拒绝重复导入、CSV file-path ingest
- 已补 query trace 回归，验证 `/ask -> trace_id -> /traces` 这一条可复盘链路
- 已补本地 eval 脚本，可以把 fixture 文档、golden set、failure cases 跑成基线结果

运行测试：

```bash
cd /Users/firetang/Documents/llm/projects/02-rag-knowledge-assistant
source .venv/bin/activate
python -m unittest discover -s tests -v
```

运行本地 eval：

```bash
cd /Users/firetang/Documents/llm/projects/02-rag-knowledge-assistant
source .venv/bin/activate
python scripts/run_local_eval.py --output eval/results/local_eval_baseline.json
```

当前 baseline：

- `10` 条测试问题
- `6` 条 golden set
- `3` 条 failure cases
- `unittest` 当前 `11/11` 通过
- 本地 baseline 结果：golden set `6/6` 通过，failure cases `3/3` 通过

## Curl

```bash
curl http://127.0.0.1:8001/health
```

```bash
curl http://127.0.0.1:8001/documents
```

```bash
curl "http://127.0.0.1:8001/traces?limit=5"
```

```bash
curl -X POST http://127.0.0.1:8001/documents/text \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Redis Notes",
    "source": "redis-notes.md",
    "tags": ["cache", "infra"],
    "ingest_strategy": "replace_existing",
    "text": "Redis 是一个基于内存的数据结构存储系统，常用于缓存、消息队列、排行榜和分布式锁。"
  }'
```

```bash
curl -X POST http://127.0.0.1:8001/documents/file-path \
  -H "Content-Type: application/json" \
  -d '{
    "path": "/absolute/path/to/knowledge.csv",
    "tags": ["table", "kb"],
    "ingest_strategy": "replace_existing"
  }'
```

```bash
curl -X POST http://127.0.0.1:8001/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Qdrant 支持什么过滤能力？",
    "top_k": 3,
    "tags": ["table"],
    "return_debug": true
  }'
```

返回的 `debug.trace_id` 可以再拿去和 `/traces` 里的最近记录对照。

```bash
curl -X POST http://127.0.0.1:8001/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "这份文档主要讲了什么？",
    "document_ids": ["doc_xxxxxxxxxxxx"],
    "return_debug": true
  }'
```
