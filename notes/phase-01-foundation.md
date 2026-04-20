# Phase 01 Foundation Notes

这份笔记专门对应 `AI_APP_12_WEEK_PLAN.md` 里 `Phase 1: Foundation` 还没打钩的内容。

目标不是“再看一遍概念”，而是让你能够：

- 自己讲明白核心术语
- 结合 `01-fastapi-minimal-chat` 解释设计
- 达到阶段一的 `Must Understand / Must Explain / Exit Criteria`

## 对应未打钩项

### Must Understand

- `token`
- `context window`
- `temperature`
- `structured output`
- `function calling / tool calling`

### Must Explain

- 为什么 AI 应用主语言通常是 Python
- 为什么后端背景做 AI 应用有优势
- 为什么最小服务骨架要先分层

### Exit Criteria

- 能用自己的话讲清 LLM API 调用链路

## 1. Token

### 是什么

`token` 不是“一个单词”，而是模型处理文本时使用的更小单位。英文里可能接近单词或词片段，中文里常常一个字就是一个 token，但不绝对。

### 为什么重要

- 模型的输入和输出成本通常按 token 计费
- 模型一次能处理多少内容，取决于 token 数，而不是字符数
- prompt 太长、检索内容太多，最终都会变成 token 压力

### 在项目里怎么理解

做 RAG 时，你不是在和“字符数”打交道，而是在和“token 预算”打交道。`chunk`、`top_k`、上下文拼接，本质上都在争抢 context window。

### 一句话讲法

token 是模型读写文本时的基本计量单位，成本、长度限制和上下文设计最后都要落到 token 上。

## 2. Context Window

### 是什么

`context window` 是模型单次请求里最多能看到的上下文总长度，包括：

- system prompt
- user prompt
- 检索出来的上下文
- 历史消息
- 模型输出

### 为什么重要

- 超出窗口，内容会被截断或无法提交
- 即使没超，窗口太拥挤也会让有效信息被稀释
- RAG 项目的设计重点之一，就是把“最相关的少量信息”送进去，而不是把所有文档都塞进去

### 在项目里怎么理解

`02-rag-knowledge-assistant` 里为什么要做 chunk、top_k、citations，本质都和 context window 有关。不是模型看得越多越好，而是“让模型看到最相关、最紧凑、最可验证的信息”。

### 一句话讲法

context window 决定了模型这次最多能看到多少上下文，所以检索系统的目标不是塞满，而是精选。

## 3. Temperature

### 是什么

`temperature` 控制输出的随机性。

- 越低：越稳定、越保守、越接近高概率答案
- 越高：越发散、越有变化、越适合创意场景

### 为什么重要

不同任务对 temperature 的要求不同：

- 知识问答、结构化抽取、代码生成：通常偏低
- 营销文案、脑暴、创意写作：可以更高

### 在项目里怎么理解

RAG 问答的目标是“基于检索内容稳定回答”，不是写诗，所以通常不希望 temperature 太高。

### 一句话讲法

temperature 不是“质量调节器”，而是“随机性调节器”；越要求稳定和可复现，通常越要低。

## 4. Structured Output

### 是什么

`structured output` 是让模型按指定结构返回结果，而不是只返回一段自由文本。

常见形式：

- JSON
- 固定字段
- 枚举值
- schema 校验后的结果

### 为什么重要

- 方便程序继续处理，而不只是给人看
- 方便做接口集成、自动化流程、Agent 输出
- 减少“模型说得像对了，但程序没法用”的情况

### 在项目里怎么理解

后面的 Agent / Workflow 项目会越来越依赖 structured output。因为系统不只是要“读懂模型”，还要“拿模型输出继续执行下一步动作”。

### 一句话讲法

structured output 的价值在于让模型输出从“聊天内容”变成“系统可消费的数据”。

## 5. Function Calling / Tool Calling

### 是什么

这是让模型不要直接编答案，而是先决定“要不要调用某个工具”，并按规定参数去调用。

例如：

- 查天气
- 查数据库
- 调内部检索接口
- 调搜索、工单、日志系统

### 为什么重要

- 让模型获得外部能力，而不只靠参数记忆
- 让系统更可控，因为工具输入输出是结构化的
- 是 Agent 的基础组成部分之一

### 你现在该怎么理解

可以先把它理解成：

`模型负责决定做什么，工具负责真的去做`

### 一句话讲法

tool calling 让模型从“只会生成文本”变成“会调系统能力的控制器”。

## 6. 为什么 AI 应用主语言通常是 Python

### 核心原因

- 生态最强：OpenAI、LangChain、LangGraph、LlamaIndex、向量库、评测工具，通常 Python 支持最早最全
- 实验成本低：写 demo、调 prompt、试链路更快
- 数据与 AI 工具链天然集中在 Python 生态里

### 但别走偏

这不代表 Go、Java 没价值，而是 AI 应用开发阶段通常是：

- `Python` 负责模型能力接入、实验和编排
- 其他后端语言负责服务系统、基础设施、性能敏感模块

### 一句话讲法

AI 应用优先用 Python，不是因为它“更高级”，而是因为它在模型生态里摩擦最小、工具最全、试错最快。

## 7. 为什么后端背景做 AI 应用有优势

### 核心优势

后端工程师天然更关心：

- API 设计
- 错误处理
- 配置管理
- 日志与可观测性
- 超时、重试、权限、成本控制
- 可靠性与可维护性

而这些，恰好是 AI 应用从 demo 走向工程系统时最缺的能力。

### 现实区别

很多人会调模型，但做不出稳定系统。

你有后端背景，就更容易把 AI 功能接进：

- 服务
- 工作流
- 检索系统
- 企业内部平台

### 一句话讲法

后端背景的优势不是“更懂 prompt”，而是更擅长把模型能力做成可上线、可维护、可观测的系统。

## 8. 为什么最小服务骨架要先分层

### 分层不是为了好看

在 `01-fastapi-minimal-chat` 里先拆出：

- `api`
- `core`
- `schemas`
- `services`

目的是从第一天就避免把项目写成一个以后没法扩展的脚本。

### 每层大概负责什么

- `api`: 路由与 HTTP 入口
- `core`: 配置、基础设施
- `schemas`: 请求响应结构
- `services`: 业务逻辑与模型调用

### 为什么要这么做

- 以后加日志、鉴权、缓存、RAG、Agent 时不容易乱
- 测试更容易做
- 改模型调用逻辑时，不会把整个接口层也搅乱
- 面试时能说明你不是“写了个 demo”，而是在搭工程骨架

### 一句话讲法

最小服务先分层，是为了给后续扩展留出结构，不让项目在第二步就塌成一团。

## 9. LLM API 调用链路怎么讲

这部分是阶段一的核心出口，你至少要能顺着自己的项目讲一遍。

### 最小调用链路

1. 客户端发起 HTTP 请求到 FastAPI 接口
2. 路由层接收请求，并用 schema 做参数校验
3. 路由层把业务交给 service
4. service 组织模型输入，例如 system prompt、user message、参数
5. SDK 把请求发给模型服务
6. 模型返回结果
7. service 解析结果并做必要的格式整理
8. 路由层把结果包装成响应，返回给客户端

### 用 `01-fastapi-minimal-chat` 来讲

- `/chat` 是 HTTP 入口
- `ChatRequest` / `ChatResponse` 负责接口结构
- `LLMService` 负责真正调用模型
- `config.py` 负责读取模型配置、key、base url
- 最后把 reply 返回给调用方

### 一句话讲法

LLM API 调用链路本质上就是：`HTTP 请求 -> 参数校验 -> 业务组装 -> 模型调用 -> 结果解析 -> HTTP 响应`。

## 阶段一打钩标准

你不用背定义，但至少要做到下面这些：

- 能分别用自己的话解释 `token / context window / temperature`
- 能解释 `structured output` 和 `tool calling` 为什么是系统能力，不只是模型技巧
- 能解释为什么你现在主线用 Python，而不是先用 Go 重写一切
- 能解释为什么后端背景做 AI 应用不是劣势，反而是工程优势
- 能拿 `01-fastapi-minimal-chat` 解释分层设计
- 能从请求进来到响应出去，把 LLM API 链路讲顺

如果这些你都能口述出来，`Phase 1` 里那几个钩基本就可以打了。

## 建议你怎么用这份笔记

1. 先完整读一遍
2. 对着 `projects/01-fastapi-minimal-chat` 自己复述一遍
3. 不看笔记，再讲一遍 “什么是 token / 为什么要分层 / 调用链路怎么走”
4. 如果卡住，就回来看这一节

## 最后给你一个 60 秒版本

如果面试官让我用最短的话讲阶段一，我会这样说：

我先用 Python 和 FastAPI 搭了一个最小 LLM 服务骨架，把接口、配置、schema、模型调用分层拆开。这个阶段我重点理解了 token、context window、temperature、structured output 和 tool calling 这些基本概念，也能讲清一个 LLM 请求是怎么从 HTTP 入口一路走到模型，再把结果返回给客户端的。之所以先用 Python，是因为 AI 生态最成熟；而我有后端背景，所以在接口设计、错误处理、配置管理和系统可靠性上会更有优势。
