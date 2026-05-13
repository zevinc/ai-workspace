# Agent Rules

## AI Knowledge Capture

Create a knowledge note only when the response is:

- Important or reusable
- Architectural or design-related
- Debugging / troubleshooting related
- Related to Agent workflow or automation
- Longer than 300 words with long-term value

Do not save temporary, low-value, or repetitive responses.

## Save Flow

When knowledge capture is triggered:

1. Ensure temp directory exists, write the note to:

```bash
mkdir -p .tmp/ai & .tmp/ai/note.md
```

2. Choose a category:

| Category        | Usage                                        |
| --------------- |----------------------------------------------|
| architecture    | system design, architecture                  |
| backend         | Java, Spring Boot, Gradle, DB, APIs          |
| frontend        | React, Vue, Angular, UI/UX, state management |
| agents          | Hermes, Claude Code, workflows, automation   |
| rag             | embeddings, vector DB, retrieval             |
| prompts         | prompt engineering, prompt rules             |
| decisions       | ADRs, trade-offs, technical decisions        |
| troubleshooting | bugs, incidents, debugging                   |

3. Choose a short kebab-case topic:

```text
hermes-auto-knowledge
springboot-ai-log-writer
pgvector-rag-indexing
```

4. Save using the script:

```bash
scripts/save_ai_note.sh <category> <topic> .tmp/ai/note.md
```

* Always use `scripts/save_ai_note.sh`
* Never manually write files into `docs/ai/`
* The script controls naming, timestamps, and final paths

5. Updating Index Directory:

update the index directories `docs/ai/INDEX.md` and `docs/manual/INDEX.md` to record new knowledge sources, content summaries, and tags. This enables Agents to quickly locate relevant knowledge and improve response efficiency.

## Markdown Template

* The saved markdown file must include front-matter with `title`, `tags`, `summary`, and `created` date.

```markdown
---
title:
tags:
summary:
created:
---

# Background

# Problem

# Solution

# Key Points

# Risks

# Related
```

## Index Example

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
- summary: Async AI HTTP log writer using queue buffering and batch DB writes.
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
