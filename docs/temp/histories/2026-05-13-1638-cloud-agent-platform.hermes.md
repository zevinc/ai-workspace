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

# 云端通用 Agent 平台架构设计

## 一、整体架构（6 层微服务）

```
接入层        → API Gateway (Spring Cloud Gateway)
引擎层        → Agent Runtime + Tool Registry + Orchestration
模型层        → Model Gateway (多厂商适配/路由/限流)
知识层        → RAG Service + Vector DB + Knowledge Graph
会话层        → Session Service + Memory Service
基础设施层    → PostgreSQL + Redis + RabbitMQ + MinIO + Prometheus
```

## 二、9 大模块功能设计

### 1. Agent Runtime Service（核心引擎）
- Agent 循环引擎：ReAct / Plan-Execute / Reflection
- Prompt 模板管理 + 版本控制
- 上下文窗口管理（token 计算/自动压缩）
- 流式输出 (SSE/WebSocket)
- Human-in-the-Loop 中断与恢复
- 沙箱执行隔离 (Docker/K8s Pod)

### 2. Model Gateway Service（模型网关）
- 多厂商统一抽象 (OpenAI/Anthropic/Gemini/本地)
- 智能路由（成本/能力/延迟策略）
- Fallback 链 + 语义缓存
- 多维度限流配额

### 3. Tool Registry Service（工具注册中心）
- MCP 协议兼容
- 内置工具库 + 自定义函数工具
- 工具自动发现 + 语义匹配推荐
- 权限控制 + 执行沙箱

### 4. Knowledge & RAG Service（知识服务）
- 文档管道：解析 → 分块 → 向量化
- pgvector 混合检索（语义 + 关键词 + RRF 融合）
- Knowledge Graph（Neo4j，可选）
- 增量索引 + 多模态支持

### 5. Orchestration Service（编排引擎）
- DAG 工作流 + 可视化编辑
- 多 Agent 协作模式：Sequential/Parallel/Router/Debate/Supervisor
- 人工审批节点 + 模板市场

### 6. Session & Memory Service（会话记忆）
- 短期记忆 (Redis/PostgreSQL)
- 长期记忆 (向量化存储)
- 记忆检索 + LRU 遗忘策略

### 7. Auth & Tenant Service（认证多租户）
- OAuth2/OIDC + RBAC + ABAC
- API Key 管理
- 数据库级/Schema 级多租户隔离

### 8. Observability Service（可观测性）
- OpenTelemetry 全链路追踪
- Prometheus + Grafana 监控
- Token 成本追踪
- Agent 运行回放调试

## 三、技术选型

| 层 | 选型 |
|----|------|
| 语言/框架 | Java 21 + Spring Boot 3.x + Spring Cloud |
| API Gateway | Spring Cloud Gateway |
| ORM | Spring Data JPA + QueryDSL |
| 主数据库 | PostgreSQL 16 |
| 向量数据库 | pgvector (PG 插件) |
| 缓存 | Redis Stack |
| 消息队列 | RabbitMQ |
| 对象存储 | MinIO / S3 |
| LLM SDK | LangChain4j |
| 容器编排 | Kubernetes |
| 监控追踪 | Prometheus + Grafana + OpenTelemetry + Jaeger |
| 前端 | React 18 + TypeScript + Ant Design + React Flow |

## 四、执行计划（24 周 / 6 个月）

| Phase | 周期 | 任务 | 里程碑 |
|-------|------|------|--------|
| 0：基础骨架 | W1-4 | API Gateway / Auth / Model Gateway / Agent MVP | Hello Agent |
| 1：核心引擎 | W5-10 | Tool Registry / Session / Prompt 管理 | 生产级引擎 |
| 2：知识体系 | W11-14 | RAG Service / Knowledge Graph | 知识就绪 |
| 3：进阶能力 | W15-20 | Orchestration / Observability / 前端 | 全功能内测 |
| 4：产品化 | W21-24 | 多租户/计费/压测/文档/SDK | 公开发布 |

## 五、团队配置

- 后端 (Java): 3-4 人
- 前端: 1-2 人
- AI/ML: 1 人
- DevOps: 1 人
- PM: 1 人
- 总计: 7-9 人

## 六、关键决策

1. **Java 而非 Python**：团队技术栈匹配 + 企业级稳定性，Python 仅作为 AI/ML 辅助服务
2. **pgvector 而非独立向量 DB**：减少运维复杂度，PostgreSQL 一站式
3. **MCP 协议**：Agent-Tool 通信标准，保证工具生态兼容性
4. **混合检索优于纯语义检索**：RRF 融合保证精确匹配和语义理解兼顾

## 七、风险

- LangChain4j 生态不如 Python LangChain 成熟，可能需要自行封装部分能力
- 多 Agent 编排的稳定性和死锁问题需要充分测试
- Token 成本控制是商业化关键，语义缓存命中率需要持续优化
