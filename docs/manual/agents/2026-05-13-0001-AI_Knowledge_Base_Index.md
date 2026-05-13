---
title: AI 知识库索引
tags:
    - knowledge-base
    - index
    - lazy-loading
summary: 按关键词和标签组织的知识库索引条目，Agent 匹配关键词后按需加载对应文件。
created: 2026-05-13
---

# AI Knowledge Base Index

> 本索引用于 AI 智能体懒加载知识库。  
> 使用方式：根据用户问题匹配关键词 → 找对应文件 → 读取详情。

## 索引条目

### [architecture/2026-01-15-microservice-boundary.md](architecture/2026-01-15-microservice-boundary.md)
- **日期**: 2026-01-15
- **分类**: architecture
- **标签**: `微服务` `领域驱动设计` `边界划分` `防腐层`
- **关键词**: 服务拆分、聚合根、限界上下文、DDD
- **摘要**: 微服务拆分边界的5条原则，以及3个反模式案例。基于实际电商项目总结。

### [backend/2026-02-10-spring-transaction.md](backend/2026-02-10-spring-transaction.md)
- **日期**: 2026-02-10
- **分类**: backend
- **标签**: `Spring Boot` `事务` `@Transactional` `回滚`
- **关键词**: 传播机制、隔离级别、rollbackFor、自调用、代理模式
- **摘要**: Spring 事务失效的7种场景、正确回滚姿势、声明式与编程式事务对比。

### [backend/2026-03-01-gradle-multi-module.md](backend/2026-03-01-gradle-multi-module.md)
- **日期**: 2026-03-01
- **分类**: backend
- **标签**: `Gradle` `多模块` `构建` `Kotlin DSL`
- **关键词**: settings.gradle、buildSrc、复合构建、依赖管理、构建缓存
- **摘要**: 多模块 Gradle 项目的组织方式、通用配置抽取、构建时间从3分钟降到40秒的优化过程。

### [decisions/2026-02-20-cache-strategy-ADR.md](decisions/2026-02-20-cache-strategy-ADR.md)
- **日期**: 2026-02-20
- **分类**: decisions
- **标签**: `ADR` `缓存` `Redis` `Caffeine`
- **关键词**: 多级缓存、缓存穿透、缓存雪崩、内存命中率
- **摘要**: 技术决策记录：为什么采用本地缓存(Caffeine) + 分布式缓存(Redis)两层架构，替代单一 Redis。

### [troubleshooting/2026-03-15-outofmemory-heap-dump.md](troubleshooting/2026-03-15-outofmemory-heap-dump.md)
- **日期**: 2026-03-15
- **分类**: troubleshooting
- **标签**: `OOM` `内存泄漏` `MAT` `Heap Dump`
- **关键词**: -Xms -Xmx、GC overhead、线程栈、livedata
- **摘要**: 生产环境 OOM 事故复盘：现象 → 抓堆 → MAT 分析 → 定位到 ThreadLocal 未清理 → 修复与预防。

### [rag/2026-03-10-vector-db-choice.md](rag/2026-03-10-vector-db-choice.md)
- **日期**: 2026-03-10
- **分类**: rag
- **标签**: `向量数据库` `选型` `Milvus` `Qdrant` `Pgvector`
- **关键词**: HNSW、IVF_FLAT、recall@10、QPS、成本对比
- **摘要**: 向量数据库选型对比评测：Milvus (高吞吐) vs Pgvector (低运维) vs Qdrant (云原生)，最终选择方案及依据。

### [agents/2026-01-20-hermes-workflow.md](agents/2026-01-20-hermes-workflow.md)
- **日期**: 2026-01-20
- **分类**: agents
- **标签**: `Hermes` `工作流` `DAG` `Agent编排`
- **关键词**: 计划-执行-观察、工具调用、错误重试、LLM Router
- **摘要**: Hermes 智能体工作流设计模式：顺序、并行、条件分支、循环的配置示例与监控。

### [prompts/2026-04-01-few-shot-prompting.md](prompts/2026-04-01-few-shot-prompting.md)
- **日期**: 2026-04-01
- **分类**: prompts
- **标签**: `Few-shot` `提示工程` `结构化提示`
- **关键词**: 示例选择、格式约束、角色扮演、CoT
- **摘要**: Few-shot 提示的设计模式、标注示例、负面约束（do's and don'ts）及模板库。
