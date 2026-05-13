---
title: AI Agent 自动知识沉淀方案
tags:
    - agent
    - knowledge-capture
    - architecture
    - automation
    - rag
    - pgvector
    - index
    - retrieval
    - frontmatter
summary: 语言/框架无关的 AI Agent 知识沉淀 5 层架构方案：触发→捕获→处理→存储→检索，含背景动机、环节实现、流程示例、工程陷阱、参考工具。
created: 2026-05-13
---

# AI Agent 自动知识沉淀方案

> 语言/框架无关设计方案。给定具体技术栈后提供工程实现。

---

## 背景

在与 AI Agent（如 Hermes、Claude Code）的日常协作中，会产生大量有价值的技术讨论：架构决策、排错经验、工具配置技巧、协议选型分析等。这些知识散落在对话历史里，手动整理成本高、易遗漏、难以复用。

需要一套自动化机制，让 Agent 在对话过程中自主判断哪些内容值得沉淀，按统一规范写入知识库，并通过索引让后续会话可检索、可加载——同时保证 Agent 不绕过脚本、不污染目录、不产生碎片。

---

## 1. 整体架构设计

```
                          ┌──────────────────────────────────────┐
                          │         Agent 对话会话               │
                          └──────────────┬───────────────────────┘
                                         │ 每轮回复后
                                         ▼
┌──────────────────────────────────────────────────────────────────┐
│                     L1: 触发层 (Trigger)                          │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ AGENTS.md 规则引擎：长度阈值 / 关键词匹配 / 分类判据       │ │
│  │ Agent 自评估：答案质量、复用价值、时效性                  │ │
│  └─────────────────────────────────────────────────────────────┘ │
└───────────────────────────────┬──────────────────────────────────┘
                                │ 触发 → 进入捕获
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│                     L2: 捕获层 (Capture)                          │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ 内容生成：Markdown + YAML frontmatter                      │ │
│  │ 元数据提取：title, tags, summary, category, created        │ │
│  │ 内容模板：Background → Problem → Solution → Key Points    │ │
│  │           → Risks → Related                                │ │
│  └─────────────────────────────────────────────────────────────┘ │
└───────────────────────────────┬──────────────────────────────────┘
                                │ 写入临时区
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│                     L3: 处理层 (Process)                          │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ 分类路由：按内容特征 → 匹配 category                       │ │
│  │ 去重检查：全文本/语义相似度 → 新文档 or 更新已有           │ │
│  │ 命名规范：yyyy-mm-dd-HHmm-kebab-case.md                    │ │
│  │ 脚本执行：save_ai_note.sh → 原子 cp 到目标目录            │ │
│  └─────────────────────────────────────────────────────────────┘ │
└───────────────────────────────┬──────────────────────────────────┘
                                │ 持久化
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│                     L4: 存储层 (Storage)                          │
│  ┌───────────────────┐  ┌──────────────────┐  ┌───────────────┐ │
│  │ 文件存储           │  │ 向量存储 (可选)   │  │ 索引存储      │ │
│  │ docs/ai/{category}/│  │ PostgreSQL+       │  │ INDEX.md × 2 │ │
│  │ docs/manual/{cat}/ │  │ pgvector          │  │               │ │
│  └───────────────────┘  └──────────────────┘  └───────────────┘ │
└───────────────────────────────┬──────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│                     L5: 检索层 (Retrieval)                        │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ Lazy-load: 先 INDEX.md → 匹配 → 按需读文件                │ │
│  │ 混合检索: keyword (ripgrep) + semantic (pgvector)         │ │
│  │ 上下文注入: 匹配文档 → Agent 系统提示 / 工具上下文        │ │
│  └─────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

### 架构设计原则

| 原则 | 说明 |
|------|------|
| **触发与执行分离** | 在对话中评估触发条件，沉淀操作异步执行，不阻塞对话响应 |
| **存储与检索解耦** | 文件存储保证可读性和版本控制，向量存储提供语义检索，互不绑定 |
| **索引先行** | 所有检索从 INDEX.md 开始，避免全量扫描。索引是知识库的"目录页" |
| **双库双索引** | `docs/ai/` + `docs/manual/` 各有独立 INDEX.md，按任务类型分流 |
| **渐进增强** | 最小闭环 = 文件 + INDEX.md，可选叠加 pgvector、全文搜索、GraphRAG |

---

## 2. 关键实现环节

### 2.1 触发判断机制

触发规则定义在项目根目录 `AGENTS.md` 的 `## AI Knowledge Capture` 节。
Agent 在每次回复后按 5 条判据自评：

```
1. 答案是否包含通用性强、可复用的知识？           → 是 → 触发
2. 是否涉及系统设计或架构决策？                   → 是 → 触发
3. 是否包含 bug 修复、事故处理、排错经验？        → 是 → 触发
4. 是否与 Agent 工作流/自动化相关？               → 是 → 触发
5. 回复是否超过 300 字且具有长期价值？            → 是 → 触发
```

**反触发（明确不保存）**：
- 临时路径、一次性指令
- 已在知识库中覆盖的重复内容
- 纯对话性质、无技术含量的闲聊

### 2.2 内容格式化

严格遵循 `AGENTS.md` 的 `## Markdown Template` 节。每个保存的 markdown 文件必须包含 YAML frontmatter：

```markdown
---
title: 简洁的知识标题
tags:
    - tag1
    - tag2
    - tag3
summary: 一句话描述，不超过 200 字
created: YYYY-MM-DD
---

# Background

# Problem

# Solution

# Key Points

# Risks

# Related
```

> **格式约定**：`tags` 使用 YAML 列表（每行 `- tag`），不用行内数组 `[a, b, c]`，与 `docs/ai/INDEX.md` 和 `AGENTS.md` 模板保持一致。

### 2.3 分类路由

| 内容特征 | → category |
|---------|-----------|
| 微服务拆分、系统边界、架构图 | architecture |
| Java/Spring Boot/Gradle/DB/API 实现 | backend |
| React/Vue/Angular/UI/UX 实现 | frontend |
| Hermes/Claude Code/Agent 工作流 | agents |
| 向量数据库、embedding、检索增强 | rag |
| 提示词模版、System Prompt 设计 | prompts |
| 技术选型决策、ADR | decisions |
| Bug 修复、报错解决、踩坑记录 | troubleshooting |

### 2.4 去重策略

保存前必须去重，避免知识碎片化：

```
Step 1: 关键词匹配
  → 在 docs/ai/{category}/ 和 docs/manual/{category}/ 目录用 ripgrep 搜索已有文件的标题和 frontmatter

Step 2: 如果找到相似候选
  → 读取候选文件完整内容
  → AI 判断是新知识（新建）还是增量补充（更新现有文件）

Step 3: 如果是增量补充
  → 用 patch 工具在现有文件中追加内容，不新建文件
  → 更新原文件的 last_updated 字段
  → 同步更新对应 INDEX.md 中的 last_updated
```

### 2.5 保存管道（5 步）

完全对等 `AGENTS.md` `## Save Flow` 的 5 个步骤：

```
Step 1: 准备临时目录
  mkdir -p .tmp/ai
  write_file .tmp/ai/note.md

Step 2: 选定分类
  根据内容特征匹配 category（见 §2.3）

Step 3: 选定短横线命名主题
  如 hermes-auto-knowledge、spring-transactional-pitfall

Step 4: 执行保存脚本
  bash scripts/save_ai_note.sh <category> <topic> .tmp/ai/note.md
  → 脚本自动：时间戳命名 → cp 到目标目录 → 输出最终路径
  → 严禁绕过脚本直接用 write_file/mv 写 docs/ai/ 或 docs/manual/

Step 5: 更新索引目录
  在 docs/ai/INDEX.md（或 docs/manual/INDEX.md，取决于知识归属）追加 Entry，
  格式见 AGENTS.md 的 ## Index Example 节。
```

**关键约束**：
- 始终使用 `scripts/save_ai_note.sh`，绝不手动写文件到 `docs/ai/`
- 脚本控制命名、时间戳和最终路径，保证格式统一

### 2.6 索引更新（Step 5 详解）

每次新知识保存后，必须在对应的 INDEX.md 同步追加条目。
格式严格遵循 `AGENTS.md` 的 `## Index Example` 节定义（Entry 格式）：

```markdown
## Entry: {topic}

- path: `docs/ai/{category}/{timestamp}-{topic}.md`
- category: `{category}`
- tags:
    - `tag1`
    - `tag2`
- summary: {一句话摘要}
- use_when:
    - {用户触发场景 1}
    - {用户触发场景 2}
- related:
    - `docs/ai/{category}/{related-file}.md`
- priority: `high` | `medium` | `low`
- last_updated: `YYYY-MM-DD`
- status: `active`
```

> **提示**：`docs/ai/INDEX.md` 和 `docs/manual/INDEX.md` 均采用此格式。
> `use_when` 字段是 Agent 懒加载的关键——Agent 根据此项判断何时需要读取对应文件，务必填写准确。

### 2.7 可选增强：向量索引

```
新文件保存
  ↓
文件监控 (FS watch / git hook / CI / cron)
  ↓
chunk_text(content, chunk_size=1200, chunk_overlap=200)
  ↓
embedding_model.encode(chunk) → vector[1536]
  ↓
INSERT INTO ai_docs (file_path, chunk_index, content, embedding)
  ↓
INDEX.md → 关键词检索  |  pgvector → 语义检索  |  两者组合 = 混合检索
```

---

## 3. 典型流程示例

### 示例 A：Bug 排错自动沉淀

```
[用户] Spring Boot 事务不回滚，加了 @Transactional 也不管用

[Agent 回答，超过 300 字]
  分析根因：同类方法自调用导致 AOP 代理失效 → 给出了 3 种修复方案

[Agent 自评]
  ✅ 排错经验（条件3）  ✅ 超过 300 字（条件5）  ✅ 可复用

[Agent 执行 5 步保存流程]
  Step 1: mkdir -p .tmp/ai
           write_file .tmp/ai/note.md
  Step 2: 分类 → troubleshooting
  Step 3: topic → spring-transactional-self-invocation
  Step 4: bash scripts/save_ai_note.sh troubleshooting spring-transactional-self-invocation .tmp/ai/note.md
           → Saved: docs/ai/troubleshooting/2026-05-13-1400-spring-transactional-self-invocation.md
  Step 5: 更新 docs/ai/INDEX.md，追加 Entry
```

### 示例 B：架构决策同步

```
[用户] 我们决定用户服务拆成 auth 和 profile 两个微服务

[Agent 回答]
  分析拆分理由、边界、数据共享策略 → 生成架构文档

[Agent 自评]
  ✅ 架构设计（条件2）  ✅ 长期价值（条件5）

[Agent 执行 5 步保存流程]
  Step 1: 写入 .tmp/ai/note.md（含 frontmatter）
  Step 2: 分类 → architecture
  Step 3: topic → user-service-split-adr
  Step 4: bash scripts/save_ai_note.sh architecture user-service-split-adr .tmp/ai/note.md
  Step 5: 更新 docs/ai/INDEX.md
```

### 示例 C：知识增量更新

```
[用户] 上次那个 @Transactional 方案，再加一种：用 @Async 解耦自调用

[Agent]
  1. 先去重 → 搜索 troubleshooting + transactional
  2. 找到 docs/ai/troubleshooting/...-spring-transactional-self-invocation.md
  3. 判断：这是对已有知识的补充，不是全新知识
  4. 用 patch 工具在现有文件 #Solution 部分追加第 4 种方案
  5. 更新 frontmatter 的 last_updated
  6. 更新 docs/ai/INDEX.md 对应 Entry 的 last_updated
```

---

## 4. 优势总结

1. **零手动成本** — Agent 自主判断是否沉淀，无需人工干预
2. **分类清晰** — 8 大类别覆盖技术知识域，按需检索命中率高
3. **命名规范** — 时间戳 + kebab-case 主题，可排序、可 grep
4. **路径一致** — 脚本强制统一格式，避免人为操作差异
5. **按需沉淀** — 不是全量保存，只保留高价值内容，知识库精炼
6. **索引驱动** — INDEX.md 作为检索入口，Agent 懒加载，避免全量扫描

---

## 5. 工程化注意事项

### 5.1 必须遵守

| 规则 | 原因 |
|------|------|
| 绝不绕过脚本直接写文件 | 保证命名规范和时间戳一致性 |
| 保存前必须去重搜索 | 防止知识碎片化和重复 |
| 保存后必须更新对应 INDEX.md（Step 5） | 索引是检索的唯一入口，不一致则知识不可发现 |
| 一个 topic 一个文件 | 避免巨型文件，便于按需加载 |
| 优先增量更新而非重复创建 | 同一主题的知识应收敛到同一文件 |
| frontmatter 必须包含 title/tags/summary/created | `AGENTS.md` `## Markdown Template` 节的硬性要求 |

### 5.2 常见陷阱

1. **过度沉淀** — 每轮都保存，知识库膨胀、噪声大。严格按 5 条触发条件过滤。
2. **去重不足** — 同一主题多个文件，检索时漏掉关键信息。保存前强约束搜索。
3. **索引滞后** — 文件写了但 INDEX.md 未更新，知识不可发现。
4. **分类错误** — 排错经验放入 architecture 类，降低检索命中率。
5. **双库混淆** — 技术实现细节放入了 docs/manual/，用户手册放入了 docs/ai/。
6. **frontmatter 缺失** — 保存文件缺少 YAML frontmatter，与 AGENTS.md 规定不符，后续检索工具可能无法解析。
7. **脚本 bug 被忽略** — `scripts/save_ai_note.sh` 曾被文件名片段污染 sed 正则，导致保存失败。Agent 遇到脚本报错应主动检查并修复，而非绕过脚本。

### 5.3 性能考量

| 环节 | 延迟 | 优化手段 |
|------|------|---------|
| 去重搜索 (ripgrep) | < 100ms | 限定 category 目录范围 |
| 文件写入 (.tmp/) | < 10ms | 本地 I/O，可忽略 |
| 脚本移动 (cp) | < 10ms | 同盘操作 |
| INDEX.md patch 更新 | < 10ms | 纯文本，只改单一 Entry |
| 向量索引 (可选) | 100-500ms/chunk | 批量处理 + 增量模式 |
| 语义检索 (可选) | 50-200ms | ivfflat/prob 索引 + limit |

**建议**：文件层（Step 1-5）在对话中同步完成；向量索引异步触发（cron / watchdog），不阻塞对话。

### 5.4 安全边界

- 知识文件只保存 Agent 自己生成的内容，不保存用户原始输入中的敏感信息
- 需要人工审核的内容：API key、密码、内网地址等 → 自动脱敏或跳过
- 脚本权限：`save_ai_note.sh` 仅可写入 `docs/ai/` 和 `docs/manual/` 目录

### 5.5 扩展性预留

```
当前阶段（最小闭环）：
  AGENTS.md 规则 → 文件保存 → INDEX.md × 2 更新 → ripgrep 检索

中期增强（语义检索）：
  + pgvector → 混合检索

远期增强（知识图谱）：
  + GraphRAG → 关系推理 → 多跳检索
```

---

## 6. 参考

### 6.1 核心依赖

| 工具 | 用途 | 备注 |
|------|------|------|
| `scripts/save_ai_note.sh` | 文件命名和归档 | 自建脚本，< 40 行，曾修复过 sed 正则污染 bug |
| `rg` (ripgrep) | 关键词去重搜索 | 已有，无需额外安装 |
| Markdown + YAML frontmatter | 内容格式 | 通用标准 |

### 6.2 可选依赖（语义检索增强）

| 工具 | 用途 | 备注 |
|------|------|------|
| PostgreSQL + pgvector | 向量存储与检索 | Docker Compose 一键启动 |
| OpenAI text-embedding-3-small | 文本向量化 | 或本地 sentence-transformers |
| 可选本地模型 | all-MiniLM-L6-v2 (384d) | 离线可用，适合隐私敏感场景 |

### 6.3 参考项目与论文

| 来源 | 要点 |
|------|------|
| **Anthropic "Building Effective Agents"** (2024) | workflow vs agent 的区分，orchestrator-worker 推荐 |
| **MemGPT / Letta** (2023-2024) | LLM OS 概念，长期记忆管理，认知架构 |
| **LangChain Memory** | ConversationBufferMemory、VectorStoreRetrieverMemory |
| **LangGraph Checkpointing** | Agent 状态持久化与恢复 |
| **arXiv:2601.20404** | AGENTS.md 对 AI Coding Agent 效率影响的实证研究 |
| **NousResearch Hermes Agent Issues #531** | User Workspace & Knowledge Base 持久化讨论 |
| **OpenAI Assistants File Search** | 托管的文件索引 + 向量检索 |
| **GraphRAG (Microsoft)** | 知识图谱增强的 RAG，适用于多跳推理 |

### 6.4 与同类方案的对比

| 方案 | 文件 | 向量 | 索引 | Agent 集成 | 复杂度 |
|------|------|------|------|-----------|--------|
| **本方案** | ✅ | 可选 | INDEX.md × 2 | 原生 | 低 |
| OpenAI Assistants | ✅ | ✅ | 自动 | 原生 | 低（托管） |
| LangChain Memory | - | ✅ | - | 需编码 | 中 |
| MemGPT/Letta | ✅ | ✅ | 自动 | 需适配 | 高 |
| 纯 pgvector | - | ✅ | - | 需编码 | 中 |
| Obsidian + Copilot | ✅ | ✅ | 标签系统 | 分离 | 低 |

### 6.5 本项目关键文件

- `AGENTS.md` — 定义触发规则、保存流程、模板格式
- `scripts/save_ai_note.sh` — 核心保存脚本
- `docs/ai/INDEX.md` — 技术知识库索引
- `docs/manual/INDEX.md` — 用户手册知识库索引
- `docs/ai/` — 知识库根目录

---

> **下一步**：当用户给出具体编程语言（Java/Python/Go/...）和技术栈（Spring Boot/FastAPI/...），输出：
> 1. 具体代码实现（save 脚本/索引更新/向量化/检索 API）
> 2. 目录结构和配置文件
> 3. 与该技术栈的集成方式（如 Spring Boot 的 AOP 拦截、FastAPI 的 middleware 等）
