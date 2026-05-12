---
title: Hermes 自动知识沉淀方案
tags: [hermes, knowledge-capture, automation, ai-workflow]
summary: 基于 AGENTS.md 规则，通过 AI 自动识别并保存高价值知识到 docs/ai/ 目录的完整方案
created: 2026-05-13
---

# 背景

在与 Hermes Agent 的日常协作中，会产生大量有价值的技术讨论、架构决策和排错经验。手动整理这些内容成本高、易遗漏。需要一套自动化机制，让 AI 在对话过程中自主判断哪些内容值得沉淀，并按照规范写入知识库。

# 方案

## 触发条件（五选一即可触发）

AI 在每条回复完成后评估是否满足以下任一条件：

1. **重要或可复用** — 回答包含通用性强的知识
2. **架构或设计相关** — 系统设计、架构决策
3. **排错或故障排查** — bug 修复、事故处理
4. **Agent 工作流或自动化** — Hermes/Claude Code 配置、工作流
5. **超过 300 字且具有长期价值** — 长回复且不过时

明确排除：临时性、低价值、重复性内容。

## 分类体系

| 类别 | 用途 |
|------|------|
| architecture | 系统设计、架构 |
| backend | Java、Spring Boot、Gradle、数据库、API |
| agents | Hermes、Claude Code、工作流、自动化 |
| rag | 嵌入、向量数据库、检索 |
| prompts | 提示工程、提示规则 |
| decisions | ADR、权衡、技术决策 |
| troubleshooting | Bug、事故、调试 |

## 保存流程

1. 确保 `.tmp/ai/` 目录存在
2. 将笔记写入 `.tmp/ai/note.md`
3. 选择合适的类别（category）和短横线命名主题（topic）
4. 执行：`scripts/save_ai_note.sh <category> <topic> .tmp/ai/note.md`

脚本会自动处理：
- 生成带时间戳的文件名（格式：`YYYY-MM-DD--<topic>.md`）
- 将文件移动到 `docs/ai/<category>/` 目录
- 确保 frontmatter 完整

## 关键约束

- **始终使用** `scripts/save_ai_note.sh` 脚本
- **绝不手动** 写文件到 `docs/ai/` 目录
- 脚本控制命名、时间戳和最终路径
- 不能直接使用 write_to_file 或 mv 命令绕过脚本

# 优势

1. **零手动成本** — AI 自主判断，无需人工干预
2. **分类清晰** — 7 大类别覆盖主要知识域
3. **命名规范** — 时间戳 + 主题，可排序、可检索
4. **路径一致** — 脚本保证格式统一，避免人为错误
5. **按需沉淀** — 不是全量保存，只保留高价值内容

# 相关

- `AGENTS.md` — 定义触发规则和保存流程
- `scripts/save_ai_note.sh` — 核心保存脚本
- `docs/ai/` — 知识库根目录
