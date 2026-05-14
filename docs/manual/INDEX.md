# AI Knowledge Index

  > Central registry for reusable AI/project knowledge.
  > Agents must read this file first before loading detailed notes.

---

## Entry: ai-knowledge-base-index

- path: `docs/manual/agents/2026-05-13-0001_AI_Knowledge_Base_Index.md`
- category: `agents`
- tags:
    - `knowledge-base`
    - `index`
    - `lazy-loading`
    - `reference`
- summary: 按关键词和标签组织的知识库索引条目目录，覆盖架构、后端、提示词、排错等 8 个类别，Agent 可通过关键词匹配定位目标文件后按需加载。
- use_when:
    - Agent needs to discover what project knowledge exists
    - User asks about knowledge base structure / 知识库有哪些内容
    - User wants to find a specific knowledge document by keyword
    - User asks about available reference documents
- related: ~
- priority: `high`
- last_updated: `2026-05-13`
- status: `active`

---

## Entry: claude-md-java-springboot-constitution

- path: `docs/manual/agent/2026-05-13-0001-CLAUDE.md`
- category: `prompts`
- tags:
    - `claude-code`
    - `java`
    - `spring-boot`
    - `constitution`
    - `prompt-template`
    - `tech-stack`
- summary: Java Spring Boot 项目的 CLAUDE.md 宪法文件模版，包含完整技术栈清单、强制编码规范（项目结构/命名/代码质量/测试/配置）、禁止事项、错误处理模式，供 Claude Code 在每次任务前自动加载。
- use_when:
    - User asks about CLAUDE.md / project constitution template
    - User asks about Java Spring Boot coding standards
    - User asks about project tech stack / naming conventions / structure
    - User asks about prohibited practices / antipatterns
    - User asks about error handling patterns / global exception handler
    - User asks about testing standards (unit / integration / e2e)
- related:
    - `docs/manual/agents/2026-05-13-0001-AI_Knowledge_Base_Index.md`
- priority: `high`
- last_updated: `2026-05-13`
- status: `active`

---

## Entry: init-agent-using-docs

- path: `docs/manual/inits/init_agent_using_docs.md`
- category: `reference`
- tags:
    - `agent`
    - `knowledge-base`
    - `lazy-loading`
    - `INDEX.md`
    - `documentation`
    - `CLAUDE.md`
    - `AGENTS.md`
- summary: Agent 知识库使用规范：定义双知识库（docs/ai/ + docs/manual/）的懒加载流程——先读索引目录、按 category/tags/summary 匹配、按需加载具体文档、双库优先级策略，含 CLAUDE.md/AGENTS.md 推荐写法和分类体系。
- use_when:
    - User asks about how Agent loads knowledge / 知识库加载流程
    - User asks about CLAUDE.md / AGENTS.md recommended content
    - User asks about knowledge base categories / 分类
    - User asks about lazy-loading strategy / 按需加载
    - User asks about dual knowledge base priority / 双库优先级
    - User asks about agent documentation usage rules
- related:
    - `docs/manual/inits/int_index.md`
    - `docs/manual/inits/init_docs.md`
    - `docs/ai/INDEX.md`
    - `AGENTS.md`
- priority: `high`
- last_updated: `2026-05-13`
- status: `active`

---

## Entry: int-index-format

- path: `docs/manual/inits/int_index.md`
- category: `reference`
- tags:
    - `INDEX.md`
    - `index`
    - `knowledge-base`
    - `metadata`
    - `entry-format`
    - `reference`
- summary: INDEX.md 索引目录的 Entry 格式规范文档：定义 path/category/tags/summary/use_when/related/priority/last_updated/status 各字段的语义与格式要求，含完整示例和 Agent 从读到用的生效过程。
- use_when:
    - User asks about INDEX.md entry format / index entry 格式
    - User asks about knowledge base metadata fields / 索引字段定义
    - User asks about index directory specification / 索引目录规范
    - User asks how to write a new INDEX.md entry
    - Agent needs to validate INDEX.md format correctness
- related:
    - `docs/manual/inits/init_agent_using_docs.md`
    - `docs/manual/inits/init_docs.md`
    - `docs/ai/INDEX.md`
    - `docs/manual/INDEX.md`
- priority: `high`
- last_updated: `2026-05-13`
- status: `active`

---

## Entry: init-knowledge-base

- path: `docs/manual/inits/init_docs.md`
- category: `reference`
- tags:
    - `knowledge-base`
    - `initialization`
    - `directory-structure`
    - `AGENTS.md`
    - `setup`
    - `automation`
    - `save-pipeline`
- summary: 项目知识库从零搭建的完整初始化方案：目录结构设计（8 个 ai/ 分类 + INDEX.md）、AGENTS.md 模板规则、保存脚本与管道、分类路由策略、索引更新流程、以及 Agent 使用文档的配置引导。
- use_when:
    - User asks about knowledge base setup / 知识库初始化
    - User asks about docs/ai/ directory structure / 目录结构设计
    - User asks about AGENTS.md template / rules setup
    - User asks about save_ai_note.sh pipeline setup
    - User asks about category routing / 分类路由
    - User asks about knowledge base automation / 知识库自动化
- related:
    - `docs/manual/inits/init_agent_using_docs.md`
    - `docs/manual/inits/int_index.md`
    - `docs/ai/agents/2026-05-13-1549-agent-auto-knowledge-capture.md`
    - `AGENTS.md`
    - `scripts/save_ai_note.sh`
- priority: `high`
- last_updated: `2026-05-13`
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
