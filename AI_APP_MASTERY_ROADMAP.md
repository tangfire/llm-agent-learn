# AI Application Mastery Roadmap

这是一份不按周数、只按能力模块推进的完整路线图。

适用目标：

- 想从后端转到 `AI 应用开发 / 大模型应用开发`
- 不满足于“会调 API”，想把 `应用、框架、RAG、Agent、底层原理、推理系统` 串起来
- 最终做出 1-2 个能拉开差距的项目

这份路线图和 `AI_APP_12_WEEK_PLAN.md` 的关系：

- `AI_APP_12_WEEK_PLAN.md` 更偏当前冲刺和阶段推进
- `AI_APP_MASTERY_ROADMAP.md` 更偏长期完整学习地图

## 怎么使用这份路线图

- 不按几周走，按模块推进
- 每个模块只看 4 件事：
  - 我需要懂什么
  - 我需要亲手做什么
  - 我需要能讲清什么
  - 学到什么程度算过关
- 每完成一项就把 `[ ]` 改成 `[x]`
- 如果求职压力大，优先做 `必修模块`
- 如果你已经会一部分，可以跳过，但必须能讲清楚

## 最终能力目标

学完这份路线图后，你应该能做到：

- [ ] 能独立开发 Python + FastAPI 的 AI 服务
- [ ] 能独立实现并优化 RAG 系统
- [ ] 能独立设计 Agent / Workflow 系统
- [ ] 能解释 LangChain、LangGraph、LlamaIndex 的定位和边界
- [ ] 能解释 RAG、Agent、检索、Embedding、Transformer 的核心原理
- [ ] 能理解微调、推理部署、vLLM、MCP 等扩展方向在整个体系里的位置
- [ ] 能产出 1-2 个真正能区分于普通校招生的项目

## 推荐学习顺序

严格建议的主顺序：

1. `模块 0` 学习方法与工程基线
2. `模块 1` Python 服务工程
3. `模块 2` LLM 应用基础
4. `模块 3` RAG 从零实现
5. `模块 4` RAG 框架与高级玩法
6. `模块 5` Agent 从零理解
7. `模块 6` LangGraph 与工作流系统
8. `模块 7` Eval / Guardrails / Observability
9. `模块 8` 检索底层
10. `模块 9` 模型底层
11. `模块 10` 训练与微调认知
12. `模块 11` 推理与 Serving
13. `模块 12` 现代扩展：MCP / Tooling / Agent 平台化
14. `模块 13` 差异化项目
15. `模块 14` 面试与求职包装

并行建议：

- `模块 8` 和 `模块 9` 可以穿插学
- `模块 10` 和 `模块 11` 不需要太早重投入
- `模块 13` 应该从 `模块 3` 开始就逐步准备，不要等学完再做

## 模块 0：学习方法与工程基线

定位：

- 这是你后面所有学习的基础约束

### 你要建立的习惯

- [ ] 用一个 workspace 持续积累项目
- [ ] 每个项目必须有 README
- [ ] 每次新增能力都要留下 curl / demo / 测试样例
- [ ] 每学完一个概念，都写出自己的解释版本
- [ ] 每周做一次复盘：学了什么、做了什么、哪里还不会

### 你要避免的坑

- [ ] 只看视频不写代码
- [ ] 只会框架，不会第一性原理
- [ ] 只会搭 demo，不会解释设计
- [ ] 只学概念，不做项目沉淀

### 过关标准

- [ ] 你已经有一个稳定的学习工作区
- [ ] 你已经能持续把学习成果沉淀为项目和文档

## 模块 1：Python 服务工程

定位：

- 这是你从 Go 后端切到 AI 应用工程的第一座桥

### 你要懂

- [ ] `venv`
- [ ] `requirements.txt` / 依赖管理
- [ ] `.env` 与配置注入
- [ ] `typing`
- [ ] `dataclass`
- [ ] `pydantic`
- [ ] `async / await`
- [ ] `FastAPI` 路由、请求模型、响应模型、异常处理
- [ ] 基础日志
- [ ] Docker 基础

### 你要做

- [ ] 完成最小 FastAPI 服务骨架
- [ ] 实现普通接口和 SSE 流式接口
- [ ] 支持配置切换和 mock / live 双模式
- [ ] 写出服务 README

### 你要能讲

- [ ] 为什么 AI 应用通常优先用 Python
- [ ] 为什么服务分层重要
- [ ] 为什么 schema 校验很重要

### 过关标准

- [ ] 你能在 1 小时内新起一个可用的 FastAPI AI 服务
- [ ] 你能自己设计 `api / core / schemas / services`

## 模块 2：LLM 应用基础

定位：

- 这是所有上层能力的语言层基础

### 你要懂

- [ ] token
- [ ] context window
- [ ] temperature
- [ ] top_p
- [ ] structured output
- [ ] prompt template
- [ ] function calling / tool calling
- [ ] hallucination
- [ ] latency / cost / throughput 的基本权衡

### 你要做

- [ ] 用 OpenAI SDK 或等价 SDK 完成一次普通对话调用
- [ ] 完成一次 structured output 输出
- [ ] 完成一次 tool calling 最小案例

### 你要能讲

- [ ] 为什么温度不是越低越好
- [ ] 为什么长上下文不等于效果稳定
- [ ] 为什么工具调用比“让模型自己幻想”更可靠

### 过关标准

- [ ] 你能解释一次完整 LLM 请求发生了什么
- [ ] 你能解释常见参数为什么这样配

## 模块 3：RAG 从零实现

定位：

- 这是 AI 应用开发最核心的第一大模块

### 你要懂

- [ ] 什么是 RAG
- [ ] 文档入库流程
- [ ] chunk 的目的
- [ ] embedding 的作用
- [ ] 向量检索在解决什么问题
- [ ] top_k 是什么
- [ ] citations 为什么重要
- [ ] no-hit / low-confidence 为什么必须有

### 你要做

- [ ] 文本入库接口
- [ ] chunk 切分
- [ ] embedding
- [ ] 向量检索
- [ ] 回答生成
- [ ] citations
- [ ] retrieved chunks
- [ ] 空白输入校验
- [ ] 低相关度拒答

### 你要能讲

- [ ] 为什么知识库问答优先做 RAG 不优先做微调
- [ ] 为什么检索错会导致回答错
- [ ] 为什么没有 citations 的 RAG 不够可信

### 过关标准

- [ ] 你能不靠框架手写一个最小 RAG 服务
- [ ] 你能解释每个阶段在干什么

## 模块 4：RAG 框架与高级玩法

定位：

- 这一层不是为了“偷懒”，而是为了建立框架认知和工程效率

### 4A. LangChain

你要懂：

- [ ] LangChain 在解决什么问题
- [ ] prompt / retriever / output parser 的角色
- [ ] runnable 或等价抽象的价值

你要做：

- [ ] 用 LangChain 重做一版最小 RAG 链路
- [ ] 对比“自己写”和“框架写”的差别

你要能讲：

- [ ] 为什么这里用 LangChain
- [ ] 什么地方不适合把所有逻辑都塞给 LangChain

### 4B. LlamaIndex

你要懂：

- [ ] LlamaIndex 为什么更适合文档 ingest / index / query 场景
- [ ] 它和 LangChain 的重心差别

你要做：

- [ ] 用 LlamaIndex 完成最小 ingest + query
- [ ] 对比你自己的 `02` 项目和 LlamaIndex 的抽象方式

你要能讲：

- [ ] LangChain 和 LlamaIndex 不是互斥关系
- [ ] 什么时候你会优先用 LlamaIndex

### 4C. RAG 高级话题

- [ ] rerank
- [ ] hybrid retrieval
- [ ] query rewrite
- [ ] multi-query retrieval
- [ ] metadata filtering
- [ ] 文档版本管理
- [ ] 基本 eval

### 过关标准

- [ ] 你能自己写 RAG
- [ ] 你也能说清三个主流 RAG 路线的边界：手写 / LangChain / LlamaIndex

## 模块 5：Agent 从零理解

定位：

- 不先理解 Agent 的本质，直接上框架很容易学偏

### 你要懂

- [ ] Agent 的本质是 `模型 + 工具 + 状态 + 控制流`
- [ ] ReAct / plan-act-observe 的基本思路
- [ ] tool schema 为什么重要
- [ ] memory 该放在哪里
- [ ] 为什么要有 step limit
- [ ] 为什么要有 timeout / retry / budget

### 你要做

- [ ] 做一个最小工具调用 Agent
- [ ] 至少接 2 个工具
- [ ] 至少有一次失败兜底
- [ ] 至少有一次结构化输出

### 你要能讲

- [ ] Agent 和普通聊天机器人有什么本质区别
- [ ] 为什么 Agent 不能完全放飞自主规划
- [ ] 为什么工程上更强调“可控”，而不是“看起来聪明”

### 过关标准

- [ ] 你能不用框架讲清 Agent 是怎么跑起来的

## 模块 6：LangGraph 与工作流系统

定位：

- 这是你后面做差异化 Agent 项目的主武器

### 你要懂

- [ ] LangGraph 是低层工作流 / agent orchestration 框架
- [ ] state、node、edge 分别在做什么
- [ ] checkpointer 的意义
- [ ] interrupt / human-in-the-loop 的意义
- [ ] 为什么 graph 比 prompt chain 更适合复杂系统

### 你要做

- [ ] 用 LangGraph 跑通一个最小 workflow
- [ ] 加入工具调用
- [ ] 加入状态流转
- [ ] 加入失败兜底
- [ ] 加入人工确认点

### 你要能讲

- [ ] 为什么 LangGraph 比直接手搓 while loop 更适合复杂 Agent
- [ ] 为什么 LangGraph 适合做多步、可追踪、可恢复的流程

### 过关标准

- [ ] 你能用 LangGraph 独立写一个业务型 Agent 工作流

## 模块 7：Eval / Guardrails / Observability

定位：

- 这是“工程 demo”和“靠谱 AI 系统”的分水岭

### 你要懂

- [ ] golden set
- [ ] retrieval eval 和 answer eval 的区别
- [ ] faithfulness / relevance / groundedness 基本概念
- [ ] LLM-as-judge 的优缺点
- [ ] prompt injection
- [ ] tool misuse
- [ ] 最小 guardrails 是什么

### 你要做

- [ ] 给 RAG 项目建立一个最小评测集
- [ ] 给 Agent 项目记录调用轨迹
- [ ] 记录失败 case
- [ ] 为关键工具增加权限边界

### 你要能讲

- [ ] 为什么 AI 应用不能只靠人工主观试用
- [ ] 为什么 observability 对 Agent 很重要

### 过关标准

- [ ] 你的项目开始具备“可评估、可追踪、可复盘”的能力

## 模块 8：检索底层

定位：

- 这是你把 RAG 从“会搭”升级到“真懂”的关键

### 你要懂

- [ ] tokenization 的基本直觉
- [ ] embedding 为什么能表达语义相近
- [ ] cosine similarity 是什么
- [ ] ANN 在解决什么问题
- [ ] HNSW 的直觉
- [ ] BM25 的作用
- [ ] 为什么 hybrid retrieval 常见
- [ ] rerank 的位置与价值

### 你要做

- [ ] 写一份自己的检索原理笔记
- [ ] 对比向量检索和 BM25 的适用场景
- [ ] 在项目里至少实现一次 rerank 或 hybrid 思考

### 你要能讲

- [ ] 为什么向量检索不等于一定检索正确
- [ ] 为什么召回和精排要分开理解
- [ ] 为什么“检索质量”和“生成质量”要分开调

### 过关标准

- [ ] 你能把 RAG 的底层逻辑讲到面试官觉得你不是只会调包

## 模块 9：模型底层

定位：

- 目标不是做研究，而是建立足够深的第一性原理认知

### 你要懂

- [ ] Transformer 基本结构
- [ ] self-attention 在做什么
- [ ] positional information 的作用
- [ ] decoder-only 模型为什么适合生成
- [ ] KV cache 为什么提速
- [ ] context window 为什么不是越大越万能

### 你要做

- [ ] 写一份自己的 Transformer 解释笔记
- [ ] 能画出一版简化的“输入 -> token -> attention -> 生成”流程图

### 你要能讲

- [ ] 为什么模型会 hallucination
- [ ] 为什么长上下文不等于检索
- [ ] 为什么推理成本高

### 过关标准

- [ ] 你能把模型底层解释到“工程同学听得懂、算法同学也不会嫌太浅”

## 模块 10：训练与微调认知

定位：

- 这一层是“必须懂边界”，不是“必须亲自炼大模型”

### 你要懂

- [ ] pretraining 是什么
- [ ] SFT 在做什么
- [ ] RLHF / DPO 大致在做什么
- [ ] LoRA / PEFT 在做什么
- [ ] 蒸馏为什么重要
- [ ] 什么时候该微调
- [ ] 什么时候不该微调

### 你要做

- [ ] 写一份“RAG、Prompt、微调”的选择指南
- [ ] 能结合业务场景说出为什么选 RAG 或微调

### 你要能讲

- [ ] 为什么知识更新类场景通常不先微调
- [ ] 为什么风格约束 / 格式约束 / 任务习惯有时适合微调

### 过关标准

- [ ] 你不会把所有问题都回答成“微调一下就行”

## 模块 11：推理与 Serving

定位：

- 这层让你知道“模型是怎么跑起来的”，但不要求你一开始就自己部署一套大服务

### 你要懂

- [ ] 在线推理和离线推理的区别
- [ ] batching 在做什么
- [ ] continuous batching 的意义
- [ ] quantization 在换什么
- [ ] KV cache 和显存的关系
- [ ] 吞吐和延迟的 tradeoff
- [ ] 为什么 `vLLM` 常被提起
- [ ] 托管 API 和自部署的边界

### 你要做

- [ ] 会解释 `vLLM` 是高吞吐推理服务框架
- [ ] 知道 OpenAI-compatible serving 是什么意思
- [ ] 知道什么时候该直接用 API，什么时候才考虑自部署

### 你要能讲

- [ ] 为什么校招应用岗不应该把“自己部署大模型”当主线
- [ ] 为什么推理系统关注 KV cache、batching、并发

### 过关标准

- [ ] 你能把 Serving 讲到“知道边界、知道价值、知道何时该用”

## 模块 12：现代扩展与最新应用工程话题

定位：

- 这一层是近两年 AI 应用工程里明显越来越重要的东西

### 你要懂

- [ ] MCP 是什么
- [ ] Remote MCP 和普通 function calling 的关系
- [ ] file search / vector store / tool use 的关系
- [ ] structured output 为什么越来越重要
- [ ] model routing 是什么
- [ ] prompt caching / response caching 的价值
- [ ] 多 Agent 为什么不一定比单 Agent 更好

### 你要做

- [ ] 至少做一次 tool calling + structured output 的组合案例
- [ ] 至少理解一次 MCP server 的基本思路
- [ ] 至少在设计层面思考 model routing 和缓存

### 你要能讲

- [ ] MCP 解决的是工具和上下文接入的标准化问题
- [ ] 为什么“更多 Agent”不等于“更高级”
- [ ] 为什么工程上越来越强调工具接入、评估、可观测性

### 过关标准

- [ ] 你对“最新应用工程方向”有体系认知，而不是只听过几个新词

## 模块 13：两个拉开差距的项目

### 项目 A：Enterprise Knowledge Copilot

目标：

- 做出一个真正像企业级知识助手的 RAG 系统

最低要求：

- [ ] 文档入库
- [ ] chunk 配置
- [ ] citations
- [ ] no-hit 拒答
- [ ] rerank
- [ ] 文档列表与元信息
- [ ] basic eval
- [ ] 日志与错误处理

进阶要求：

- [ ] hybrid retrieval
- [ ] metadata filtering
- [ ] query rewrite
- [ ] cache
- [ ] 用户反馈收集
- [ ] 多租户意识

为什么它能拉开差距：

- [ ] 它展示的是 `RAG + Eval + 工程质量`，不是普通问答 demo

### 项目 B：Ops / Incident Agent

目标：

- 做一个能体现你后端系统思维的 Agent 系统

推荐场景：

- [ ] 日志排障助手
- [ ] 告警分析助手
- [ ] 接口文档诊断助手

最低要求：

- [ ] 多工具
- [ ] 工作流
- [ ] step limit
- [ ] retry / timeout
- [ ] 人工确认
- [ ] 结构化输出
- [ ] 轨迹记录

进阶要求：

- [ ] SQL 只读工具
- [ ] 文档检索工具
- [ ] 日志检索工具
- [ ] 成本统计
- [ ] 权限控制
- [ ] 会话持久化

为什么它能拉开差距：

- [ ] 它最能体现你从 Go 后端转过来的工程优势

## 模块 14：面试与求职包装

定位：

- 这是把技术资产变成 offer 资产的最后一环

### 你要准备

- [ ] AI 方向简历标题
- [ ] 每个项目的 30 秒、2 分钟、5 分钟讲法
- [ ] 高频 RAG 问题答案
- [ ] 高频 Agent 问题答案
- [ ] 高频后端基础题
- [ ] 每周算法训练

### 你要能讲

- [ ] 为什么你不是“后端转 AI 的新手”
- [ ] 为什么你的项目体现工程能力
- [ ] 为什么你适合 AI 应用工程岗

### 过关标准

- [ ] 你已经能稳定投递 AI 应用 / Agent / AI 平台 / AI 软件工程相关岗位

## 必修模块与选修模块

### 必修

- [ ] 模块 1
- [ ] 模块 2
- [ ] 模块 3
- [ ] 模块 5
- [ ] 模块 6
- [ ] 模块 7
- [ ] 模块 8
- [ ] 模块 9
- [ ] 模块 13
- [ ] 模块 14

### 强烈建议

- [ ] 模块 4
- [ ] 模块 10
- [ ] 模块 11
- [ ] 模块 12

## 官方资料入口

这些是我建议你优先看的官方入口，后面学具体模块时再逐步深入。

- [ ] FastAPI 官方教程: https://fastapi.tiangolo.com/tutorial/
- [ ] LangChain 官方概览: https://docs.langchain.com/oss/python/langchain/overview
- [ ] LangGraph 官方概览: https://docs.langchain.com/oss/python/langgraph/overview
- [ ] LlamaIndex 官方文档: https://docs.llamaindex.ai/
- [ ] OpenAI Tools 官方文档: https://platform.openai.com/docs/guides/tools/tool-choice
- [ ] OpenAI Agents 官方文档: https://platform.openai.com/docs/guides/agents/agent-builder
- [ ] vLLM 官方文档: https://docs.vllm.ai/
- [ ] MCP 官方介绍: https://modelcontextprotocol.io/

## 你当前最适合的推进顺序

结合你现在的进度，建议你按下面的顺序继续：

1. [ ] 继续把 `02-rag-knowledge-assistant` 修成可靠版 RAG
2. [ ] 在修 `02` 的过程中同步补完模块 3
3. [ ] 再开始模块 5 和模块 6，启动 `03` Agent 项目
4. [ ] 然后穿插学模块 8 和模块 9
5. [ ] 最后补模块 10、11、12，把认知闭环补全

## 当前建议

你现在不要再扩散学习面了，下一步最值钱的动作依旧是：

- [ ] 继续完善 `02`
- [ ] 通过 `02` 学透 RAG
- [ ] 在修 bug 和补能力时把“为什么这样设计”写进 README
