# AI Application Competitive Roadmap

这是从最初的 `12 周转向计划` 继续升级出来的竞争力路线图。

目标不是让你“会搭几个 demo”，而是把你训练成：

- 能做 `AI 应用开发`
- 能做 `RAG / Agent / Workflow` 工程
- 能解释关键底层原理
- 能做出 1-2 个真正能拉开差距的项目
- 能在校招 / 实习 / 社招早期竞争里明显区别于“只会调 API”的候选人

## 先说清楚目标边界

这份计划追求的是：

- 从 `后端工程师` 顺滑转到 `AI 应用工程师`
- 在秋招前完成第一轮可投递能力建设
- 在更长周期内补齐从 `应用 -> 系统 -> 模型 -> 推理` 的认知闭环

这份计划不追求的是：

- 短期内把你训练成纯算法研究员
- 把主要时间砸在预训练、分布式训练、论文复现
- 为了“学得深”而牺牲作品产出和求职节奏

一句话：

你的主线是 `应用工程 + 系统工程 + 必要的模型底层理解`，不是去和顶校论文选手硬拼纯研究。

## 你的最终定位

主投方向：

- `AI 应用开发工程师`
- `大模型应用工程师`
- `AI 软件工程师`
- `AI 平台后端`
- `Agent / Workflow 工程师`

你的差异化标签：

- 有真实 `Go` 后端实习经历
- 有服务端工程视角，不只是 prompt 和 API
- 能把模型能力接进系统，做成可上线、可评估、可观测的产品

## 使用方式

- 完成一项就把 `[ ]` 改成 `[x]`
- 每周至少更新一次 `Current Sprint`
- 每个阶段都看 4 件事：
  - 学懂了什么
  - 做出来什么
  - 能讲清什么
  - 哪些还不会
- 不追求机械照表抄课，允许根据秋招节奏调整

## 路线总览

这份路线图分成两层：

### Layer A: 求职冲刺主线

这是你 `现在到秋招前` 必须优先完成的部分。

- `Phase 1`: Python + FastAPI + 最小 LLM 服务
- `Phase 2`: RAG 项目做到简历级
- `Phase 3`: Agent / Workflow 项目做到差异化
- `Phase 4`: 简历、面试、投递、项目包装

### Layer B: 深度补全主线

这是你在完成求职冲刺后继续往深里学的部分。

- `Phase 5`: Eval / Guardrails / Observability
- `Phase 6`: LangChain / LangGraph / LlamaIndex 体系化
- `Phase 7`: Transformer / Embedding / 检索底层
- `Phase 8`: Pretrain / SFT / RLHF / LoRA 认知
- `Phase 9`: Serving / vLLM / KV Cache / Quantization
- `Phase 10`: 系统设计、性能、可靠性、产品化

## 竞争力标准

如果你想在这个方向真正有竞争力，最后不能只停在“会用一些框架”。

你最终至少要同时满足下面这些标准：

### 标准 A：不是只会调用模型

- [ ] 你能手写最小 LLM 服务
- [ ] 你能手写最小 RAG
- [ ] 你能解释工具调用 / Agent 基本原理
- [ ] 你能说清什么时候该自己写、什么时候该用框架

### 标准 B：项目不是 demo，而是工程系统

- [ ] 项目有明确 API 或 workflow 入口
- [ ] 项目有日志、错误处理、配置管理
- [ ] 项目有评测集或效果验证方式
- [ ] 项目能展示失败场景与兜底策略
- [ ] 项目能展示 tradeoff，而不是只有“能跑”

### 标准 C：能解释底层，不会被面试官一问就空

- [ ] 能解释 chunk / embedding / rerank / hybrid retrieval
- [ ] 能解释 Agent / workflow / state / tool schema
- [ ] 能解释 Transformer / attention / KV cache 的工程直觉
- [ ] 能解释 RAG、Prompt、微调、自部署之间的边界

### 标准 D：有真正拉开差距的交付物

- [ ] 至少 1 个“可靠版 RAG”项目
- [ ] 至少 1 个“工程化 Agent / Workflow”项目
- [ ] 每个项目都有 README、架构图、curl 示例、效果说明、简历 bullets
- [ ] 至少 1 个项目有可量化的优化记录

## 项目质量红线

下面这些情况会明显拉低项目含金量：

- [ ] 只有页面或截图，没有后端和接口设计
- [ ] 全程靠框架拼装，自己解释不出底层链路
- [ ] 没有 no-hit / 低相关度拒答
- [ ] 没有 eval，只能说“我感觉效果不错”
- [ ] 没有失败 case、兜底策略、日志、配置管理
- [ ] 不能解释为什么这样设计

## 项目交付物标准

以后你做任何一个主项目，都尽量按这个标准交付。

### Baseline

- [x] 能跑
- [x] 有 README
- [x] 有启动步骤
- [x] 有最小示例请求

### Competitive

- [x] 有架构说明
- [x] 有关键模块拆分
- [x] 有日志 / 错误处理 / 配置项
- [x] 有评测问题集或验证方法
- [x] 有 tradeoff 说明
- [x] 有简历 bullets

### Standout

- [ ] 有优化前后对比表
- [x] 有失败案例与改进记录
- [x] 有 demo 视频或可复现演示链路
- [ ] 有明确的工程化亮点
- [ ] 有一两个“别人一般不会做”的增强点

## 当前状态快照

### 已确认完成

- [x] 已有 `Go` 服务端实习经历
- [x] 已完成 `Python + FastAPI + LLM` 最小服务骨架
- [x] 已拆出 `api / core / schemas / services`
- [x] 已完成 `projects/01-fastapi-minimal-chat`
- [x] 已创建 `projects/02-rag-knowledge-assistant`
- [x] `02` 已打通第一版 RAG 闭环
- [x] `02` 已接入本地 `qdrant`
- [x] `02` 已支持文本入库与问答检索
- [x] `02` 已支持 tags / document_ids 检索范围过滤
- [x] `02` 已支持重复导入去重 / replace 与 failure-case regression
- [x] `02` 已支持多格式本地文件路径 ingest（不再只限 inline text）
- [x] `02` 已支持 query trace 导出与最近决策回看

### 当前最重要缺口

- [ ] `02` 还没到“简历级 / 面试级”
- [ ] `02` 还缺 `PDF / DOCX` 解析、hybrid retrieval、版本管理与更完整观测链路
- [ ] 还没有 `03` Agent / Workflow 项目
- [ ] 还没有形成系统化的 `RAG + Agent + 底层原理` 知识闭环
- [ ] 还没有进入面试表达和投递节奏

## 学习原则

- [ ] `60%` 时间做项目，`20%` 时间补基础，`20%` 时间准备面试
- [ ] 主语言先切到 `Python`，但保留 `Go` 作为差异化标签
- [ ] 先从第一性原理实现，再上框架
- [ ] 先把项目做通，再做优化，再总结原理
- [ ] 任何技术点最终都要能回答：
  - 是什么
  - 解决什么问题
  - 为什么这样设计
  - 不这样做会怎样

## 框架使用策略

### LangChain

定位：

- 作为 `RAG 组件编排` 和快速实验框架
- 适合你在理解原生实现后，对比框架抽象

规则：

- [ ] 不要一开始就把项目完全交给 `LangChain`
- [ ] 先自己写最小版 RAG，再用 `LangChain` 重做一遍关键链路
- [ ] 最终要能回答：`为什么这个地方我愿意用框架，而不是自己写`

### LangGraph

定位：

- 作为 `Agent / Workflow` 主框架
- 重点学习 state、node、edge、checkpointer、human-in-the-loop

规则：

- [ ] `03` 项目优先使用 `LangGraph`
- [ ] 不把 Agent 理解成“多轮聊天 + prompt 拼接”
- [ ] 最终要能回答：`为什么 graph/workflow 比随手 chain 更可控`

### LlamaIndex

定位：

- 作为 `文档 ingest / index / query` 方向的对照框架
- 重点不是全量迁移，而是建立框架认知

规则：

- [ ] 只做最小对照实现
- [ ] 最终要能回答它和 `LangChain` 的侧重点差异

## 核心能力分层

### Level 1: 能做 AI 应用

你至少要做到：

- [ ] 能写 Python 服务
- [ ] 能调用模型
- [ ] 能做最小 RAG
- [ ] 能做基础工具调用
- [ ] 能把一个 AI 功能封装成 API

### Level 2: 能做可靠的 AI 工程

你至少要做到：

- [ ] 会做检索优化
- [ ] 会做 eval
- [ ] 会做日志、追踪、错误处理
- [ ] 会做权限、成本、超时、重试
- [ ] 能解释系统为什么稳定或不稳定

### Level 3: 能解释底层与系统边界

你至少要做到：

- [ ] 理解 Transformer 基本机制
- [ ] 理解 embedding 与向量检索直觉
- [ ] 理解 ANN / HNSW 在解决什么问题
- [ ] 理解 pretrain / SFT / RLHF / DPO 的角色分工
- [ ] 理解推理服务为什么关注 KV cache、batching、quantization

## 核心主路线

### Phase 1: Foundation

目标：

- 把 `Python + FastAPI + 最小 LLM 服务` 跑通
- 开始形成 AI 应用工程的基本骨架

#### Must Build

- [x] `01-fastapi-minimal-chat`
- [x] `/health`
- [x] `/chat`
- [x] `/stream_chat`
- [x] mock / live 两种模式
- [x] 分层结构

#### Must Understand

- [ ] token
- [ ] context window
- [ ] temperature
- [ ] structured output
- [ ] function calling / tool calling

#### Must Explain

- [ ] 为什么 AI 应用主语言通常是 Python
- [ ] 为什么后端背景做 AI 应用有优势
- [ ] 为什么最小服务骨架要先分层

#### Exit Criteria

- [x] 有一个可复用的最小服务模板
- [ ] 能用自己的话讲清 LLM API 调用链路

### Phase 2: RAG V1 -> Competitive RAG

目标：

- 把 `02-rag-knowledge-assistant` 从“能跑”升级为“能写进简历、能扛住面试追问、能和普通 demo 拉开差距”

#### Phase 2A: 先做通闭环

- [x] 文本入库
- [x] chunk 切分
- [x] embedding
- [x] 向量检索
- [x] 生成回答
- [x] 返回 citations
- [x] 返回 retrieved chunks

#### Phase 2B: 补齐工程基本面

- [x] 增加 `GET /documents`
- [x] 支持列出已入库文档元信息
- [x] 为 chunk 参数增加配置与展示
- [x] 增加基础日志
- [x] 增加更清晰的错误分类
- [x] 增加开发 / 测试友好的初始化方式

#### Phase 2C: 补齐 RAG 可靠性

- [x] 增加空白输入校验
- [x] 增加低相关度拒答
- [x] 增加最小化 rerank
- [x] 增加 top_k 与 score 的调试信息
- [x] 增加至少 8-10 条测试问题
- [x] 建立一小份 golden set

#### Phase 2D: 做成简历级项目

- [x] 在 README 里写清架构
- [x] 写清楚为什么先做 RAG 而不是微调
- [x] 写清楚 chunk 的取值权衡
- [x] 写清楚 citations 的价值
- [x] 写清楚优化前后变化
- [x] 输出 2-3 条简历 bullets

#### Phase 2E: 站上竞争力档位

- [x] 增加 metadata filter 或文档标签过滤
- [ ] 尝试 hybrid retrieval 或至少给出设计方案
- [x] 增加文档 replace / 去重策略，并补充更新策略说明
- [x] 增加失败 case 记录
- [x] 输出一份小型 eval / benchmark 结果
- [x] 写出项目中的系统瓶颈和后续优化方向

#### Phase 2F: 从 demo 走向更像真实系统

- [x] 为 ingest 增加去重 / replace 策略，避免重复入库污染检索
- [x] 为 `/ask` 增加 tags / document_ids 过滤，缩小检索范围
- [x] 固化阈值调优记录，说明为什么 `0.25` 比 `0.30` 更合适
- [x] 增加 query trace 导出，便于复盘 `top_k / threshold / score / decision`
- [x] 建立至少 3 个失败 case，并持续做回归验证
- [x] 支持本地文件路径 ingest 与多格式 loader，先把文档输入层做厚一点

#### Phase 2G: 把 RAG 做深，不只做通

这一阶段决定项目是不是还停留在“玩具味道”，重点是把 ingest、retrieval、eval、observability 分层做细。

- [ ] 支持 `PDF / DOCX / HTML` 上传与解析，不只靠手工文本和本地路径
- [ ] 做文档清洗、标题感知 chunking、parent-child retrieval
- [ ] 增加 hybrid retrieval（`BM25 + vector`）与更强 reranker
- [ ] 增加 query rewrite / multi-query / query routing
- [ ] 增加异步 ingest、删除 / 重建索引、版本 / freshness 管理
- [ ] 增加 trace / latency / cost / recall / correctness 观测
- [ ] 做 sentence-level citations、grounding check、hallucination guard

#### Must Understand

- [x] RAG 的基本流程
- [x] chunk size / overlap 的权衡
- [x] embedding 在检索里干什么
- [x] top_k 的作用与副作用
- [x] 为什么要有 citations
- [ ] 为什么要有 no-hit / low-confidence 兜底

#### Must Explain

- [x] 为什么知识库问答优先选 RAG 而不是微调
- [x] 为什么回答错要先看检索而不是先怪模型
- [x] 为什么“检索质量”和“生成质量”要分开看

#### Exit Criteria

- [ ] `02` 达到简历级
- [ ] `02` 能支持你回答 10 个以上常见面试追问
- [ ] `02` 已经有“可靠性 + 评测 + 工程化”三个层面的亮点

### Phase 3: Agent / Workflow

目标：

- 完成一个真正有差异化的 Agent / Workflow 项目，而不是简单的“调用几个工具的聊天机器人”

推荐题目：

- [ ] 日志排障助手
- [ ] 接口文档 Copilot
- [ ] 工单处理助手

推荐优先级：

1. 日志排障助手
2. 接口文档 Copilot
3. 工单处理助手

#### Must Build

- [ ] 新建 `03` 项目
- [ ] 使用 `LangGraph`
- [ ] 至少 2-4 个工具
- [ ] 至少 1 条明确 workflow
- [ ] 至少 1 个失败兜底机制
- [ ] 至少 1 个结构化输出结果
- [ ] 至少 1 个人类介入点或审批点
- [ ] 至少 1 个状态持久化或可恢复执行点
- [ ] 至少 1 个预算 / step limit / timeout 控制
- [ ] 至少 1 个调用轨迹或 trace 记录

#### Must Understand

- [ ] Agent 的本质是 `模型 + 工具 + 状态 + 控制流`
- [ ] ReAct / plan-act-observe 是什么
- [ ] tool schema 为什么重要
- [ ] 为什么 workflow 比纯 prompt chain 更可控
- [ ] 为什么需要 step limit、timeout、retry、budget

#### Must Explain

- [ ] 为什么这个项目比普通 chat bot 更像工程系统
- [ ] 为什么这里用 `LangGraph`
- [ ] 为什么不能无约束地让 Agent 自主规划

#### Exit Criteria

- [ ] 有 1 个明显区别于“只会调 API”选手的项目
- [ ] 能讲清工具调用、状态流转、失败兜底
- [ ] 能讲清为什么这个项目体现了系统设计和工程控制力

### Phase 4: Resume / Interview / Delivery

目标：

- 把已有项目变成真实投递资产，而不是“你自己觉得做过”的学习产物

#### Must Deliver

- [ ] 一版 AI 方向简历
- [ ] 一版投递关键词清单
- [ ] 每个项目的 `30 秒 / 2 分钟 / 5 分钟` 讲法
- [ ] 高频问题答案清单
- [ ] 每周最少 5 道算法题
- [ ] 后端基础回温
- [ ] 每个项目的架构图
- [ ] 每个项目的失败案例与优化总结
- [ ] 每个项目的效果说明或 benchmark 小结

#### Must Understand

- [ ] 项目表达和“真正会做”之间的区别
- [ ] 面试官通常怎么拆穿空心项目
- [ ] 为什么 eval、metrics、tradeoff 很关键

#### Must Explain

- [ ] 为什么你不是“后端转 AI 的新手”
- [ ] 为什么你的项目体现了工程价值
- [ ] 为什么你的路线适合做 AI 应用工程

#### Exit Criteria

- [ ] 可以开始稳定投递
- [ ] 能顶住第一轮 AI 应用岗技术面
- [ ] 项目讲法已经从“做了什么”升级为“为什么这样设计、效果如何、下一步怎么优化”

### Phase 5: Eval / Guardrails / Observability

目标：

- 把“会做项目”升级成“会做可靠 AI 系统”

#### Must Learn

- [ ] 什么是 golden set
- [ ] retrieval eval 和 answer eval 的区别
- [ ] faithfulness / relevance / groundedness 基本概念
- [ ] LLM-as-judge 的优缺点
- [ ] prompt injection / tool misuse / 越权调用风险

#### Must Build

- [ ] 为 `02` 增加最小评测脚本
- [ ] 为 `03` 增加调用轨迹或日志
- [ ] 增加失败 case 记录
- [ ] 增加基本 guardrails

#### Must Explain

- [ ] 为什么 AI 应用不能只靠“我感觉效果还行”
- [ ] 为什么没有 observability 的 Agent 很难维护

### Phase 6: Framework Mastery

目标：

- 建立对主流框架的有边界的理解，而不是跟风背名字

#### LangChain

- [ ] 会用 prompt / retriever / output parser
- [ ] 会用 runnable 或等价抽象组织链路
- [ ] 能回答何时用、何时不用

#### LangGraph

- [ ] 会定义 state
- [ ] 会定义 node / edge
- [ ] 会使用 checkpointer
- [ ] 会设计 human-in-the-loop

#### LlamaIndex

- [ ] 会做最小 ingest + query
- [ ] 能讲清它在文档和索引方向上的优势
- [ ] 能讲清它和 `LangChain` 的差别

#### Exit Criteria

- [ ] 能以“比较视角”看待框架，而不是把框架当魔法

### Phase 7: Retrieval Internals

目标：

- 把 RAG 从“会用”补到“懂底层直觉”

#### Must Learn

- [ ] tokenization 基本直觉
- [ ] embedding 为什么能表达语义相近
- [ ] cosine similarity 是什么
- [ ] ANN 在解决什么问题
- [ ] HNSW 的直觉
- [ ] BM25 的作用
- [ ] hybrid retrieval 为什么常见
- [ ] rerank 的位置与价值

#### Must Explain

- [ ] 为什么向量检索不等于“语义一定正确”
- [ ] 为什么召回和精排要分开看
- [ ] 为什么有时 BM25 和向量检索要一起上

### Phase 8: Model Internals

目标：

- 建立“不做研究也能说清楚”的模型底层认知

#### Must Learn

- [ ] Transformer 基本结构
- [ ] self-attention 在做什么
- [ ] positional information 的基本作用
- [ ] decoder-only 模型的生成直觉
- [ ] KV cache 为什么能提速
- [ ] context window 为什么不是越大越万能

#### Must Explain

- [ ] 为什么模型会 hallucination
- [ ] 为什么长上下文不等于检索能力
- [ ] 为什么 inference cost 会高

## 可选进阶扩展

如果你在核心 24 周后还要继续补得更扎实，可以继续往下走。

### Extension 1: Training Awareness

- [ ] 理解 pretraining 的目标
- [ ] 理解 SFT 在做什么
- [ ] 理解 RLHF / DPO 的角色
- [ ] 理解 LoRA / PEFT 在做什么
- [ ] 理解蒸馏为什么重要
- [ ] 能回答什么时候该微调，什么时候不该

### Extension 2: Serving / Infra Awareness

- [ ] 知道 `vLLM` 是做什么的
- [ ] 知道 continuous batching 的意义
- [ ] 知道 quantization 在换什么
- [ ] 知道吞吐和延迟的 tradeoff
- [ ] 知道托管 API 和自部署的边界
- [ ] 能回答为什么大多数校招应用岗不该把自部署模型当主线

## 知识地图

### A. Python Engineering

- [ ] `venv`
- [ ] 依赖管理
- [ ] `.env`
- [ ] `typing`
- [ ] `dataclass`
- [ ] `pydantic`
- [ ] `async / await`
- [ ] FastAPI 路由与依赖
- [ ] 日志
- [ ] 配置管理
- [ ] Docker

### B. LLM Basics

- [ ] token
- [ ] context window
- [ ] temperature
- [ ] top_p
- [ ] structured output
- [ ] function calling
- [ ] prompt template
- [ ] hallucination
- [ ] cost / latency / throughput

### C. RAG

- [ ] chunk
- [ ] overlap
- [ ] embedding
- [ ] vector store
- [ ] top_k
- [ ] hybrid retrieval
- [ ] rerank
- [ ] citations
- [ ] no-hit
- [ ] eval

### D. Agent

- [ ] tool schema
- [ ] workflow
- [ ] state
- [ ] retry
- [ ] timeout
- [ ] budget
- [ ] human-in-the-loop
- [ ] trace
- [ ] memory

### E. Model / Inference

- [ ] Transformer
- [ ] attention
- [ ] KV cache
- [ ] batching
- [ ] quantization
- [ ] vLLM
- [ ] SFT
- [ ] RLHF / DPO
- [ ] LoRA

## 两个拉开差距的项目

这两个项目不是都必须一开始做完，但最终最好都做。

### Project A: Enterprise Knowledge Copilot

定位：

- 一个真正能体现你 `RAG + 工程化 + Eval` 水平的项目

最低要求：

- [ ] 文档入库
- [ ] chunk 策略可配置
- [ ] citations
- [ ] no-hit 拒答
- [ ] rerank
- [ ] 文档列表与元信息
- [ ] basic eval
- [ ] 日志与错误处理
- [ ] 架构图与 README
- [ ] 优化对比说明

进阶要求：

- [ ] hybrid retrieval
- [ ] 文档版本管理
- [ ] 用户反馈收集
- [ ] query rewrite
- [ ] cache
- [ ] 权限与多租户意识
- [ ] 至少一个真实失败案例分析
- [ ] 至少一个效果评估表

为什么它能拉开差距：

- 这不是“问答 demo”，而是能体现 `检索、评测、可解释性、工程稳定性`

### Project B: Ops / Incident Agent

定位：

- 一个体现你 `Agent + Workflow + 后端系统思维` 的项目

推荐场景：

- [ ] 日志排障助手
- [ ] 告警分析助手
- [ ] 接口文档诊断助手

最低要求：

- [ ] 多工具
- [ ] 状态流转
- [ ] step limit
- [ ] retry / timeout
- [ ] 审批点或人工确认
- [ ] 结构化输出
- [ ] 轨迹记录
- [ ] 架构图与 workflow 图
- [ ] 至少一条失败恢复路径

进阶要求：

- [ ] 只读 SQL 工具
- [ ] 文档检索工具
- [ ] 日志检索工具
- [ ] 成本统计
- [ ] 权限控制
- [ ] 会话持久化
- [ ] 中间状态持久化 / checkpointer
- [ ] 工具调用审计日志

为什么它能拉开差距：

- 它最能体现你从 `Go 后端` 切过来的优势，因为它不是写 prompt，而是在做可控的系统

## 面试表达清单

### `02` 项目必须能回答

- [ ] 为什么优先做 RAG 不做微调
- [ ] chunk 怎么切
- [ ] top_k 怎么选
- [ ] 为什么要 citations
- [ ] 为什么需要低相关度拒答
- [ ] rerank 在哪里起作用
- [ ] 怎么做效果评估

### `03` 项目必须能回答

- [ ] Agent 和普通 chat bot 的区别
- [ ] tool schema 为什么重要
- [ ] 为什么要 workflow
- [ ] 为什么要 timeout / retry / budget
- [ ] 为什么要 human-in-the-loop
- [ ] 为什么这个项目体现了你的工程能力

### 底层必须能回答

- [ ] attention 在干什么
- [ ] embedding 为什么能做检索
- [ ] HNSW 的直觉
- [ ] KV cache 为什么重要
- [ ] SFT 和 RLHF / DPO 的区别
- [ ] LoRA 是怎么在少量参数上适配模型的

## 简历策略

- [ ] 标题写成 `AI 应用开发 / 大模型应用 / AI 软件工程`
- [ ] 强调 `Go 后端 + Python + FastAPI + RAG + Agent`
- [ ] 项目一定写结果，不写“学习了什么”
- [ ] 项目一定写技术关键词
- [ ] 项目一定写 tradeoff 或优化点
- [ ] 项目一定写你的独立设计和工程化思考
- [ ] 项目一定写“可靠性 / 评测 / 观测性 / 成本 / 权限”这类高信号关键词

## 时间分配建议

平时节奏：

- [ ] 工作日每天 `1.5-2` 小时
- [ ] 周末每天 `4-5` 小时

每周固定动作：

- [ ] 代码推进
- [ ] 概念复盘
- [ ] README / 笔记更新
- [ ] 面试题训练
- [ ] 算法训练

## Current Sprint

这一栏只放最近 `1-2 周` 最重要的事，每周更新。

### Sprint Goal

把 `02-rag-knowledge-assistant` 从第一版闭环推进到 `可靠版 RAG`

### This Sprint Checklist

- [x] 为 `AskRequest` 增加空白输入校验
- [x] 为检索结果增加低相关度拒答逻辑
- [x] 为 `/documents/text` 区分客户端错误和服务端错误
- [x] 解决本地 `qdrant` 初始化过早导致的并发占用问题
- [x] 增加 `GET /documents`
- [x] 增加基础日志
- [x] 为 `/health` 与文档入库响应增加 chunk 配置展示
- [x] 为 `02` 增加最小接口测试
- [x] 增加 8-10 条测试问题
- [x] 记录一次优化前后的效果差异
- [x] 为 `/ask` 增加 `status + debug` 调试信息
- [x] 增加本地 golden set 与可复现 eval 脚本
- [x] 产出一份 baseline eval 结果文件
- [x] 为 `/ask` 增加 query trace 导出与最近 trace 查看接口

### Next RAG Deepening Checklist

- [x] 增加 tags / document_ids 过滤，把检索范围收窄到指定文档
- [x] 增加重复导入去重或 replace 机制
- [x] 记录 3 个以上失败 case，并把它们加入回归集
- [x] 输出 2-3 条简历 bullets
- [x] 写一版系统瓶颈与后续优化方向说明
- [ ] 支持 `PDF / DOCX` 解析与浏览器上传
- [ ] 增加 heading-aware / parent-child chunking
- [ ] 尝试 hybrid retrieval（`BM25 + vector`）
- [ ] 增加 query rewrite / multi-query / rerank 模型
- [ ] 增加异步 ingest、删除重建索引、版本与 freshness 机制
- [ ] 增加 trace / latency / cost / recall 观测

### `02` 当前可用简历 Bullets

- 用 `FastAPI + Qdrant` 搭建本地 RAG knowledge assistant，支持文本与多格式本地文件入库、chunk 切分、向量检索、citations 返回与低相关度拒答。
- 为检索链路增加 `tags / document_ids` 范围过滤、重复导入 `replace / reject` 策略与 chunk / score debug 信息，降低脏数据污染和误检索范围。
- 建立本地 eval baseline 与 failure-case regression，沉淀 `10` 条测试问题、`6` 条 golden set、`3` 条 failure cases，用于阈值调优和回归验证。

### `02` 当前系统瓶颈与下一轮优化方向

- 文档输入层：现在已经不只支持 inline text，但还缺 `PDF / DOCX` 解析、浏览器上传、对象存储拉取。
- 文档处理层：chunk 仍以基础切分为主，还没做标题感知、表格保真、parent-child 或语义边界切分。
- 检索层：当前以向量检索加本地 rerank 为主，还缺 `BM25 + vector` hybrid retrieval、query rewrite、learned reranker。
- 质量层：已经有 golden set 和 failure cases，但数据规模还小，citations 还是 chunk 级，还没做更细的 grounding 检查。
- 工程层：还缺异步 ingest pipeline、删除 / 重建索引、版本 / freshness 策略，以及 latency / cost / recall 观测。

## 竞争力检查点

当你阶段性自检时，可以直接看这几个问题。

### 还只是入门

- [ ] 只会调 API
- [ ] 只会用框架
- [ ] 解释不出 retrieval / agent / attention
- [ ] 项目没有评测和失败 case

### 已经具备竞争力

- [ ] 能手写最小 RAG 和最小 Agent
- [ ] 能用框架但不依赖框架
- [x] 项目有评测、观测、失败兜底
- [x] 能讲清 tradeoff 和系统边界

### 明显强于普通候选人

- [ ] 有一个可靠版 RAG 项目
- [ ] 有一个工程化 Agent / Workflow 项目
- [ ] 能解释底层原理和上层工程设计之间的联系
- [ ] 能把项目讲成“问题 -> 设计 -> 取舍 -> 验证 -> 优化”

### Notes

- 日期：
- 本周完成：
- 当前卡点：
- 下周重点：
