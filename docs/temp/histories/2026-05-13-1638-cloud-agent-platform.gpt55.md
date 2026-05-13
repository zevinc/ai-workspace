---
title: 云端通用 Agent 平台架构设计
tags:
    - agent-platform
    - architecture
    - microservices
    - spring-boot
    - LLM
    - RAG
    - multi-agent
    - orchestration
    - knowledge-base
    - MCP
summary: 云端通用 Agent 平台完整解决方案：6 层微服务架构（接入/引擎/模型/知识/会话/基础设施）、9 大模块功能设计（Agent 运行时/模型网关/工具注册中心/RAG/编排/会话记忆/认证多租户/可观测性）、Java Spring Boot 为主的技术选型、24 周 5 阶段执行计划。
created: 2026-05-13
---

下面是一套**云端通用 Agent 平台**落地方案，定位为：面向企业内部/业务系统的 **Agent 构建、运行、工具接入、知识接入、权限治理、观测运维平台**。

---

# 1. 平台目标

建设一个类似“Agent Operating Platform”的云端平台，让不同业务团队可以快速创建、发布、运行和管理 Agent。

核心能力：

1. 统一接入多模型：OpenAI / Claude / Gemini / Qwen / DeepSeek / 私有模型。
2. 统一接入工具：HTTP API、数据库、文件系统、MCP Server、内部服务。
3. 统一知识库：文档上传、解析、切片、Embedding、RAG 检索。
4. 统一编排：单 Agent、多 Agent、工作流、人审、重试、回滚。
5. 统一运行时：任务队列、沙箱执行、长期任务、异步任务。
6. 统一治理：权限、审计、限流、成本、Prompt 版本、输出安全。
7. 统一观测：Trace、Token、耗时、工具调用、失败原因、用户反馈。

MCP 适合做“Agent 连接工具和上下文”的标准协议，官方规范把 MCP Server 能力分为 Resources、Prompts、Tools 三类；A2A 则更偏向 Agent 与 Agent 之间的互操作和协作。([modelcontextprotocol.io][1])

---

# 2. 整体架构

```text
┌─────────────────────────────────────────────┐
│                 前端控制台                   │
│ Agent配置 / Workflow设计 / 知识库 / 运行记录 │
└──────────────────────┬──────────────────────┘
                       │
┌──────────────────────▼──────────────────────┐
│               API Gateway / BFF              │
│  Auth / Tenant / RateLimit / Audit / RBAC     │
└──────────────────────┬──────────────────────┘
                       │
┌──────────────────────▼──────────────────────┐
│               Agent 管理层                    │
│ Agent Registry / Prompt版本 / Model配置       │
│ Tool Registry / MCP Registry / Policy配置     │
└──────────────────────┬──────────────────────┘
                       │
┌──────────────────────▼──────────────────────┐
│               Agent 编排运行层                │
│ Planner / Executor / Memory / Tool Calling    │
│ Workflow / Multi-Agent / Human-in-the-loop    │
└──────────────┬───────────────┬───────────────┘
               │               │
     ┌─────────▼───────┐ ┌─────▼──────────┐
     │ Tool Runtime    │ │ Knowledge RAG   │
     │ API/MCP/Code    │ │ Embedding/Search│
     └─────────┬───────┘ └─────┬──────────┘
               │               │
┌──────────────▼───────────────▼──────────────┐
│               基础设施层                     │
│ PostgreSQL / Redis / MQ / VectorDB / Object  │
│ Kubernetes / Temporal / Observability        │
└─────────────────────────────────────────────┘
```

---

# 3. 核心模块设计

## 3.1 Agent Registry

管理 Agent 元数据。

主要功能：

| 功能            | 说明                           |
| ------------- | ---------------------------- |
| Agent 创建      | 名称、描述、头像、业务归属                |
| System Prompt | 支持变量、模板、版本                   |
| Model 配置      | 模型、温度、最大 token、超时            |
| Tool 授权       | 指定 Agent 可用工具                |
| Knowledge 授权  | 指定 Agent 可用知识库               |
| Memory 策略     | 会话记忆、长期记忆、用户画像               |
| 发布管理          | draft / staging / production |
| 回滚            | 回滚到历史版本                      |

建议 Agent 配置结构：

```json
{
  "agentId": "customer-service-agent",
  "name": "客服助手",
  "model": {
    "provider": "openai",
    "model": "gpt-4.1",
    "temperature": 0.3
  },
  "promptVersion": "v12",
  "tools": ["order_query", "refund_create"],
  "knowledgeBases": ["product-docs", "faq"],
  "memory": {
    "session": true,
    "longTerm": false
  },
  "guardrails": {
    "inputCheck": true,
    "outputCheck": true,
    "toolApproval": ["refund_create"]
  }
}
```

---

## 3.2 Prompt 管理

Prompt 不要硬编码在代码里，应平台化管理。

功能：

| 功能          | 说明                                 |
| ----------- | ---------------------------------- |
| Prompt 模板   | System / Developer / User Prompt   |
| 变量注入        | `{{user_name}}`、`{{current_date}}` |
| 版本管理        | 每次修改生成版本                           |
| 灰度发布        | 指定部分流量使用新版本                        |
| Prompt 测试集  | 固定问题集自动回归                          |
| 效果评分        | 人工评分 + LLM Judge                   |
| Prompt Diff | 对比两个版本差异                           |

Prompt 表结构示例：

```sql
agent_prompt
- id
- agent_id
- version
- system_prompt
- developer_prompt
- variables_schema
- status
- created_by
- created_at
```

---

## 3.3 Tool Registry

工具是 Agent 平台最核心的能力之一。

支持四类工具：

| 类型        | 说明                  |
| --------- | ------------------- |
| HTTP Tool | 调用内部 REST API       |
| DB Tool   | 查询数据库，需严格权限         |
| MCP Tool  | 通过 MCP Server 接入工具  |
| Code Tool | 沙箱执行 Python / JS 脚本 |

MCP 官方规范中，Tools 用于让模型执行函数或访问外部系统，Resources 用于提供上下文数据，Prompts 用于暴露可复用提示词模板。([modelcontextprotocol.io][1])

工具定义示例：

```json
{
  "name": "order_query",
  "description": "根据订单号查询订单详情",
  "type": "http",
  "method": "GET",
  "url": "https://order-service/api/orders/{orderId}",
  "inputSchema": {
    "type": "object",
    "properties": {
      "orderId": {
        "type": "string"
      }
    },
    "required": ["orderId"]
  },
  "auth": {
    "type": "service_token"
  },
  "timeoutMs": 3000
}
```

---

## 3.4 Agent 编排引擎

分三层实现：

```text
Agent Runtime
├── Planner：判断任务步骤
├── Executor：执行 LLM / Tool / RAG
├── State Manager：保存中间状态
├── Memory Manager：读写记忆
├── Guardrail：输入输出安全检查
└── Trace Collector：记录完整链路
```

推荐支持三种编排模式：

| 模式             | 适用场景                |
| -------------- | ------------------- |
| ReAct Agent    | 通用问答、工具调用           |
| Workflow Agent | 固定业务流程，如退款、审批       |
| Multi-Agent    | 复杂任务拆分，如研发助手、数据分析助手 |

OpenAI Agents SDK 官方定位包含 agent、tool、handoff、guardrails、tracing、sandbox execution 等能力，适合作为参考架构或部分运行时实现。([OpenAI Developers][2])

---

## 3.5 Workflow / 长任务引擎

Agent 不应该只支持一次性问答，还要支持长流程。

例如：

```text
用户提交需求
 → 产品分析 Agent
 → 技术方案 Agent
 → 代码生成 Agent
 → 测试 Agent
 → 人工确认
 → 提交 PR
```

推荐引入：

| 能力     | 说明           |
| ------ | ------------ |
| DAG 编排 | 节点、边、条件分支    |
| 状态持久化  | 每一步结果可恢复     |
| 人工审批   | 高风险操作前暂停     |
| 重试机制   | 工具失败自动重试     |
| 补偿机制   | 失败后回滚        |
| 定时任务   | 周期性 Agent 任务 |

技术上可以用：

| 方案                  | 适合场景                 |
| ------------------- | -------------------- |
| Temporal            | 企业级长任务、可靠工作流         |
| LangGraph           | Agent 状态图、多 Agent 编排 |
| Spring StateMachine | Java 项目内轻量状态机        |
| 自研 DAG Engine       | 高度定制化平台              |

---

## 3.6 Knowledge / RAG 模块

知识库模块建议拆成 6 个子模块：

```text
文件上传
 → 文档解析
 → 文本清洗
 → Chunk 切片
 → Embedding
 → 向量检索 + 重排序
```

功能设计：

| 模块             | 功能                     |
| -------------- | ---------------------- |
| Document Store | 存原始文件                  |
| Parser         | PDF、Word、Markdown、HTML |
| Chunker        | 按标题、段落、token 切片        |
| Embedder       | 生成向量                   |
| Retriever      | 向量检索、关键词检索、混合检索        |
| Reranker       | 对召回结果重新排序              |
| Citation       | 回答带来源引用                |
| Sync Job       | 定时同步外部知识源              |

推荐检索流程：

```text
用户问题
 → query rewrite
 → hybrid search
 → rerank
 → context compression
 → LLM answer
 → citation generation
```

---

## 3.7 Memory 模块

Agent 记忆分三类：

| 类型              | 说明        | 存储                    |
| --------------- | --------- | --------------------- |
| Session Memory  | 当前会话上下文   | Redis / PostgreSQL    |
| User Memory     | 用户偏好、长期信息 | PostgreSQL            |
| Task Memory     | 任务中间状态    | PostgreSQL / Temporal |
| Semantic Memory | 可检索历史知识   | VectorDB              |

建议不要一开始做太复杂的“自动记忆”，先做：

1. 会话历史。
2. 显式收藏。
3. 用户确认后写入长期记忆。
4. 重要任务结果自动沉淀到知识库。

---

## 3.8 Guardrails / 安全治理

Guardrails 应覆盖输入、执行、输出三层。

| 阶段   | 风险               | 方案              |
| ---- | ---------------- | --------------- |
| 输入   | Prompt Injection | 输入检测、上下文隔离      |
| RAG  | 知识污染             | 文档权限过滤、来源可信度    |
| Tool | 越权调用             | RBAC、工具白名单、参数校验 |
| Code | 恶意执行             | 沙箱、网络隔离、资源限制    |
| 输出   | 泄露敏感信息           | DLP、敏感词、PII 检测  |
| 成本   | Token 爆炸         | 限流、预算、最大轮数      |

OpenAI Agents SDK 的 Guardrails 支持对用户输入和 Agent 输出做校验，Tracing 则记录 LLM 生成、工具调用、handoff、guardrail 等运行事件，适合参考到平台治理和观测模块中。([openai.github.io][3])

---

## 3.9 Observability / AgentOps

Agent 平台必须做可观测，否则生产环境很难排查问题。

建议记录：

| 指标             | 说明                 |
| -------------- | ------------------ |
| Trace ID       | 一次 Agent Run 的唯一标识 |
| Token Usage    | 输入、输出、总 token      |
| Cost           | 按模型计算成本            |
| Latency        | 总耗时、LLM 耗时、Tool 耗时 |
| Tool Calls     | 调用了哪些工具            |
| RAG Sources    | 使用了哪些知识片段          |
| Error          | 失败节点、异常堆栈          |
| User Feedback  | 点赞、点踩、人工评分         |
| Prompt Version | 当前使用的 Prompt 版本    |
| Model Version  | 当前使用的模型            |

Trace 结构：

```text
AgentRun
├── LLMCall
├── ToolCall
├── RetrievalCall
├── GuardrailCheck
├── HumanApproval
└── FinalAnswer
```

---

# 4. 推荐技术选型

## 4.1 后端技术栈

结合你之前偏 Java / Spring Boot 的项目背景，推荐：

| 层级     | 技术                                        |
| ------ | ----------------------------------------- |
| 后端框架   | Spring Boot 3.x                           |
| AI 框架  | Spring AI + LangGraph / OpenAI Agents SDK |
| API 网关 | Spring Cloud Gateway / Kong               |
| 鉴权     | Spring Security + OAuth2 / OIDC           |
| 数据库    | PostgreSQL                                |
| 缓存     | Redis                                     |
| 消息队列   | Kafka / RabbitMQ                          |
| 工作流    | Temporal                                  |
| 向量库    | pgvector / Milvus / Qdrant                |
| 对象存储   | S3 / MinIO                                |
| 搜索     | Elasticsearch / OpenSearch                |
| 观测     | OpenTelemetry + Prometheus + Grafana      |
| 日志     | Loki / ELK                                |
| 部署     | Kubernetes                                |
| IaC    | Terraform / Helm                          |

## 4.2 Agent Runtime 选型

| 方案                | 优点                          | 缺点             | 建议              |
| ----------------- | --------------------------- | -------------- | --------------- |
| Spring AI         | Java 生态友好                   | Agent 编排能力相对弱  | 适合作为模型与 RAG 接入层 |
| LangGraph         | 状态图、多 Agent 强               | Python 生态为主    | 适合复杂 Agent 编排   |
| OpenAI Agents SDK | Tool / Guardrail / Trace 完整 | 绑定 OpenAI 生态更深 | 适合快速验证          |
| Temporal          | 长任务可靠                       | 不是 Agent 框架    | 适合生产级工作流        |
| 自研 Runtime        | 可控性最高                       | 成本高            | 平台后期再做          |

推荐组合：

```text
Spring Boot 作为平台主后端
+ Spring AI 做模型与 RAG 接入
+ Temporal 做长任务工作流
+ MCP 做工具标准接入
+ LangGraph / OpenAI Agents SDK 做复杂 Agent Runtime 参考或独立服务
```

---

# 5. 关键数据模型

## Agent

```sql
agent
- id
- tenant_id
- name
- description
- status
- owner_id
- created_at
- updated_at
```

## Agent Version

```sql
agent_version
- id
- agent_id
- version
- model_config
- prompt_config
- tool_config
- knowledge_config
- memory_config
- guardrail_config
- status
```

## Tool

```sql
tool
- id
- name
- type
- description
- input_schema
- output_schema
- auth_config
- endpoint_config
- created_at
```

## Agent Run

```sql
agent_run
- id
- tenant_id
- agent_id
- agent_version
- user_id
- input
- output
- status
- token_input
- token_output
- cost
- latency_ms
- created_at
```

## Tool Call

```sql
tool_call
- id
- run_id
- tool_id
- input
- output
- status
- latency_ms
- error_message
```

## Knowledge Chunk

```sql
knowledge_chunk
- id
- knowledge_base_id
- document_id
- content
- metadata
- embedding
- created_at
```

---

# 6. 典型调用流程

## 6.1 普通问答

```text
用户输入
 → API Gateway
 → Agent Runtime
 → 加载 Agent 配置
 → 加载 Prompt
 → 检索知识库
 → 调用 LLM
 → 输出答案
 → 保存 Trace
```

## 6.2 工具调用

```text
用户：帮我查订单 123
 → Agent 判断需要 order_query
 → Tool Registry 校验权限
 → 参数 Schema 校验
 → 调用订单服务
 → LLM 整理结果
 → 返回用户
```

## 6.3 高风险操作

```text
用户：帮我给这个订单退款
 → Agent 调用订单查询
 → 生成退款方案
 → 判断 refund_create 是高风险工具
 → 暂停，等待人工确认
 → 用户确认
 → 执行退款 API
 → 返回结果
```

---

# 7. 部署架构

```text
Kubernetes Cluster
├── agent-console-web
├── agent-api-service
├── agent-runtime-service
├── tool-runtime-service
├── rag-service
├── embedding-worker
├── document-parser-worker
├── workflow-worker
├── postgres
├── redis
├── vector-db
├── minio
├── prometheus
├── grafana
└── loki / elasticsearch
```

建议服务拆分：

| 服务                    | 职责             |
| --------------------- | -------------- |
| agent-api-service     | Agent 管理、配置、发布 |
| agent-runtime-service | Agent 执行       |
| tool-service          | 工具注册与调用        |
| rag-service           | 知识库检索          |
| document-service      | 文档解析与入库        |
| workflow-service      | 长任务编排          |
| observability-service | Trace、日志、成本分析  |
| admin-console         | 平台控制台          |

---

# 8. 执行计划

## 阶段一：MVP，4～6 周

目标：能创建 Agent、接入模型、接入知识库、调用简单工具。

交付：

1. Agent 创建与配置。
2. Prompt 版本管理。
3. OpenAI / Claude / Qwen 模型接入。
4. 文件上传、解析、Embedding、RAG。
5. HTTP Tool 注册与调用。
6. Agent Run 记录。
7. 基础 Trace、Token 统计。
8. 简单控制台。

优先技术：

```text
Spring Boot
PostgreSQL + pgvector
Redis
MinIO
Spring AI
OpenTelemetry
```

---

## 阶段二：生产可用，6～10 周

目标：支持业务系统接入和稳定运行。

交付：

1. 多租户。
2. RBAC 权限。
3. Tool 权限控制。
4. MCP Server 接入。
5. Guardrails。
6. Human-in-the-loop。
7. 成本统计。
8. Prompt 测试集。
9. Agent 发布与回滚。
10. 失败重试与限流。

引入：

```text
Temporal
Kubernetes
Prometheus + Grafana
MCP Gateway
```

---

## 阶段三：平台化，10～16 周

目标：支持多 Agent 协作、复杂工作流和企业级治理。

交付：

1. Workflow 设计器。
2. 多 Agent 编排。
3. A2A 协议兼容。
4. Agent Marketplace。
5. 自动评测。
6. LLM Judge。
7. 成本预算。
8. 沙箱代码执行。
9. 审计报表。
10. AgentOps Dashboard。

A2A 官方文档将其定位为开放标准，用于不同框架、不同供应商构建的 Agent 之间安全通信和协作，适合放到平台化阶段支持。([a2a-protocol.org][4])

---

# 9. 推荐落地路线

最推荐的路线是：

```text
先做“Agent 管理 + RAG + HTTP Tool + Trace”
再做“工作流 + MCP + Guardrails”
最后做“多 Agent + A2A + Agent Marketplace”
```

不要一开始就做全自动多 Agent。第一版应该聚焦：

1. Agent 配置可视化。
2. 知识库可用。
3. 工具调用可控。
4. 运行过程可追踪。
5. 结果可评估。
6. 权限和成本可治理。

---

# 10. 最小可行版本架构建议

如果你现在要马上启动，我建议 MVP 就这样设计：

```text
前端：React / Vue
后端：Spring Boot 3
模型层：Spring AI
数据库：PostgreSQL + pgvector
缓存：Redis
文件：MinIO
队列：RabbitMQ
观测：OpenTelemetry + Grafana
工具协议：HTTP Tool 优先，MCP 第二阶段
工作流：先简单状态机，后续接 Temporal
```

MVP 模块：

```text
agent-platform
├── agent-api
├── agent-runtime
├── tool-registry
├── knowledge-service
├── document-worker
├── embedding-worker
├── observability
└── console-web
```

核心原则：

> Agent 平台不要只做“聊天壳子”，而是要做成：**模型 + 工具 + 知识 + 工作流 + 权限 + 观测 + 治理** 的统一运行平台。

[1]: https://modelcontextprotocol.io/specification/2025-11-25?utm_source=chatgpt.com "Specification"
[2]: https://developers.openai.com/api/docs/guides/agents?utm_source=chatgpt.com "Agents SDK | OpenAI API"
[3]: https://openai.github.io/openai-agents-python/guardrails/?utm_source=chatgpt.com "Guardrails - OpenAI Agents SDK"
[4]: https://a2a-protocol.org/latest/?utm_source=chatgpt.com "Agent2Agent (A2A) Protocol"
