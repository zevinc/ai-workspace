# 添加索引文件

每次知识自动沉淀后，更新索引目录 `docs/ai/INDEX.md`，记录新知识的来源、内容摘要和标签。这样 Agent 就能快速定位相关知识，提升回答效率。

1. 索引目录-路径: docs/ai/INDEX.md

2. 索引目录-示例:

```yaml
agents:
  2026-05-13-0150-hermes-auto-knowledge:
    title: Hermes 自动知识沉淀方案
    tags: [hermes, knowledge-capture, automation, ai-workflow]
    summary: 基于 AGENTS.md 规则，通过 AI 自动识别并保存高价值知识到 docs/ai/ 目录的完整方案
    created: 2026-05-13
```

3. 索引目录-生效过程:

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
