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
# Agent Instructions

## AI Knowledge Base Loading Rule

This project has **two** AI knowledge bases at:
- `~/ai-workspace/docs/ai/` (AI Automatic accumulation of knowledge)
- `~/ai-workspace/docs/manual/` (User Artificial accumulation of knowledge)

The agent must not load all knowledge files by default.

Instead, follow this lazy-loading workflow:

1. Read both index files (if they exist):
   - `~/ai-workspace/docs/ai/INDEX.md`
   - `~/ai-workspace/docs/manual/INDEX.md`

2. Use both `INDEX.md` files as knowledge catalogs.

3. Based on the user request, identify relevant content from **either** knowledge base using:
   - category
   - tags
   - summary
   - file path

4. Load only the matching markdown files. Prefer loading from the knowledge base that has the most relevant match.

5. If no relevant entry is found in both `INDEX.md` files, optionally search both directories:

```bash
rg -n --ignore-case "<keyword>" ~/ai-workspace/docs/ai ~/ai-workspace/docs/manual
```

6. Prefer project knowledge over generic answers. When both knowledge bases contain relevant information, prefer:
    - `~/ai-workspace/docs/manual/` for user-facing manuals, guides, and operational documentation
    - `~/ai-workspace/docs/ai/` for technical architecture, backend, agents, RAG, prompts, decisions, and troubleshooting

7. If new reusable knowledge is produced, determine which knowledge base it belongs to:
    - Save under `~/ai-workspace/docs/ai/<category>/<yyyy-mm-dd>-<topic>.md` for technical/development knowledge
    - Save under `~/ai-workspace/docs/manual/<category>/<yyyy-mm-dd>-<topic>.md` for user manuals, guides, or operational docs

8. After saving a new note, update the corresponding `INDEX.md` file in the same directory.

## Knowledge Categories

### For `~/ai-workspace/docs/ai/`

- `architecture`: system design, architecture
- `backend`: Java, Spring Boot, Gradle, DB, APIs
- `agents`: Hermes, Claude Code, workflows, automation
- `rag`: embeddings, vector DB, retrieval
- `prompts`: prompt engineering, prompt rules
- `decisions`: ADRs, trade-offs, technical decisions
- `troubleshooting`: bugs, incidents, debugging

### For `~/ai-workspace/docs/manual/`

- `user-guides`: end-user documentation, how-to guides
- `operations`: deployment, monitoring, backup, recovery
- `faq`: frequently asked questions
- `onboarding`: new user setup, installation, configuration
- `reference`: API references, CLI commands, configuration specs

(Actual categories may be defined in `~/ai-workspace/docs/manual/INDEX.md`)

## Knowledge Loading Policy

Do not read all files in `~/ai-workspace/docs/ai/` or `~/ai-workspace/docs/manual/`.

Always start from both `INDEX.md` files:
- `~/ai-workspace/docs/ai/INDEX.md`
- `~/ai-workspace/docs/manual/INDEX.md`

Only read detailed markdown files when their path appears relevant to the current task.

When both knowledge bases have relevant information, prioritize based on the task type:
- **Technical development tasks** → prefer `~/ai-workspace/docs/ai/`
- **User-facing documentation or operational tasks** → prefer `~/ai-workspace/docs/manual/`
```
