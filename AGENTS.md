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

| Category        | Usage                                      |
| --------------- | ------------------------------------------ |
| architecture    | system design, architecture                |
| backend         | Java, Spring Boot, Gradle, DB, APIs        |
| agents          | Hermes, Claude Code, workflows, automation |
| rag             | embeddings, vector DB, retrieval           |
| prompts         | prompt engineering, prompt rules           |
| decisions       | ADRs, trade-offs, technical decisions      |
| troubleshooting | bugs, incidents, debugging                 |

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

## Markdown Template

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