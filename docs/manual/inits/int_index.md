# 初始化-知识库-索引目录(`INDEX.md`)

每次知识自动沉淀后，更新索引目录 `docs/ai/INDEX.md` 和 `docs/manual/INDEX.md`，记录新知识的来源、内容摘要和标签。这样 Agent 就能快速定位相关知识，提升回答效率。

## 文件路径

```text
docs/ai/INDEX.md
```

## 文件内容示例

```md
# AI Knowledge Index

  > Central registry for reusable AI/project knowledge.
  > Agents must read this file first before loading detailed notes.

---  
  
## Entry: claude-code-knowledge-loading

- path: `docs/ai/agents/2026-05-13-claude-code-knowledge-loading.md`
- category: `agents`
- tags:
    - `claude-code`
    - `codex`
    - `knowledge-base`
    - `lazy-loading`
    - `rag`
- summary: How coding agents lazily load markdown knowledge using INDEX.md.
- use_when:
    - User asks about Claude Code knowledge loading
    - User asks about AGENTS.md
    - User asks about AI memory architecture
    - User asks about lazy-loading markdown knowledge
- related:
    - `docs/ai/rag/2026-05-13-vector-retrieval.md`
- priority: `high`
- last_updated: `2026-05-13`
- status: `active`

---

## Entry: springboot-ai-log-writer

- path: `docs/ai/backend/2026-05-13-springboot-ai-log-writer.md`
- category: `backend`
- tags:
    - `spring-boot`
    - `postgresql`
    - `async`
    - `queue`
    - `logging`
- summary:
  Async AI HTTP log writer using queue buffering and batch DB writes.
- use_when:
    - User asks about AI logging
    - User asks about async persistence
    - User asks about PostgreSQL log writing
- related:
    - `docs/ai/architecture/2026-05-13-ai-observability.md`
- priority: `medium`
- last_updated: `2026-05-13`
- status: `active`
```

## 生效过程

```text
用户提问
  ↓
Coding Agent 读取 CLAUDE.md / AGENTS.md
  ↓
确定 知识库 的 存储位置(例如:`docs/ai/INDEX.md`) 和 索引目录(例如:`docs/ai/INDEX.md`)
  ↓
加载 索引目录(INDEX.md)
  ↓
根据用户问题判断相关 category / title / tag / summary, 按需读取相关 markdown 知识文档
  ↓
基于 知识文档 来 回答 或 修改代码
```
