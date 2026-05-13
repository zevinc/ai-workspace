---
title: Agent 知识库使用规范
tags:
    - agent
    - knowledge-base
    - lazy-loading
    - INDEX.md
    - documentation
    - CLAUDE.md
    - AGENTS.md
summary: 描述 Agent（Claude Code 等）如何按需加载两个知识库的流程规范：先读索引目录、按关键词匹配 category/tags/summary、按需加载具体文档，含 CLAUDE.md/AGENTS.md 推荐写法、8 个 ai/ 分类 + 5 个 manual/ 分类体系、以及双库优先级策略。
created: 2026-05-13
---

# 初始化-智能体-使用知识库

## 加载流程

```text
Agent 启动
  ↓
读取 CLAUDE.md / AGENTS.md
  ↓
只加载 索引目录
  ↓
根据 用户问题 判断相关的 category / tag / summary
  ↓
按需读取具体 md 知识文档
  ↓
基于 知识文档 回答 或 修改代码
```

## CLAUDE.md / AGENTS.md 推荐写法

```markdown
## AI Knowledge Base Loading Rule

This project has **two** knowledge bases:

| Path | Purpose |
|------|---------|
| `~/ai-workspace/docs/ai/` | AI‑accumulated technical knowledge |
| `~/ai-workspace/docs/manual/` | User‑written manuals & operational docs |

The agent must **not** load all files by default. Follow this lazy‑loading workflow:

### 1. Start from index files

Read both index files (if they exist):
- `~/ai-workspace/docs/ai/INDEX.md`
- `~/ai-workspace/docs/manual/INDEX.md`

### 2. Find relevant content

Use the `INDEX.md` files as catalogs. Locate relevant entries by:
- Category
- Tags
- Summary
- File path

### 3. Load only matching files

Prefer the knowledge base with the most relevant match.

### 4. Fallback search

If no entry is found in either index, optionally search both directories:

```bash
rg -n --ignore-case "<keyword>" ~/ai-workspace/docs/ai ~/ai-workspace/docs/manual
```

### 5. Create new knowledge (if applicable)

Prefer project knowledge over generic answers. When new reusable knowledge is produced, save it to the appropriate base: `~/ai-workspace/docs/ai/<category>/<yyyy-mm-dd>-<topic>.md`

### 6. Update index

After saving a new note, update the corresponding `INDEX.md` in the same directory.

## Knowledge Categories (`~/ai-workspace/docs/ai/`)

| Category | Description |
|----------|-------------|
| `architecture` | System design, architecture |
| `backend` | Java, Spring Boot, Gradle, DB, APIs |
| `agents` | Hermes, Claude Code, workflows, automation |
| `rag` | Embeddings, vector DB, retrieval |
| `prompts` | Prompt engineering, rules |
| `decisions` | ADRs, trade-offs, technical decisions |
| `troubleshooting` | Bugs, incidents, debugging |

> Additional categories may be defined in `~/ai-workspace/docs/manual/INDEX.md`.

## Loading Policy Summary

- ✅ Always start from both `INDEX.md` files
- ✅ Only read detailed markdown files when relevant
- ❌ Never read all files in knowledge base directories
```
