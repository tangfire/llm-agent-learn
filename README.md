# LLM Learning Workspace

这个工作区按“一个阶段一个项目”的方式组织，方便后面持续加新练习而不乱。

## 目录约定

- `projects/NN-topic-name/`: 每个独立练习项目
- 每个项目内部固定保留：
- `app/`: 服务代码
- `app/api/`: 路由层
- `app/core/`: 配置与基础设施
- `app/schemas/`: 请求响应模型
- `app/services/`: 业务与模型调用
- `README.md`: 项目说明
- `requirements.txt`: Python 依赖
- `.env.example`: 环境变量模板

## 当前项目

- `projects/01-fastapi-minimal-chat/`: FastAPI 最小 LLM 服务
