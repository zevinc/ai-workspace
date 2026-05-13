# AI Knowledge Index

  > Central registry for reusable AI/project knowledge.
  > Agents must read this file first before loading detailed notes.

---

## Entry: ai-knowledge-base-index

- path: `docs/manual/agents/2026-05-13_AI_Knowledge_Base_Index.md`
- category: `agents`
- tags:
    - `knowledge-base`
    - `index`
    - `lazy-loading`
    - `architecture`
    - `backend`
- summary: AI 知识库索引入门文档，按关键词和标签组织条目，Agent 匹配关键词后按需加载对应文件。
- use_when:
    - Agent needs to discover project knowledge
    - User asks about knowledge base structure
    - User asks about microservice boundaries
    - User asks about Spring transactions
    - User asks about Gradle multi-module
    - User asks about cache strategy ADR
- related: ~
- priority: `high`
- last_updated: `2026-05-13`
- status: `active`

---

## Entry: claude-md-java-springboot-constitution

- path: `docs/manual/prompts/2026-05-13-CLAUDE.md`
- category: `prompts`
- tags:
    - `claude-code`
    - `java`
    - `spring-boot`
    - `constitution`
    - `prompt-template`
    - `tech-stack`
- summary: Java Spring Boot 项目的 CLAUDE.md 宪法文件模版，包含完整技术栈清单、强制编码规范、禁止事项和错误处理模式，供 Claude Code 在每次任务前自动加载。
- use_when:
    - User asks about CLAUDE.md template
    - User asks about Java Spring Boot coding standards
    - User asks about project constitution / rules
    - User asks about tech stack checklist
    - User asks about prohibited practices
- related:
    - `docs/manual/agents/2026-05-13_AI_Knowledge_Base_Index.md`
- priority: `high`
- last_updated: `2026-05-13`
- status: `active`
