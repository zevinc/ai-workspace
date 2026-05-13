---
title: 云端通用 Agent 平台 — 最终融合方案
tags:
    - agent-platform
    - architecture
    - microservices
    - spring-ai
    - temporal
    - RAG
    - multi-agent
    - orchestration
    - guardrails
    - MCP
    - knowledge-base
summary: 云端通用 Agent 平台最终融合方案（Hermes + GPT5.5）：8 层服务架构含独立 Model Gateway 和 Session Service、9 大模块含 SQL Schema 和调用流程、Spring AI + Temporal 技术栈、3 层 Guardrails 安全治理、6 步 RAG 管道 + 知识图谱、5 种编排模式、24 周 5 阶段执行计划、7-9 人团队配置。融合策略：GPT5.5 主体(90%) + Hermes 模块化拆分和团队规划。
created: 2026-05-13
---

# 云端通用 Agent 平台 — 最终融合方案

> 方案来源：GPT5.5 方案为主体（90%），融合 Hermes 方案的模块化服务拆分、团队规划、编排模式、语义缓存和知识图谱。
> 本方案是最终版本，替代此前所有独立方案和对比分析。

---

## 目录

1. [平台目标](#1-平台目标)
2. [整体架构](#2-整体架构)
3. [核心模块设计](#3-核心模块设计)
4. [安全治理 (Guardrails)](#4-安全治理-guardrails)
5. [知识 & RAG 设计](#5-知识--rag-设计)
6. [数据模型](#6-数据模型)
7. [典型调用流程](#7-典型调用流程)
8. [技术选型](#8-技术选型)
9. [部署架构](#9-部署架构)
10. [执行计划](#10-执行计划)
11. [团队配置](#11-团队配置)
12. [关键决策记录](#12-关键决策记录)
13. [风险与缓解](#13-风险与缓解)

---

## 1. 平台目标

建设一个 **Agent Operating Platform**，让不同业务团队可以快速创建、发布、运行和管理 Agent。

核心能力矩阵（7 个统一）：

| # | 能力 | 说明 |
|---|------|------|
| 1 | 统一接入多模型 | OpenAI / Claude / Gemini / Qwen / DeepSeek / 私有模型 |
| 2 | 统一接入工具 | HTTP API、数据库、文件系统、MCP Server、内部服务 |
| 3 | 统一知识库 | 文档上传、解析、切片、Embedding、RAG 检索 |
| 4 | 统一编排 | 单 Agent、多 Agent、工作流、人审、重试、回滚 |
| 5 | 统一运行时 | 任务队列、沙箱执行、长期任务、异步任务 |
| 6 | 统一治理 | 权限、审计、限流、成本、Prompt 版本、输出安全 |
| 7 | 统一观测 | Trace、Token、耗时、工具调用、失败原因、用户反馈 |

协议定位：
- **MCP**：Agent 连接工具和上下文的标准协议，覆盖 Resources / Prompts / Tools 三类能力
- **A2A**：Agent 与 Agent 之间的互操作和协作标准（Phase 3 引入）

---

## 2. 整体架构

### 2.1 架构分层

```
┌─────────────────────────────────────────────────────────────────┐
│                         前端控制台                                │
│    Agent配置 / Workflow设计 / 知识库管理 / 运行记录 / 监控大盘      │
└──────────────────────────────┬──────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────┐
│                    API Gateway / BFF                             │
│      Auth (OAuth2/OIDC) / Tenant / RateLimit / Audit / RBAC      │
└──────────────────────────────┬──────────────────────────────────┘
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
┌─────────▼────────┐  ┌────────▼────────┐  ┌───────▼──────────┐
│  Agent 管理层     │  │  Model Gateway  │  │  Session Service │
│  · Agent Registry │  │  · 多厂商适配    │  │  · 会话上下文     │
│  · Prompt 版本    │  │  · 智能路由     │  │  · 跨Agent共享    │
│  · Tool Registry  │  │  · 语义缓存     │  │  · 记忆检索      │
│  · Policy 配置    │  │  · 限流降级     │  │  · 用户画像      │
└─────────┬────────┘  └────────┬────────┘  └───────┬──────────┘
          │                    │                    │
┌─────────▼────────────────────▼────────────────────▼──────────┐
│                      Agent 编排运行层                          │
│  Planner / Executor / State Manager / Memory Manager          │
│  Guardrail (输入/执行/输出) / Trace Collector                 │
│  Workflow Engine (Temporal) / Multi-Agent Orchestrator        │
└──────────────┬───────────────────────┬───────────────────────┘
               │                       │
     ┌─────────▼───────┐     ┌─────────▼──────────┐
     │  Tool Runtime   │     │  Knowledge & RAG   │
     │  API/MCP/Code   │     │  Embedding/Search  │
     │  沙箱执行隔离     │     │  Rerank/Citation   │
     └─────────┬───────┘     └─────────┬──────────┘
               │                       │
┌──────────────▼───────────────────────▼──────────────────────┐
│                      基础设施层                               │
│  PostgreSQL+pgvector / Redis / RabbitMQ / MinIO / Temporal   │
│  Kubernetes / Prometheus+Grafana / OpenTelemetry+Jaeger     │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 架构设计要点

**融合决策**：采用 GPT5.5 的嵌套分层表达，融入 Hermes 的独立服务拆分：

| 设计点 | 来源 | 理由 |
|--------|------|------|
| Model Gateway 独立服务 | Hermes | 多模型路由、限流、语义缓存独立治理 |
| Session Service 独立服务 | Hermes | 跨 Agent 共享上下文，不绑定单个运行时 |
| Agent 管理层（Registry+Prompt+Tool+Policy） | GPT5.5 | 配置管理内聚，减少服务间耦合 |
| 编排运行层含 Guardrails | GPT5.5 | 安全校验必须与执行引擎紧耦合 |
| Tool Runtime 独立 | GPT5.5 | 工具调用与 Agent 逻辑解耦，支持沙箱隔离 |

---

## 3. 核心模块设计

### 3.1 Agent Registry

管理 Agent 元数据和生命周期。

| 功能 | 说明 |
|------|------|
| Agent 创建 | 名称、描述、头像、业务归属 |
| System Prompt | 支持变量、模板、版本 |
| Model 配置 | 模型、温度、最大 token、超时 |
| Tool 授权 | 指定 Agent 可用工具 |
| Knowledge 授权 | 指定 Agent 可用知识库 |
| Memory 策略 | 会话记忆、长期记忆、用户画像 |
| 发布管理 | draft → staging → production |
| 回滚 | 回滚到历史版本 |

**Agent 配置示例**：

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

### 3.2 Prompt 管理

Prompt 平台化管理，不硬编码。

| 功能 | 说明 |
|------|------|
| Prompt 模板 | System / Developer / User Prompt |
| 变量注入 | `{{user_name}}`、`{{current_date}}` |
| 版本管理 | 每次修改生成版本 |
| 灰度发布 | 指定部分流量使用新版本 |
| Prompt 测试集 | 固定问题集自动回归 |
| 效果评分 | 人工评分 + LLM Judge |
| Prompt Diff | 对比两个版本差异 |

**Prompt 表结构**：

```sql
agent_prompt (
    id            BIGSERIAL PRIMARY KEY,
    agent_id      BIGINT NOT NULL,
    version       VARCHAR(20) NOT NULL,
    system_prompt TEXT NOT NULL,
    developer_prompt TEXT,
    variables_schema JSONB,
    status        VARCHAR(20) DEFAULT 'draft',
    created_by    VARCHAR(100),
    created_at    TIMESTAMPTZ DEFAULT NOW()
);
```

---

### 3.3 Model Gateway（独立服务）

**融合来源：Hermes 提出的独立 Model Gateway 概念 + GPT5.5 的多厂商适配 + 新增语义缓存。**

| 能力 | 说明 |
|------|------|
| 多厂商统一抽象 | OpenAI / Anthropic / Gemini / Qwen / DeepSeek / 私有模型 → 统一 API |
| 智能路由 | 按成本/能力/延迟策略自动选择模型 |
| Fallback 链 | 主模型不可用时自动降级到备选 |
| 语义缓存 | 相似请求命中缓存，减少 LLM 调用成本（LRU + 相似度阈值） |
| 限流配额 | 按租户/Agent/API Key 多维度限流 |
| 负载均衡 | 多实例模型请求分发 |

**路由策略**：

| 策略 | 场景 | 实现 |
|------|------|------|
| 成本优先 | 简单问答、摘要 | → GPT-4o-mini / Claude Haiku |
| 能力优先 | 复杂推理、代码生成 | → Claude Opus / GPT-4o |
| 延迟优先 | 实时交互 | → 最快可用模型 |
| 自定义规则 | 特定场景 | 按标签/context 匹配 |

---

### 3.4 Tool Registry

支持四类工具接入：

| 类型 | 说明 | 隔离级别 |
|------|------|----------|
| HTTP Tool | 调用内部 REST API | 网络策略 |
| DB Tool | 查询数据库 | 只读账号 + 行级权限 |
| MCP Tool | 通过 MCP Server 接入 | MCP 协议层权限 |
| Code Tool | 沙箱执行 Python/JS | Docker/K8s Pod 隔离 |

**工具定义示例**：

```json
{
  "name": "order_query",
  "description": "根据订单号查询订单详情",
  "type": "http",
  "method": "GET",
  "url": "https://order-service/api/orders/{orderId}",
  "inputSchema": {
    "type": "object",
    "properties": { "orderId": { "type": "string" } },
    "required": ["orderId"]
  },
  "auth": { "type": "service_token" },
  "timeoutMs": 3000
}
```

---

### 3.5 Agent 编排运行层

分三层实现：

```
Agent Runtime
├── Planner：判断任务步骤
├── Executor：执行 LLM / Tool / RAG
├── State Manager：保存中间状态，支持断点恢复
├── Memory Manager：读写短期/长期/语义记忆
├── Guardrail：输入/执行/输出安全检查（详见 §4）
└── Trace Collector：记录完整链路（详见 §3.9）
```

**编排模式（融合 Hermes 的 5 种模式 + GPT5.5 的 3 种分类）**：

| 模式 | 适用场景 | 实现方式 |
|------|---------|----------|
| ReAct Agent | 通用问答、工具调用 | Agent Runtime 内置循环 |
| Workflow Agent | 固定业务流程（退款、审批） | Temporal Workflow |
| Sequential | 串联任务链 A→B→C | Temporal / DAG |
| Parallel | 并行分析 [A, B, C]→Merge | Temporal Activity 并行 |
| Debate | 多 Agent 辩论取共识 | Orchestrator 协调 |
| Supervisor | 主管 Agent 调度 Workers | Orchestrator + Handoff |
| Multi-Agent | 复杂任务拆分（研发助手、数据分析） | Temporal Child Workflow |

**推荐实现路径**：
- Phase 1：Agent Runtime 内置 ReAct
- Phase 2：Temporal 接管 Workflow / Sequential / Parallel
- Phase 3：Orchestrator 实现 Debate / Supervisor / Multi-Agent

---

### 3.6 Workflow / 长任务引擎

Agent 平台必须支持长流程，不能只做一次性问答。

**典型长流程示例**：

```
用户提交需求
 → 产品分析 Agent
 → 技术方案 Agent
 → 代码生成 Agent
 → 测试 Agent
 → 人工确认
 → 提交 PR
```

| 能力 | 说明 | 实现 |
|------|------|------|
| DAG 编排 | 节点、边、条件分支、并行 | Temporal Workflow |
| 状态持久化 | 每一步结果可恢复 | Temporal Event History |
| 人工审批 | 高风险操作前暂停等待确认 | Temporal Signal |
| 重试机制 | 工具失败自动重试（指数退避） | Temporal RetryPolicy |
| 补偿机制 | 失败后执行回滚操作 | Temporal Saga |
| 定时任务 | 周期性 Agent 任务 | Temporal Schedule |

---

### 3.7 Session & Memory Service（独立服务）

**融合来源：Hermes 独立 Session Service + GPT5.5 的记忆分类。**

| 记忆类型 | 说明 | 存储 | TTL |
|----------|------|------|-----|
| Session Memory | 当前会话上下文 | Redis + PostgreSQL | 会话结束 |
| User Memory | 用户偏好、长期信息 | PostgreSQL | 永久 |
| Task Memory | 任务中间状态 | PostgreSQL / Temporal | 任务结束 |
| Semantic Memory | 可检索历史知识 | pgvector | 永久 |

**实施策略（渐进式）**：

```
Phase 1: 会话历史（Redis + PostgreSQL）
Phase 2: 显式收藏 + 用户确认后写入长期记忆
Phase 3: 重要任务结果自动沉淀到知识库
Phase 4: 语义记忆自动检索与遗忘
```

---

### 3.8 安全治理 (Guardrails)

详见 [§4 安全治理](#4-安全治理-guardrails)。

---

### 3.9 Observability / AgentOps

| 指标 | 说明 | 采集方式 |
|------|------|----------|
| Trace ID | 一次 Agent Run 的唯一标识 | OpenTelemetry |
| Token Usage | 输入、输出、总 token | LLM 调用拦截 |
| Cost | 按模型计算成本 | Token × 单价 |
| Latency | 总耗时、LLM 耗时、Tool 耗时 | Span 计算 |
| Tool Calls | 调用了哪些工具、参数、结果 | Tool Runtime 上报 |
| RAG Sources | 使用了哪些知识片段 | Retriever 上报 |
| Error | 失败节点、异常堆栈 | 异常捕获 |
| User Feedback | 点赞、点踩、人工评分 | 前端采集 |
| Prompt Version | 当前使用的 Prompt 版本 | Agent Runtime 上报 |
| Model Version | 当前使用的模型 | Model Gateway 上报 |

**Trace 结构**：

```
AgentRun
├── LLMCall (可多个)
├── ToolCall (可多个)
├── RetrievalCall (可多个)
├── GuardrailCheck (输入+输出)
├── HumanApproval (可选)
└── FinalAnswer
```

---

## 4. 安全治理 (Guardrails)

### 4.1 三层防护模型

```
输入层                   执行层                    输出层
┌──────────┐    ┌─────────────────────┐    ┌──────────────┐
│ Prompt    │    │ Tool   │ Code │ RAG │    │ DLP          │
│ Injection │    │ 越权    │ 恶意  │ 污染 │    │ PII 检测      │
│ 检测      │    │ 调用    │ 执行  │ 过滤 │    │ 敏感词过滤    │
│ 上下文隔离 │    │ RBAC   │ 沙箱  │ 来源 │    │ 合规检查      │
└──────────┘    └─────────────────────┘    └──────────────┘
```

### 4.2 各层详细方案

| 阶段 | 风险 | 方案 |
|------|------|------|
| **输入** | Prompt Injection | 输入检测（正则+分类器）、上下文隔离（System Prompt 与 User Input 分通道） |
| **RAG** | 知识污染 | 文档权限过滤、来源可信度评分 |
| **Tool** | 越权调用 | RBAC 白名单、参数 Schema 校验、高风险工具人工审批 |
| **Code** | 恶意执行 | Docker/K8s Pod 沙箱、网络隔离（无外网）、CPU/内存限制、超时 kill |
| **输出** | 泄露敏感信息 | DLP 扫描、敏感词库、PII 检测（身份证/手机号/邮箱脱敏） |
| **成本** | Token 爆炸 | 单次预算上限、单 Agent 最大轮数、异常用量告警 |

### 4.3 高风险工具审批流程

```
Agent 判断需调用 refund_create（标记为高风险）
  → Runtime 挂起，通知用户
  → 用户在前端确认（含操作详情预览）
  → Runtime 收到确认 Signal
  → 执行工具调用
  → 返回结果
```

---

## 5. 知识 & RAG 设计

### 5.1 文档处理管道

```
文件上传 (MinIO)
  → 文档解析 (PDF/Word/Markdown/HTML)
  → 文本清洗 (去噪、标准化)
  → Chunk 切片 (按标题/段落/token 智能分块)
  → Embedding (text-embedding-3-small / bge-large-zh)
  → 向量入库 (pgvector)
  → 增量同步 Job (定时检测外部知识源变更)
```

### 5.2 检索流程

```
用户问题
  → Query Rewrite (口语→检索友好)
  → Hybrid Search (语义 70% + 关键词 BM25 30%，RRF 融合)
  → Rerank (Cross-encoder 精排 Top-K)
  → Context Compression (LLM 压缩冗余)
  → LLM Answer (含检索上下文)
  → Citation Generation (回答带来源引用)
```

### 5.3 RAG 子模块

| 模块 | 功能 | 技术 |
|------|------|------|
| Document Store | 存原始文件 | MinIO |
| Parser | 多格式解析 | Apache Tika / Unstructured |
| Chunker | 智能分块 | 按标题+段落，512 token 重叠 50 |
| Embedder | 生成向量 | text-embedding-3-small / bge-large-zh |
| Retriever | 混合检索 | pgvector (HNSW 索引) + BM25 |
| Reranker | 召回重排 | bge-reranker-v2-m3 |
| Citation | 来源引用 | Post-processing 追加文档来源 |
| Sync Job | 定时同步 | Temporal Schedule |

### 5.4 Knowledge Graph（Phase 2）

**融合来源：Hermes 提出的 Neo4j 知识图谱。**

在 Phase 2 引入可选的知识图谱层，用于：
- 实体抽取：从文档和对话中提取关键实体
- 关系构建：实体间关联关系自动发现
- 图检索：基于图结构的多跳推理问答

> 此为增强能力，不影响 Phase 1 MVP 交付。

---

## 6. 数据模型

### 6.1 Agent

```sql
agent (
    id            BIGSERIAL PRIMARY KEY,
    tenant_id     BIGINT NOT NULL,
    name          VARCHAR(200) NOT NULL,
    description   TEXT,
    status        VARCHAR(20) DEFAULT 'draft',
    owner_id      BIGINT,
    created_at    TIMESTAMPTZ DEFAULT NOW(),
    updated_at    TIMESTAMPTZ DEFAULT NOW()
);
```

### 6.2 Agent Version

```sql
agent_version (
    id                BIGSERIAL PRIMARY KEY,
    agent_id          BIGINT NOT NULL REFERENCES agent(id),
    version           VARCHAR(20) NOT NULL,
    model_config      JSONB NOT NULL,
    prompt_config     JSONB NOT NULL,
    tool_config       JSONB,
    knowledge_config  JSONB,
    memory_config     JSONB,
    guardrail_config  JSONB,
    status            VARCHAR(20) DEFAULT 'draft',
    created_at        TIMESTAMPTZ DEFAULT NOW()
);
```

### 6.3 Tool

```sql
tool (
    id              BIGSERIAL PRIMARY KEY,
    name            VARCHAR(200) NOT NULL UNIQUE,
    type            VARCHAR(20) NOT NULL,
    description     TEXT,
    input_schema    JSONB,
    output_schema   JSONB,
    auth_config     JSONB,
    endpoint_config JSONB,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
```

### 6.4 Agent Run

```sql
agent_run (
    id              BIGSERIAL PRIMARY KEY,
    tenant_id       BIGINT NOT NULL,
    agent_id        BIGINT NOT NULL,
    agent_version   VARCHAR(20),
    user_id         BIGINT,
    input           TEXT,
    output          TEXT,
    status          VARCHAR(20) DEFAULT 'running',
    token_input     INTEGER,
    token_output    INTEGER,
    cost            DECIMAL(10,6),
    latency_ms      INTEGER,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
```

### 6.5 Tool Call

```sql
tool_call (
    id              BIGSERIAL PRIMARY KEY,
    run_id          BIGINT NOT NULL REFERENCES agent_run(id),
    tool_id         BIGINT REFERENCES tool(id),
    input           JSONB,
    output          JSONB,
    status          VARCHAR(20),
    latency_ms      INTEGER,
    error_message   TEXT
);
```

### 6.6 Knowledge Chunk

```sql
knowledge_chunk (
    id                BIGSERIAL PRIMARY KEY,
    knowledge_base_id BIGINT NOT NULL,
    document_id       BIGINT,
    content           TEXT NOT NULL,
    metadata          JSONB,
    embedding         VECTOR(1536),
    created_at        TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX ON knowledge_chunk USING hnsw (embedding vector_cosine_ops);
```

---

## 7. 典型调用流程

### 7.1 普通问答

```
用户输入
 → API Gateway (Auth + RateLimit)
 → Agent Runtime
 → 加载 Agent 配置 + Prompt 模板
 → Session Service 加载历史上下文
 → Knowledge Service 检索相关知识
 → Model Gateway 调用 LLM (含路由+缓存检查)
 → Guardrail 输出检查
 → 流式返回用户
 → Trace Collector 保存完整链路
```

### 7.2 工具调用

```
用户："帮我查订单 123"
 → Agent Planner 判断需要 order_query 工具
 → Tool Registry 校验 Agent 是否有权限
 → 参数 Schema 校验 (orderId="123")
 → Tool Runtime 调用订单服务 (HTTP GET)
 → LLM 整理 Tool 返回结果为自然语言
 → Guardrail 输出检查
 → 返回用户
```

### 7.3 高风险操作（人工审批）

```
用户："帮我给这个订单退款"
 → Agent 调用 order_query 确认订单信息
 → Agent 生成退款方案
 → Guardrail 判断 refund_create 标记为高风险工具
 → Runtime 挂起 Workflow，推送通知给用户
 → 用户在前端审批确认
 → Temporal Signal 唤醒 Workflow
 → 执行退款 API
 → 返回结果
```

### 7.4 长流程工作流

```
用户提交需求 "做一个用户登录模块"
 → Temporal Workflow 启动
 → 需求分析 Agent (Activity 1)
 → 技术方案 Agent (Activity 2)
 → 代码生成 Agent (Activity 3)
 → 测试 Agent (Activity 4)
 → 人工确认节点 (等待 Signal)
 → 提交 PR Agent (Activity 5)
 → Workflow 完成
```

---

## 8. 技术选型

### 8.1 后端技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 后端框架 | Spring Boot 3.x | 团队主技术栈 |
| AI 框架 | Spring AI | Spring 官方，MCP 原生支持，生态成熟 |
| Agent Runtime | 自研 + Spring AI + Temporal | MVP 先自研 ReAct，Phase 2 引入 Temporal |
| API 网关 | Spring Cloud Gateway | 响应式，与 Spring 生态无缝 |
| 鉴权 | Spring Security + OAuth2/OIDC | 企业级认证标准 |
| 数据库 | PostgreSQL 16 | 全部业务数据 |
| 向量库 | pgvector (PG 插件) | 减少多数据库运维，一站式 |
| 缓存 | Redis Stack | Session、限流、语义缓存 |
| 消息队列 | RabbitMQ | 异步任务解耦，运维成熟 |
| 工作流引擎 | Temporal | 长任务可靠执行、Saga 补偿 |
| 对象存储 | MinIO / S3 | 兼容 S3 协议，自建或云 |
| 搜索引擎 | Elasticsearch (可选) | Phase 2 全文检索增强 |

### 8.2 Agent Runtime 选型决策

| 方案 | 定位 | 决策 |
|------|------|------|
| Spring AI | 模型接入 + RAG + MCP 客户端 | **采用** - Phase 1 起用 |
| 自研 Runtime | Agent 循环 + 工具调用 | **采用** - Phase 1 MVP |
| Temporal | 长任务工作流 + 重试 + 持久化 | **采用** - Phase 2 引入 |
| LangGraph | 复杂 Agent 状态图 | 参考架构，暂不引入 |
| OpenAI Agents SDK | Tool/Guardrail/Trace | 参考设计，不直接依赖 |

### 8.3 为什么选 Spring AI 而非 LangChain4j

| 维度 | Spring AI | LangChain4j |
|------|-----------|-------------|
| 维护方 | Spring 官方 | 社区 |
| Spring Boot 集成 | 原生深度集成 | 适配层 |
| MCP 支持 | 原生支持 | 需额外适配 |
| 生态成熟度 | Spring 生态保证 | Java 生态偏弱 |
| 长期风险 | 低（VMware/Broadcom 背书） | 中（社区驱动） |

### 8.4 为什么选 Temporal 而非自研 DAG

| 维度 | Temporal | 自研 DAG |
|------|----------|----------|
| 可靠性 | 工业验证（Netflix/Uber/Stripe） | 需大量测试 |
| 持久化 | 内置 Event History | 需自行实现 |
| 重试机制 | 内置指数退避 | 需自行实现 |
| 补偿事务 | 内置 Saga | 需自行实现 |
| 运维成熟度 | 高（SDK + UI + Metrics） | 需自行建设 |
| 学习成本 | 2-3 周 | 0（但长期维护成本高） |

### 8.5 基础设施

| 组件 | 选型 | 用途 |
|------|------|------|
| 容器编排 | Kubernetes | 服务部署 + 自动扩缩容 |
| CI/CD | GitHub Actions / GitLab CI | 自动化构建部署 |
| 监控 | Prometheus + Grafana | 指标采集与展示 |
| 追踪 | OpenTelemetry + Jaeger | 全链路追踪 |
| 日志 | Loki / ELK | 日志聚合检索 |
| 代码沙箱 | Docker-in-Docker / K8s Pod | Agent 代码执行隔离 |
| IaC | Terraform + Helm | 基础设施即代码 |

### 8.6 前端

| 组件 | 选型 | 用途 |
|------|------|------|
| 框架 | React 18 + TypeScript | 管理控制台 + Chat UI |
| UI 库 | Ant Design / shadcn/ui | 组件库 |
| 状态管理 | Zustand | 轻量状态管理 |
| 工作流编辑器 | React Flow | DAG 编排可视化 |
| 通信 | SSE / WebSocket | 流式输出实时推送 |

---

## 9. 部署架构

### 9.1 Kubernetes 服务清单

```
Kubernetes Cluster
├── agent-console-web         (前端控制台)
├── agent-api-service         (Agent 管理 CRUD、配置、发布)
├── model-gateway-service     (模型路由、限流、缓存 — 独立服务)
├── agent-runtime-service     (Agent 执行引擎)
├── session-service           (会话 & 记忆 — 独立服务)
├── tool-runtime-service      (工具注册与调用、沙箱管理)
├── rag-service               (知识库检索)
├── document-worker           (文档解析与 Embedding 生成)
├── embedding-worker          (批量向量化异步任务)
├── workflow-worker           (Temporal Worker)
├── observability-service     (Trace、日志、成本分析)
├── postgres                  (StatefulSet)
├── redis                     (StatefulSet)
├── rabbitmq                  (StatefulSet)
├── minio                     (StatefulSet)
├── temporal-server           (Temporal + Temporal UI)
├── prometheus + grafana      (监控)
└── jaeger                    (链路追踪)
```

### 9.2 服务职责矩阵

| 服务 | 职责 | 扩缩容策略 |
|------|------|-----------|
| agent-api-service | Agent CRUD、Prompt 管理、Tool 注册、Policy 配置 | 按请求量 |
| model-gateway-service | 多模型适配、路由、语义缓存、限流 | 按并发 LLM 调用 |
| agent-runtime-service | Agent 执行、Guardrails、Trace | 按活跃 Agent Run 数 |
| session-service | 会话上下文、历史消息、记忆检索 | 按活跃会话数 |
| tool-runtime-service | 工具调用、沙箱创建/销毁 | 按工具调用量 |
| rag-service | 向量检索、Rerank、Citation | 按检索 QPS |
| document-worker | 文档解析、Embedding 生成 | 按上传量 |
| workflow-worker | Temporal Activity 执行 | 按工作流实例数 |

---

## 10. 执行计划

### 10.1 阶段总览（融合：Hermes 阶段框架 + GPT5.5 交付物 + 团队配置）

| Phase | 周期 | 目标 | 里程碑 |
|-------|------|------|--------|
| 0：基础骨架 | W1-4 | 基础设施 + 核心链路打通 | Hello Agent |
| 1：核心引擎 | W5-10 | 生产级 Agent 运行能力 | 生产级引擎 |
| 2：知识体系 | W11-14 | 知识库 + RAG 全链路 | 知识就绪 |
| 3：进阶能力 | W15-20 | 编排 + 安全 + 可观测 | 全功能内测 |
| 4：产品化 | W21-24 | 多租户 + 治理 + 发布 | 公开发布 |

### 10.2 Phase 0：基础骨架（W1-4）

**目标**：搭建基础设施，跑通第一个 Agent 端到端链路。

**交付物**：
1. Monorepo 项目结构 + Spring Boot 多模块
2. API Gateway + Auth Service（OAuth2/OIDC + JWT）
3. Model Gateway MVP（OpenAI + Claude 适配）
4. Agent Runtime MVP（ReAct 循环 + 流式输出）
5. 简单工具调用（HTTP Tool）
6. Agent Run 记录（基础 Trace、Token 统计）
7. 最小前端控制台（Agent 创建 + 简单对话）
8. K8s 部署模板

**技术栈 MVP**：
```
Spring Boot 3 + Spring AI
PostgreSQL + pgvector
Redis
MinIO
RabbitMQ
OpenTelemetry
```

---

### 10.3 Phase 1：核心引擎（W6-10）

**目标**：支持业务系统接入和稳定运行。

**交付物**：
1. Agent Registry 完整 CRUD + 发布状态机（draft/staging/production）
2. Prompt 版本管理 + 变量注入 + 测试集
3. Tool Registry 完整实现（HTTP/DB/MCP/Code 四类）
4. MCP Server 接入 + MCP Gateway
5. Session Service（上下文管理 + 多轮对话）
6. 多租户基础隔离
7. RBAC 权限（Agent 级 + Tool 级）
8. 基础 Guardrails（输入检测 + 输出检查）
9. Human-in-the-Loop（高风险工具审批）
10. 失败重试 + 限流

**引入技术**：
```
Temporal (长任务工作流)
Kubernetes (生产部署)
Prometheus + Grafana
```

---

### 10.4 Phase 2：知识体系（W11-14）

**目标**：完整的知识库和 RAG 能力。

**交付物**：
1. 文档处理管道（上传 → 解析 → 清洗 → 切片 → Embedding）
2. 混合检索（语义 + BM25 + RRF 融合）
3. Rerank 重排序
4. Citation 来源引用
5. Query Rewrite
6. Context Compression
7. 定时同步外部知识源（Temporal Schedule）
8. Knowledge Graph 可选试点（Neo4j — 若资源允许）

---

### 10.5 Phase 3：进阶能力（W15-20）

**目标**：多 Agent 协作、企业级安全和可观测。

**交付物**：
1. Workflow 设计器（React Flow 可视化）
2. 多 Agent 编排（Sequential / Parallel / Supervisor / Debate）
3. A2A 协议兼容
4. 完整 3 层 Guardrails（输入/执行/输出）
5. 沙箱代码执行（K8s Pod 隔离）
6. 成本统计 + Token 预算
7. AgentOps Dashboard（Trace 回放、失败分析）
8. LLM Judge 自动评测
9. 审计报表

---

### 10.6 Phase 4：产品化（W21-24）

**目标**：公开发布就绪。

**交付物**：
1. 完整多租户隔离（Schema 级 + 数据加密）
2. 计费系统（按 Token / 调用次数）
3. API Key 管理 + Developer Portal
4. 压力测试（1000 并发 Agent Run）
5. 安全审计（渗透测试 + 合规检查）
6. 完整文档 + SDK（Java / Python / TypeScript）
7. Agent Marketplace 基础（模板市场）
8. 灾备方案 + SLA 定义

---

### 10.7 推荐落地路线

```
Phase 0 ─── 先做 "Agent管理 + RAG + HTTP Tool + Trace"
               ↓
Phase 1 ─── 再做 "工作流 + MCP + Guardrails + Session"
               ↓
Phase 2 ─── 深化 "知识库 + RAG 全链路"
               ↓
Phase 3 ─── 扩展 "多Agent + A2A + 完整可观测"
               ↓
Phase 4 ─── 产品化 "多租户 + 计费 + Marketplace"
```

> 核心原则：不要一开始做全自动多 Agent。第一版聚焦——Agent 配置可视化、知识库可用、工具调用可控、运行过程可追踪、结果可评估、权限和成本可治理。

---

## 11. 团队配置

### 11.1 角色与人数

| 角色 | 人数 | 核心技能 | 职责 |
|------|------|----------|------|
| 后端工程师 (Java) | 3-4 | Spring Boot / Spring AI / PostgreSQL / Temporal | 核心微服务开发 |
| 前端工程师 | 1-2 | React / TypeScript / React Flow | 管理控制台 + Chat UI + Workflow 编辑器 |
| AI/ML 工程师 | 1 | LLM 集成 / RAG 优化 / Prompt Engineering / Embedding 选型 | AI 能力层 |
| DevOps 工程师 | 1 | K8s / Terraform / CI/CD / Prometheus | 基础设施 + 部署 + 监控 |
| 产品经理 | 1 | B2B 平台经验 / Agent 领域知识 | 需求定义、路线规划、用户反馈 |
| **总计** | **7-9** | | |

### 11.2 关键角色到阶段映射

| Phase | 后端 | 前端 | AI/ML | DevOps | PM |
|-------|------|------|-------|--------|----|
| 0 (W1-4) | 3 (全投入) | 1 | 1 (全投入) | 1 | 1 |
| 1 (W5-10) | 4 (全投入) | 2 | 1 | 1 | 1 |
| 2 (W11-14) | 3 | 1 | 1 (重点) | 1 | 1 |
| 3 (W15-20) | 4 | 2 (全投入) | 1 | 1 | 1 |
| 4 (W21-24) | 3 | 1 | 0.5 | 1 (重点) | 1 |

---

## 12. 关键决策记录

| # | 决策 | 理由 | 替代方案 | 状态 |
|----|------|------|----------|------|
| 1 | 选择 Java/Spring Boot 而非 Python | 团队技术栈 + 企业级稳定性 | Python FastAPI (AI/ML 辅助服务) | ✅ 确定 |
| 2 | 选择 Spring AI 而非 LangChain4j | Spring 官方支持 + MCP 原生集成 | LangChain4j | ✅ 确定 |
| 3 | 选择 Temporal 而非自研 DAG | 工业验证 + 内置可靠性机制 | 自研 DAG (维护成本高) | ✅ 确定 |
| 4 | 选择 pgvector 而非独立向量 DB | 减少运维复杂度 | Milvus / Qdrant | ✅ 确定 |
| 5 | Model Gateway 独立服务 | 多模型路由/限流/缓存独立治理 | 合入 Agent Runtime | ✅ 确定 |
| 6 | Session Service 独立服务 | 跨 Agent 共享上下文 | 绑定 Agent Runtime | ✅ 确定 |
| 7 | MCP 作为工具接入标准 | 生态兼容性 + 标准化 | 自定义协议 | ✅ 确定 |
| 8 | A2A 延后到 Phase 3 | 优先保证核心引擎，多 Agent 互操作非 MVP | Phase 1 引入 | ✅ 确定 |

---

## 13. 风险与缓解

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|----------|
| Temporal 学习曲线 | 开发进度延迟 1-2 周 | 中 | Phase 0 增加 Temporal 培训，MVP 先用简单状态机 |
| Spring AI 1.0 未 GA | API 变动需适配 | 中 | 锁定版本，抽象 Model Gateway 层隔离变化 |
| Token 成本超预期 | 商业化受阻 | 高 | Phase 1 即实现语义缓存 + 成本预算 + 告警 |
| 多 Agent 编排死锁 | 生产故障 | 中 | Temporal 超时自动恢复 + Saga 补偿 + 充分压测 |
| 安全漏洞（Prompt Injection） | 数据泄露 | 高 | Phase 1 即实现输入检测 + 上下文隔离 |
| pgvector 大规模性能瓶颈 | 检索延迟 > 500ms | 低 | Phase 2 评估 Milvus fallback 方案 |
| 团队招聘困难 | 进度延迟 | 中 | Phase 0 用现有团队 + 外聘顾问 |

---

## 附录：方案演进历史

本方案替代以下历史文档，旧文件均已归档：

| 原文档 | 归档位置 |
|--------|----------|
| Hermes 独立方案 | `docs/temp/history/2026-05-13-1638-cloud-agent-platform.hermes.md` |
| GPT5.5 独立方案 | `docs/temp/history/2026-05-13-1638-cloud-agent-platform.gpt55.md` |
| 对比分析 | `docs/temp/comparison/2026-05-13-1645-agent-platform-comparison.md` |

> **本文件是唯一权威的最终方案。所有后续修改在本文件上进行，不再创建衍生版本。**
