# AI Knowledge Index

  > Central registry for reusable AI/project knowledge.
  > Agents must read this file first before loading detailed notes.

---

## Entry: cloud-agent-platform-final

- path: `docs/ai/architecture/2026-05-13-1705-cloud-agent-platform-final.md`
- category: `architecture`
- tags:
    - `agent-platform`
    - `architecture`
    - `microservices`
    - `spring-ai`
    - `temporal`
    - `RAG`
    - `multi-agent`
    - `orchestration`
    - `guardrails`
    - `MCP`
    - `A2A`
    - `knowledge-base`
- summary: 云端通用 Agent 平台最终融合方案（Hermes + GPT5.5）：8 层服务架构含独立 Model Gateway 和 Session Service、9 大模块含 SQL Schema、Spring AI + Temporal 技术栈、3 层 Guardrails、6 步 RAG 管道+知识图谱、5 种编排模式、24 周 5 阶段执行计划、7-9 人团队。融合策略：GPT5.5 主体(90%) + Hermes 模块化拆分。
- use_when:
    - User asks about cloud agent platform / 云端 Agent 平台 / Agent 平台架构
    - User asks about agent platform final solution / 最终方案
    - User asks about agent microservice design / 模块设计 / SQL Schema
    - User asks about Spring AI / Temporal / pgvector / Guardrails
    - User asks about agent platform execution plan / 执行计划 / 24 周 / 团队配置
    - User asks about Model Gateway / Session Service / Tool Registry / RAG
    - User asks about agent platform technology selection / 技术选型
    - User asks about multi-agent orchestration / 多 Agent 编排 / Debate / Supervisor
- related:
    - `docs/ai/agents/2026-05-13-1315-agent-paradigms-patterns.md`
    - `docs/ai/agents/2026-05-13-1549-agent-auto-knowledge-capture.md`
    - `docs/temp/history/2026-05-13-1638-cloud-agent-platform.hermes.md`
    - `docs/temp/history/2026-05-13-1638-cloud-agent-platform.gpt55.md`
    - `docs/temp/comparison/2026-05-13-1645-agent-platform-comparison.md`
- priority: `high`
- last_updated: `2026-05-13`
- status: `active`

---

## Entry: agent-auto-knowledge-capture

- path: `docs/ai/agents/2026-05-13-1549-agent-auto-knowledge-capture.md`
- category: `agents`
- tags:
    - `agent`
    - `knowledge-capture`
    - `architecture`
    - `automation`
    - `rag`
    - `pgvector`
    - `index`
    - `retrieval`
    - `frontmatter`
- summary: AI Agent 自动知识沉淀完整方案（语言/框架无关）：5 层架构（触发→捕获→处理→存储→检索）、5 步保存管道含双索引更新、去重与增量更新策略、8 大分类路由、工程陷阱与性能考量、完整工具链与参考项目。
- use_when:
    - User asks about AI agent knowledge capture / 知识沉淀 / 自动文档化
    - User asks about docs/ai/ or docs/manual/ knowledge base architecture
    - User asks about agent knowledge indexing / 索引 / INDEX.md
    - User asks about AGENTS.md Markdown Template / frontmatter format
    - User asks about dual knowledge base / 双库双索引 / save pipeline
    - User asks about save_ai_note.sh pipeline / Step 1-5
    - User asks about anti-duplication / 去重 / 增量更新 strategy
- related:
    - `docs/ai/agents/2026-05-13-1315-agent-paradigms-patterns.md`
    - `docs/manual/inits/int_index.md`
    - `docs/manual/inits/init_agent_using_docs.md`
    - `scripts/save_ai_note.sh`
    - `AGENTS.md`
- priority: `high`
- last_updated: `2026-05-13`
- status: `active`

---

## Entry: agent-paradigms-patterns

- path: `docs/ai/agents/2026-05-13-1315-agent-paradigms-patterns.md`
- category: `agents`
- tags:
    - `ai-agent`
    - `agent-paradigm`
    - `architecture-pattern`
    - `ReAct`
    - `Chain-of-Thought`
    - `multi-agent`
    - `MCP`
    - `A2A`
    - `cognitive-architecture`
    - `tool-use`
    - `planning`
    - `prompt-engineering`
    - `LLM`
- summary: 系统梳理 2022–2025 年 AI Agent 领域核心范式，覆盖基础推理、行动工具、规划执行、多智能体协作、工程架构、协议标准、高级认知、安全质量等 30+ 范式，含伪代码与代表性实现。
- use_when:
    - User asks about AI agent paradigms / patterns / architecture
    - User asks about ReAct, CoT, ToT, Reflexion, CodeAct
    - User asks about multi-agent collaboration / delegation
    - User asks about MCP, A2A protocols
    - User asks about agent cognitive architecture
    - User asks about agentic RAG, Router Agent, SWE-agent
    - User asks about Human-in-the-Loop, Guardrails
    - User asks about Andrew Ng agentic design patterns
- related: ~
- priority: `high`
- last_updated: `2026-05-13`
- status: `active`

---

## Entry: http-protocol-interview-questions

- path: `docs/ai/backend/2026-05-14-1124-http-protocol-interview-questions.md`
- category: `backend`
- tags:
    - `http`
    - `https`
    - `network`
    - `protocol`
    - `interview`
    - `cache`
    - `cookie`
    - `jwt`
    - `tls`
    - `cors`
    - `http2`
    - `http3`
    - `quic`
- summary: HTTP 协议面试题型系统归类，覆盖 8 大类：基础概念、版本演进(0.9→3)、方法(GET/POST/PUT/PATCH)、状态码(1xx~5xx)、头部、HTTPS/TLS 加密与握手、认证(Cookie/Session/JWT)、缓存(强缓存/协商缓存)。每题配有经典追问与标准答案，按初/中/高级标注考察重点。
- use_when:
    - User asks about HTTP interview questions / HTTP 面试题
    - User asks about HTTP/HTTPS protocol / HTTP 协议原理
    - User asks about HTTP version differences / HTTP 版本演进
    - User asks about Cookie / Session / JWT / Token 认证
    - User asks about HTTP cache / 强缓存 / 协商缓存 / Cache-Control
    - User asks about TLS handshake / HTTPS 加密原理
    - User asks about CORS / 跨域 / OPTIONS 预检
    - User asks about HTTP/2 多路复用 / HTTP/3 QUIC
- related:
    - ~
- priority: `high`
- last_updated: `2026-05-14`
- status: `active`

---

## Entry: jakarta-servlet-dispatchertype

- path: `docs/ai/backend/2026-05-14-1426-jakarta-servlet-dispatchertype.md`
- category: `backend`
- tags:
    - `servlet`
    - `jakarta`
    - `dispatchertype`
    - `filter`
    - `enum`
    - `tomcat`
    - `spring-boot`
    - `spring-security`
- summary: jakarta.servlet.DispatcherType 枚举 6 个值详解（REQUEST/FORWARD/INCLUDE/ASYNC/ERROR/WEBSOCKET）：触发条件、Filter 配置方式（@WebFilter/web.xml/FilterRegistrationBean）、forward 绕过安全漏洞案例、Tomcat 源码 Filter 匹配流程、Spring Security 全类型注册策略。
- use_when:
    - User asks about DispatcherType / Servlet dispatcher type / 分发类型
    - User asks about Filter dispatcher / Filter 不生效 / forward 绕过
    - User asks about Servlet filter chain / request.getDispatcherType()
    - User asks about @WebFilter dispatcherTypes configuration
    - User asks about Spring Security filter registration
    - User asks about ASYNC dispatch / ERROR page filter
- related:
    - `docs/ai/backend/2026-05-14-0105-spring-webmvcconfigurer-all-methods.md`
- priority: `high`
- last_updated: `2026-05-14`
- status: `active`

---

## Entry: spring-webmvcconfigurer-all-methods

- path: `docs/ai/backend/2026-05-14-0105-spring-webmvcconfigurer-all-methods.md`
- category: `backend`
- tags:
    - `spring-mvc`
    - `spring-boot`
    - `webmvcconfigurer`
    - `extension-point`
    - `java-config`
    - `interceptor`
    - `cors`
    - `message-converter`
    - `argument-resolver`
- summary: WebMvcConfigurer 接口全部 18 个 default 方法的中文详解，每个方法配有完整代码示例、注释和最佳实践。覆盖路径匹配、内容协商、拦截器、CORS、消息转换器、参数解析器、视图解析等全部扩展点。
- use_when:
    - User asks about WebMvcConfigurer / MVC config extension / MVC 配置扩展
    - User asks about Spring MVC interceptor / CORS / message converter config
    - User asks about argument resolver / return value handler / 自定义参数解析器
    - User asks about configure vs extend vs add pattern / 替换还是扩展
    - User asks about path matching / content negotiation / 路径匹配 / 内容协商
    - User asks about resource handler / view controller / static resource config
- related:
    - `docs/manual/agent/2026-05-13-0001-CLAUDE.md`
- priority: `high`
- last_updated: `2026-05-14`
- status: `active`
