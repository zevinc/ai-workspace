---
title: AI Agent 开发范式、架构与模式大全
tags:
  - ai-agent
  - agent-paradigm
  - architecture-pattern
  - ReAct
  - Chain-of-Thought
  - multi-agent
  - MCP
  - A2A
  - cognitive-architecture
  - tool-use
  - planning
  - prompt-engineering
  - LLM
summary: |
  系统梳理 2022–2025 年 AI Agent 领域的核心开发范式、架构模式与设计思路。
  覆盖基础推理 (CoT/ReAct/ReWOO)、行动与工具 (Function Calling/CodeAct/Browser Agent)、
  规划与执行 (Plan-Execute/ToT/Graph-of-Thought)、多智能体协作 (Delegation/Orchestrator-Worker/Swarm/MoA)、
  工程架构 (Agentic RAG/Router/SWE-agent)、协议标准 (MCP/A2A)、高级认知 (Reflexion/Self-Correction/Cognitive Architecture)、
  安全质量 (HITL/Guardrails) 等 30+ 范式。每个条目含描述、伪代码、代表性实现和适用场景。
created: 2026-05-13
---

# AI Agent 开发范式、架构与模式大全

> 整理时间：2026年5月 | 覆盖 2022–2025 年核心概念

---

## 目录

1. [基础推理范式](#1-基础推理范式)
2. [行动与工具使用范式](#2-行动与工具使用范式)
3. [规划与执行范式](#3-规划与执行范式)
4. [多智能体协作范式](#4-多智能体协作范式)
5. [工程架构模式](#5-工程架构模式)
6. [Agent 协议与标准](#6-agent-协议与标准)
7. [高级认知模式](#7-高级认知模式)
8. [安全与质量保障模式](#8-安全与质量保障模式)
9. [Andrew Ng Agentic 设计模式](#9-andrew-ng-agentic-设计模式)
10. [总结对比表](#10-总结对比表)

---

## 1. 基础推理范式

### 1.1 Chain-of-Thought (CoT) — 思维链

- **提出时间**: 2022年1月，Google Brain
- **论文**: _"Chain-of-Thought Prompting Elicits Reasoning in Large Language Models"_
- **核心思想**: 在给出最终答案之前，让模型显式输出中间推理步骤。不涉及外部工具或行动，纯推理增强。

**伪代码**:
```
SYSTEM: "Let's think step by step."

USER: "Q: 小明有5个苹果，给了小红2个，又买了3个，现在有几个？"

ASSISTANT:
  第一步：小明最初有5个苹果。
  第二步：给小红2个后，剩下 5 - 2 = 3 个。
  第三步：又买了3个，现在有 3 + 3 = 6 个。
  Answer: 6
```

**代表性实现**:
- 零样本 CoT: 直接加 "Let's think step by step"
- 少样本 CoT: 在 prompt 中提供带推理过程的示例
- Self-Consistency CoT: 多次采样取多数结果

**适用场景**: 数学推理、逻辑推理、多步骤分析 — 所有不需要外部工具的任务。

**优点**: 简单、零成本、显著提升推理准确率。

**缺点**: 无法访问实时数据；长推理链可能漂移；不适用于需要行动的 agent 场景。

---

### 1.2 ReAct (Reasoning + Acting) — 推理-行动交替

- **提出时间**: 2022年10月，Google Brain & Princeton
- **论文**: _"ReAct: Synergizing Reasoning and Acting in Language Models"_
- **核心思想**: 交替输出 Thought（推理）和 Action（行动），让模型"边想边做"。Thought 引导 Action，Action 获取 Observation，Observation 又促进下一步 Thought。

**伪代码**:
```
while not done:
    Thought: 分析当前状态，决定需要什么信息/操作
    Action:  search("关键词") / calculate(expr) / code_interpreter(code)
    Observation: <外部环境返回结果>
    # 循环直到有足够信息回答
Answer: 基于所有 Observations 的最终回答
```

**完整示例**:
```
Question: 2023年诺贝尔物理学奖得主是谁？他们的主要贡献是什么？

Thought 1: 我需要查询2023年诺贝尔物理学奖得主。
Action 1: search("2023 Nobel Prize in Physics winner")
Observation 1: Pierre Agostini, Ferenc Krausz, Anne L'Huillier — attosecond physics

Thought 2: 已获得得主名字，还需要了解他们的具体贡献。
Action 2: search("attosecond physics pulse electron dynamics")
Observation 2: 阿秒脉冲用于观测电子在原子中的超快运动...

Thought 3: 信息足够，可以回答了。
Answer: 2023年诺贝尔物理学奖授予 Pierre Agostini、Ferenc Krausz 和 Anne L'Huillier，
表彰他们在阿秒物理学领域的贡献——开发了产生阿秒光脉冲的方法，用于研究物质中电子的动力学。
```

**代表性实现**: LangChain AgentExecutor, OpenAI Assistants, Hermes Agent, AutoGPT 核心循环。

**适用场景**: 几乎所有需要工具调用的 agent 场景 — 搜索、计算、代码执行、数据库查询等。

**优点**: 可解释性强；每一步都可审计和纠偏；适合复杂多步任务。

**缺点**: 串行执行，延迟高（每步都要等 Observation）；token 消耗大（每步都要输出完整的 Thought 和 Action）。

---

### 1.3 ReWOO (Reason Without Observation) — 无观察推理

- **提出时间**: 2023年9月
- **论文**: _"ReWOO: Decoupling Reasoning from Observations for Efficient Augmented Language Models"_
- **核心思想**: 一次性规划所有需要的 Action 及其参数依赖关系，然后批量执行。避免 ReAct 的串行等待开销。

**伪代码**:
```
# Phase 1: 规划阶段（不等待任何结果）
Plan:
  - E1 = search("诺贝尔物理学奖 2023")
  - E2 = search("{E1} 阿秒物理 贡献")      # 带占位符，标明依赖
  - E3 = LLM("总结 {E1} 和 {E2}")           # LLM 作为工具
  - E4 = search("阿秒脉冲 应用")

# Phase 2: 执行阶段（批量并行执行）
Execute E1, E4 in parallel  # 无依赖，并行
Wait E1 → Execute E2         # E2 依赖 E1
Wait E1,E2 → Execute E3      # E3 依赖 E1,E2

# Phase 3: 综合
Answer = synthesize(E1, E2, E3, E4)
```

**代表性实现**: 论文开源实现 (`billxbf/ReWOO`)。

**适用场景**: 大量独立查询、可预见的工具调用链、对延迟敏感的场景。

**优点**: 大幅减少 token 消耗（少输出多轮 Thought）；支持并行执行；延迟显著低于 ReAct。

**缺点**: 缺乏动态应变能力；无法根据 Observation 调整后续规划；依赖预判准确。

---

## 2. 行动与工具使用范式

### 2.1 Function Calling / Tool Use — 函数调用

- **提出时间**: 2023年6月（OpenAI Function Calling），后续成为行业标准
- **核心思想**: 模型直接输出结构化的函数调用（JSON Schema），宿主解析后执行并将结果返回。不做显式 Thought trace，精简高效。

**伪代码**:
```
# 系统定义工具
TOOLS = [
  {name: "get_weather", params: {location: string, unit: string}},
  {name: "search_web",   params: {query: string}},
]

# 模型响应（不输出 Thought，直接输出 tool_call）
ASSISTANT (tool_calls):
  [{"id": "call_1", "function": "get_weather", "arguments": {"location": "北京", "unit": "celsius"}}]

# 宿主执行 → 返回结果
HOST → {"temperature": 22, "condition": "晴"}

# 模型继续
ASSISTANT: 北京今天晴，气温22°C。
```

**代表性实现**: OpenAI Function Calling / Tool Use, Anthropic Tool Use, Gemini Function Calling, 所有主流 LLM API。

**适用场景**: 结构化工具调用 — API 查询、数据库操作、文件读写等。

**优点**: 结构化、可靠；工具参数由 schema 约束，减少幻觉；token 效率高。

**缺点**: 缺乏显式推理过程，复杂多步决策可解释性差；通常需要配合 ReAct 等范式使用。

---

### 2.2 CodeAct — 代码即行动

- **提出时间**: 2023年11月
- **论文**: _"CodeAct: A Unified Action Space for Language Agents"_
- **核心思想**: 将所有 agent 行动统一为"生成并执行代码"。不再区分"搜索"、"计算"、"文件操作"等离散 action，而是让模型直接输出可执行代码片段，在统一的代码解释器中执行。

**伪代码**:
```
# 传统 ReAct（离散 action）
Action: search("2023 Nobel Prize physics")
Action: calculate(1 + 2 * 3)

# CodeAct（统一 action space）
Action:
```python
import requests
result = requests.get("https://api.search.com?q=2023+Nobel+Prize+physics")
answer = eval("1 + 2 * 3")
```

**核心优势**:
- 统一 action space — 不需要为每种操作定义 schema
- 图灵完备 — 理论上能干任何事
- 可组合 — `for` 循环 + 条件 + 工具调用自然组合

**代表性实现**: OpenCodeInterpreter, SWE-agent（部分借鉴）, CodeActAgent。

**适用场景**: 代码密集型任务 — 数据分析、文件处理、复杂计算、API 编排。

**优点**: 图灵完备、灵活、减少 tool schema 维护成本。

**缺点**: 安全风险（沙箱必须严格）；调试困难；对非编程任务可能过度工程化。

---

### 2.3 Browser Agent / Computer Use Agent — 浏览器/桌面智能体

- **提出时间**: 2024年（Anthropic Computer Use, WebVoyager 等）
- **核心思想**: 让 agent 像人一样操作 GUI — 看屏幕、移动鼠标、点击、输入。通过截图+像素坐标实现通用计算机操作。

**伪代码**:
```
while not done:
    # 1. 获取当前屏幕截图
    screenshot = take_screenshot()

    # 2. 模型分析截图 + 任务目标 → 确定下一步操作
    action = model.analyze(screenshot, goal="预订一张从北京到上海的机票")

    # 3. 执行操作
    if action.type == "click":
        mouse.click(action.x, action.y)
    elif action.type == "type":
        keyboard.type(action.text)
    elif action.type == "scroll":
        mouse.scroll(action.direction, action.amount)
    elif action.type == "done":
        break

    # 4. 等待页面响应
    wait_for_page_load()
```

**代表性实现**:
- **Anthropic Computer Use**: Claude 直接操控桌面
- **WebVoyager**: 端到端网页浏览 agent
- **Playwright/Playwright-MCP**: 浏览器自动化 + agent
- **Browserbase**: 托管浏览器 agent

**适用场景**: 网页自动化、需要 GUI 交互的任务（预订、填表、数据采集）、遗留系统操作。

**优点**: 通用性极强 — 任何有人机界面的场景都能用。

**缺点**: 速度慢（每步都等渲染）；token 消耗大（每次截图）；可靠性受 UI 变动影响。

---

## 3. 规划与执行范式

### 3.1 Plan-and-Execute — 先规划后执行

- **提出时间**: 2023年3月（BabyAGI, AutoGPT 时期）
- **核心思想**: 先做全局规划（分解任务为子任务列表），再逐个执行子任务。规划和执行解耦，执行阶段不再重新思考全局策略。

**伪代码**:
```
# Phase 1: 全局规划
USER: "写一篇关于AI agent的调研报告"
Plan:
  1. 搜索最新AI agent研究论文
  2. 阅读并总结关键论文
  3. 搜索业界应用案例
  4. 组织报告结构
  5. 撰写报告各章节
  6. 审校和润色

# Phase 2: 逐步执行
for task in plan:
    result = execute(task)
    if result.needs_replan:
        replan_from(task_index)

# Phase 3: 综合
final = synthesize(all_results)
```

**代表性实现**: BabyAGI, AutoGPT, LangChain PlanAndExecute, CrewAI（部分）。

**适用场景**: 任务边界清晰、可以预先分解的复杂任务 — 报告撰写、项目开发、调研分析。

**优点**: 全局视野好；执行高效（不需要每步重新思考方向）；适合长周期任务。

**缺点**: 缺乏灵活应变；中间发现新信息无法动态调整计划（除非显式 replan）。

---

### 3.2 Tree-of-Thought (ToT) — 思维树

- **提出时间**: 2023年5月，Google DeepMind & Princeton
- **论文**: _"Tree of Thoughts: Deliberate Problem Solving with Large Language Models"_
- **核心思想**: 在关键决策点分叉出多条推理路径，像树状搜索（BFS/DFS）一样探索，评估每条路径的质量，选择最优路径继续。

**伪代码**:
```
def tree_of_thought(problem, max_depth=5, beam_width=3):
    root = Thought(problem)
    frontier = [root]

    for depth in range(max_depth):
        candidates = []
        for node in frontier:
            # 生成下一步的多个候选思路（分叉）
            next_thoughts = model.generate_thoughts(node, num_candidates=3)

            for thought in next_thoughts:
                # 评估每个候选的质量
                score = model.evaluate(thought, problem)
                candidates.append((thought, score))

        # 保留 top-k（束搜索）
        candidates.sort(key=lambda x: x[1], reverse=True)
        frontier = [c[0] for c in candidates[:beam_width]]

        # 终止条件检查
        if any(t.is_solution for t in frontier):
            return best_solution(frontier)

    return best_attempt(frontier)
```

**代表性实现**: 论文官方实现, LangChain ToT。

**适用场景**: 创意写作、博弈类问题、需要探索多种可能性的规划任务。

**优点**: 探索性远强于线性推理；能找到非直觉的优秀解。

**缺点**: 计算和 token 成本极高（每个节点都需 LLM 调用）；对确定性问题收益不大。

---

### 3.3 Graph-of-Thought / Agent Graphs — 思维图

- **提出时间**: 2024年（LangGraph 为代表）
- **核心思想**: 将 agent 的思考-行动流程建模为有向图（可能带环）。每个节点代表一个处理步骤（LLM 调用、工具调用、判断），边代表状态转移条件。支持条件分支、并行、循环、人工审核节点。

**伪代码**:
```
# LangGraph 风格
from langgraph import StateGraph

workflow = StateGraph(AgentState)

# 定义节点
workflow.add_node("think", think_node)       # LLM 推理
workflow.add_node("tool_router", router)     # 判断用哪个工具
workflow.add_node("search", search_tool)     # 搜索工具
workflow.add_node("calc", calculate_tool)    # 计算工具
workflow.add_node("human_review", human)     # 人工审核
workflow.add_node("answer", answer_node)     # 最终回答

# 定义边（条件/转换）
workflow.set_entry_point("think")
workflow.add_conditional_edges(
    "think",
    router,
    {
        "search": "search",
        "calculate": "calc",
        "answer": "answer",
        "unsure": "human_review",
    }
)
workflow.add_edge("search", "think")         # 回到 think（循环）
workflow.add_edge("calc", "think")           # 回到 think（循环）
workflow.add_edge("human_review", "answer")
```

**代表性实现**: LangGraph, CrewAI Flows, OpenAI Swarm (部分), Dify, Coze。

**适用场景**: 复杂 agent 编排 — 需要条件分支、人机协作、多 agent 协调的场景。

**优点**: 极度灵活；可视化；支持复杂控制流（循环、并行、中断恢复）。

**缺点**: 设计复杂度高；调试困难；过度设计风险。

---

## 4. 多智能体协作范式

### 4.1 Delegation / Multi-Agent — 多智能体委托

- **提出时间**: 2023–2024年（AutoGPT, AutoGen 等）
- **核心思想**: 一个"主 agent"将子任务委托给独立的"子 agent"，每个子 agent 在自己的隔离上下文中执行。主 agent 只接收最终摘要，不需要看到子 agent 的中间步骤。

**伪代码**:
```
# 主 Agent
USER: "审查 PR #42 的代码，搜索相关 issue，然后给出 review 意见"

# 主 Agent 并行委托
delegate_task([
    {
        goal: "审查 PR #42 的代码变更",
        context: "Repo: myproject, PR: #42",
        tools: ["terminal", "file", "github"],
    },
    {
        goal: "搜索与 PR #42 修改文件相关的历史 issue",
        context: "PR #42 修改了 auth.py 和 models.py",
        tools: ["web", "github"],
    },
])

# 每个子 agent 独立运行自己的 ReAct 循环
# 主 agent 收到结果后综合输出

RESULTS:
  - 子 agent 1: 发现3个问题（SQL注入风险、缺少类型标注、测试覆盖不足）
  - 子 agent 2: 找到2个相关 issue (#38 认证重构，#41 模型字段变更)

FINAL OUTPUT: 综合 code review 意见
```

**代表性实现**: AutoGen, CrewAI, Hermes delegate_task, OpenAI Swarm, LangGraph 子图。

**适用场景**: 可并行分解的任务、需要不同专业知识的子任务、大量独立查询的场景。

**优点**: 并行提速；上下文隔离（主 agent 不被子任务细节淹没）；专业化分工。

**缺点**: 协调开销；子 agent 可能理解偏差；缺乏全局视角。

---

### 4.2 Orchestrator-Worker — 编排器-工作者

- **提出时间**: 2024年（Anthropic "Building Effective Agents" 重点推荐）
- **核心思想**: 一个 Orchestrator（编排 agent）动态分析任务，将子任务分派给 Worker agents。与 Plan-and-Execute 的区别：Orchestrator 不是一次性规划，而是每完成一个子任务后重新评估，动态决定下一个子任务。

**伪代码**:
```
def orchestrator_worker(task):
    context = {"task": task, "completed": [], "findings": {}}

    while not done:
        # Orchestrator 动态决策下一步
        decision = orchestrator.think(context)

        if decision.action == "delegate":
            worker_result = workers[decision.worker_type].execute(
                goal=decision.subtask,
                context=context
            )
            context["completed"].append(decision.subtask)
            context["findings"].update(worker_result)

        elif decision.action == "done":
            break

    return orchestrator.synthesize(context)
```

**代表性实现**: Anthropic 推荐的 agent 架构, LangGraph Orchestrator-Worker 模板, AutoGen。

**适用场景**: 复杂、不可预见的任务，需要动态决策的工作流。

**优点**: 灵活应变；利用不同 worker 的专业能力；全局协调性好。

**缺点**: 串行瓶颈（Orchestrator 是单点）；Orchestrator 推理成本高。

---

### 4.3 Hierarchical Agent Teams — 层级智能体团队

- **提出时间**: 2024年（AutoGen 团队）
- **核心思想**: 多层 agent 组织 — 顶层 agent 做战略规划，中层 agent 做战术协调，底层 agent 执行具体操作。类似企业组织结构。

**伪代码**:
```
# 三层结构
Level 1 — "CEO Agent"
  └── 规划总方向，分配任务给 Level 2

Level 2 — "Team Lead Agents"
  ├── "Frontend Lead" → 协调前端工作
  ├── "Backend Lead"  → 协调后端工作
  └── "QA Lead"       → 协调测试工作

Level 3 — "Worker Agents"
  ├── (Frontend) → React Component Agent, CSS Agent
  ├── (Backend)  → API Agent, DB Agent, Auth Agent
  └── (QA)       → Unit Test Agent, E2E Agent, Lint Agent

# 流程
CEO: "实现用户登录功能"
  → Frontend Lead: "负责登录页面UI"
      → React Agent: 构建 LoginForm 组件
      → CSS Agent: 设计登录页面样式
  → Backend Lead: "负责登录API"
      → API Agent: 实现 POST /api/auth/login
      → DB Agent: 设计 users 表
      → Auth Agent: 实现 JWT token 生成
  → QA Lead: "测试登录流程"
      → Unit Test Agent, E2E Agent
  ↑ 结果逐级上报汇总 ↑
```

**代表性实现**: AutoGen GroupChat + nested agents, LangGraph 嵌套图。

**适用场景**: 大型项目的自动化开发、需要多领域协作的复杂任务。

**优点**: 高度组织化；适合大规模并行协作；分工清晰。

**缺点**: 协调成本高；层级越多延迟越大；上下文传递可能失真。

---

### 4.4 Agent Swarm — 智能体集群

- **提出时间**: 2024年（OpenAI Swarm 等）
- **核心思想**: 大量轻量级 agent 像蜂群一样松散协作，没有中心控制器，通过简单的规则和通信协议自发组织。每个 agent 能力有限，但集群涌现出复杂行为。

**伪代码**:
```
# 无中心编排，agent 自主决策
class SwarmAgent:
    def step(self, environment, neighbors):
        # 感知环境 + 邻居消息
        observations = self.sense(environment, neighbors)

        # 简单规则决策
        if self.has_task():
            self.execute_task()
        elif task := self.find_helpful_task(observations):
            self.pick_up_task(task)
        else:
            # 广播自身状态/能力
            self.broadcast_status()

# 集群启动
swarm = [SwarmAgent(specialty) for _ in range(20)]
for tick in range(MAX_TICKS):
    for agent in swarm:
        agent.step(environment, swarm)
```

**代表性实现**: OpenAI Swarm, Microsoft AutoGen swarm mode。

**适用场景**: 大规模数据采集、分布式搜索、并行特征提取、需要弹性伸缩的任务。

**优点**: 高容错（单个 agent 失败不影响全局）；弹性伸缩；无需中心编排。

**缺点**: 协调效率低；难以保证任务完整性；通信开销与规模平方增长。

---

### 4.5 Mixture-of-Agents (MoA) — 智能体混合

- **提出时间**: 2024年6月，Together AI
- **论文**: _"Mixture-of-Agents Enhances Large Language Model Capabilities"_
- **核心思想**: 借鉴 MoE (Mixture-of-Experts)，但用于 agent 层面。多个不同特长的 LLM agent 各自生成回答，然后由一个聚合 agent 综合所有回答生成最终结果。分层 MoA 可以多层迭代。

**伪代码**:
```
# 单层 MoA
def mixture_of_agents(query, num_proposers=3, aggregator_model="gpt-4o"):
    # Layer 1: Proposers（提案者）并行生成候选回答
    proposers = [
        llm_call("claude-sonnet-4", query),
        llm_call("gpt-4o", query),
        llm_call("gemini-2.5-pro", query),
    ]

    # Layer 2: Aggregator（聚合器）综合所有提案
    final = llm_call(aggregator_model, f"""
    综合以下候选回答，生成最终回答：

    提案1: {proposers[0]}
    提案2: {proposers[1]}
    提案3: {proposers[2]}

    问题: {query}
    最终回答:
    """)

    return final

# 多层 MoA（可选）
def multi_layer_moa(query, layers=3):
    answers = [query]
    for _ in range(layers):
        answers = [mixture_of_agents(a) for a in answers]
    return best(answers)
```

**代表性实现**: Together AI MoA 开源实现。

**适用场景**: 需要高质量回答的场景 — 问答、摘要、创意写作、代码生成等。

**优点**: 利用不同模型互补能力；显著提升回答质量；token 成本可控。

**缺点**: 多个 LLM 调用增加延迟和成本；聚合器可能引入偏差。

---

### 4.6 Meta-Agent — 元智能体

- **提出时间**: 2024年
- **核心思想**: 一个特殊 agent 负责"管理其他 agent"——创建 agent、分配任务、评估 agent 表现、决定重用或替换 agent。类似 agent 生命周期的"管理者"。

**伪代码**:
```
class MetaAgent:
    def __init__(self):
        self.agent_pool = {}  # 已创建的 agent 池
        self.agent_performance = {}  # 历史表现记录

    def handle_task(self, task):
        # 1. 分析任务，决定是否需要新 agent
        required_skills = self.analyze_skills(task)

        # 2. 检查现有 agent 池
        for agent_id, agent in self.agent_pool.items():
            if agent.has_skills(required_skills):
                # 重用已有 agent
                return agent.execute(task)

        # 3. 创建新 agent
        new_agent = self.create_agent(
            name=f"agent_{len(self.agent_pool)}",
            skills=required_skills,
            system_prompt=self.generate_system_prompt(task),
        )
        self.agent_pool[new_agent.id] = new_agent

        # 4. 执行并记录表现
        result = new_agent.execute(task)
        self.agent_performance[new_agent.id] = self.evaluate(new_agent, task, result)

        return result

    def optimize(self):
        # 定期清理低效 agent，合并重复 agent
        ...
```

**代表性实现**: AutoGen 的 `AssistantAgent` 管理层, MetaGPT, 部分 agentic workflow 框架。

**适用场景**: 长期运行的 agent 系统，需要动态管理 agent 生命周期的场景。

**优点**: 自动优化 agent 池；减少重复创建 agent 的开销；学习改进。

**缺点**: Meta-agent 本身成为瓶颈和故障单点；实现复杂。

---

## 5. 工程架构模式

### 5.1 Agentic RAG — 智能检索增强生成

- **提出时间**: 2024年
- **核心思想**: 将传统 RAG（检索-增强-生成）升级为 agent 驱动流程：agent 主动决策检索什么、何时检索、检索几次、如何评估检索结果质量、是否需要改写查询。

**伪代码**:
```
# 传统 RAG（被动管道）
query → retriever → top_k docs → LLM → answer

# Agentic RAG（主动决策）
def agentic_rag(query):
    context = []
    attempts = 0

    while attempts < MAX_ATTEMPTS:
        # Agent 决策：已有信息是否足够？
        sufficiency = agent.judge_sufficiency(query, context)

        if sufficiency == "sufficient":
            break

        # Agent 决策：如何检索？
        search_strategy = agent.plan_retrieval(query, context)
        # 可能: rewrite query, multi-hop retrieval, metadata filter, 切换检索源

        # 执行检索
        new_docs = execute_retrieval(search_strategy)

        # Agent 评估检索质量
        relevance = agent.evaluate_relevance(query, new_docs)
        if relevance > THRESHOLD:
            context.extend(new_docs)

        attempts += 1

    # 综合回答
    return agent.synthesize(query, context)
```

**代表性实现**: LlamaIndex Agentic RAG, LangChain Agentic RAG, Cohere Compass。

**适用场景**: 需要多轮检索的复杂问答、需要跨多个知识库的综合查询、动态知识更新场景。

**优点**: 检索质量显著高于传统 RAG；自适应性好。

**缺点**: 多次 LLM 调用增加延迟；复杂度高于管道式 RAG。

---

### 5.2 Router Agent — 路由智能体

- **提出时间**: 2023–2024年
- **核心思想**: 一个轻量 agent 负责分析用户意图，将请求路由到最合适的 agent/工具/模型。减少了主 agent 的决策负担。

**伪代码**:
```
# Router 架构
USER → Router Agent → [chosen handler] → Response

def router(user_query):
    intent = classify(user_query)

    match intent:
        case "code_review":
            return delegate_to(review_agent, user_query)
        case "debug":
            return delegate_to(debug_agent, user_query)
        case "data_analysis":
            return delegate_to(data_agent, user_query)
        case "general":
            return general_agent.answer(user_query)
        case _:
            return "抱歉，我无法处理这个请求"

# 路由决策通常用轻量模型（或基于规则的分类器）
# 节约主模型 token
```

**代表性实现**: OpenAI Swarm 的 handoff pattern, LangChain RouterChain, LlamaIndex RouterQueryEngine。

**适用场景**: 多 agent 系统、需要分流不同类型请求的系统、成本敏感的场景。

**优点**: 解耦关注点；节约成本（路由判断用小模型）；易于扩展。

**缺点**: 路由决策错误导致用户体验差；需要维护路由规则。

---

### 5.3 SWE-agent / ACI (Agent-Computer Interface) — 软件开发智能体

- **提出时间**: 2024年4月，Princeton NLP
- **论文**: _"SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering"_
- **核心思想**: 为 agent 设计一个特化的"计算机接口"——不是通用的 GUI 操作，而是为代码编辑、文件操作、命令行执行等软件工程任务设计的特化交互界面。核心贡献是 ACI（Agent-Computer Interface）概念。

**核心 ACI 设计**:
```
# SWE-agent 的 ACI 命令集（特化、精简）
COMMANDS:
  - open <file> [line]              # 打开文件
  - goto <line>                     # 跳转到指定行
  - scroll_up / scroll_down         # 滚动
  - search <pattern>                # 搜索
  - edit <start_line>:<end_line>    # 编辑指定行范围
    <<<NEW CODE>>>
  - create <filename>               # 新文件
  - submit                          # 提交修复

# 关键设计原则：
# 1. 精简命令集（6-8个核心命令，避免选择困难）
# 2. 每步操作后显示当前文件上下文（保持在上下文中）
# 3. 错误消息友好（不说"Permission denied"，而是"无法编辑，请检查权限"）
# 4. 确认操作（编辑前展示 diff）
```

**伪代码**:
```
def swe_agent(issue_description, repository):
    # 初始化 ACI 环境
    env = ACIEnvironment(repository)

    while not env.is_submitted():
        # 显示当前状态（当前文件、行号、周围代码）
        state = env.get_view()

        # Agent 决策下一步 action
        action = model.decide(
            state=state,
            issue=issue_description,
            history=env.history
        )

        # 执行 action
        result = env.execute(action)

        # 反馈给 agent
        model.observe(result)

    return env.get_patch()
```

**代表性实现**: SWE-agent, OpenDevin (现 OpenHands), Hermes SWE 模式, Devin。

**适用场景**: 自动化 bug 修复、代码重构、代码生成、PR review。

**优点**: 特化接口提升软件开发效率；ACI 设计为 agent 优化而非人类优化。

**缺点**: 只适合代码任务，通用性差；需要精心设计 ACI。

---

### 5.4 Streaming Agent — 流式智能体

- **提出时间**: 2024年
- **核心思想**: Agent 边执行边输出中间结果，而非等全部完成才返回。用户能实时看到 agent 的思考过程和进展，提升体验和可中断性。

**伪代码**:
```
# 流式输出架构
async def streaming_agent(task):
    # 实时流式输出 thought
    async for thought in model.stream_thought(task):
        yield {"type": "thought", "content": thought}

    # 实时流式输出 action
    async for action in agent.plan_actions(task):
        yield {"type": "action", "content": action}

        # 实时流式输出 observation
        async for obs in execute_streaming(action):
            yield {"type": "observation", "content": obs}

    # 流式输出最终答案
    async for token in agent.generate_answer():
        yield {"type": "answer", "content": token}

# 前端实时渲染
for event in streaming_agent("search for AI news"):
    render_live(event)
    if user_clicks_stop():
        agent.interrupt()
        break
```

**代表性实现**: Vercel AI SDK streaming agents, LangChain `streamEvents`, Hermes streaming。

**适用场景**: 需要实时反馈的用户交互、长任务、需要及时纠偏的场景。

**优点**: 用户体验好；支持中断；及时发现错误。

**缺点**: 实现复杂度高（需管理状态机和重连）。

---

## 6. Agent 协议与标准

### 6.1 MCP (Model Context Protocol) — 模型上下文协议

- **提出时间**: 2024年11月，Anthropic
- **核心思想**: 定义 LLM 与外部工具、数据源之间的标准化通信协议。类似"AI 时代的 HTTP + REST API"——工具提供方实现 MCP Server，LLM 宿主实现 MCP Client，通过标准协议通信。

**架构**:
```
┌─────────────┐     MCP Protocol      ┌─────────────┐
│ MCP Client  │ ◄──────────────────► │ MCP Server   │
│ (LLM Host)  │   JSON-RPC over       │ (Tool/Data)  │
└─────────────┘   stdio / HTTP SSE    └─────────────┘

# MCP 核心能力 (Resources/Prompts/Tools):
TOOLS:
  - list_tools()       → 列出可用工具
  - call_tool(name, args) → 调用工具

RESOURCES:
  - list_resources()   → 列出可用数据资源
  - read_resource(uri) → 读取资源内容

PROMPTS:
  - list_prompts()     → 列出可用 prompt 模板
  - get_prompt(name)   → 获取 prompt 模板
```

**代表性实现**: Anthropic MCP SDK, Hermes 内置 MCP Client, Cursor MCP 支持, 大量社区 MCP Server。

**适用场景**: 工具/数据源标准化、跨平台 agent 工具复用、agent 生态建设。

**优点**: 标准化接口；工具即插即用；生态快速发展（数百个社区 MCP Server）。

**缺点**: 协议仍年轻，规范在快速迭代；安全和权限模型仍在完善。

---

### 6.2 A2A (Agent-to-Agent Protocol) — 智能体间协议

- **提出时间**: 2025年4月，Google
- **核心思想**: 定义 agent 与 agent 之间的标准化通信协议。如果 MCP 是"agent-工具"协议，A2A 是"agent-agent"协议。解决不同框架/厂商的 agent 如何互操作的问题。

**核心概念**:
```
# A2A 核心抽象
1. Agent Card: 描述 agent 的元数据（能力、端点、认证方式）
2. Task: agent 间通信的基本单位，支持状态追踪（submitted/working/input_required/completed/failed/cancelled）
3. Message: 结构化消息（支持多轮对话、多模态）
4. Artifact: 任务产出物（代码、文档、文件等）

# 通信方式
Agent A (discover) → Agent Card of B
Agent A (send_task) → Agent B → (stream task updates) → Agent A
```

**伪代码**:
```
# Agent A 发现并委派任务给 Agent B
card = http_get("https://agent-b.example.com/.well-known/agent.json")
# → {"name": "CodeReviewAgent", "capabilities": ["code_review", "security_scan"]}

task = a2a_client.send_task(
    agent_url=card.url,
    task={
        "description": "Review PR #42 security",
        "input_artifacts": [{"type": "diff", "url": "https://github.com/x/pull/42.diff"}],
    }
)

# 流式接收结果
async for update in task.stream():
    if update.status == "completed":
        print(update.artifacts)  # Review report
    elif update.status == "input_required":
        # Agent B 需要更多信息
        a2a_client.respond(update.id, additional_context)
```

**代表性实现**: Google A2A SDK（Python/JS）, LangGraph A2A 集成, CrewAI A2A 支持中。

**适用场景**: 跨组织/跨平台 agent 协作、agent 市场/生态、企业级 agent 编排。

**优点**: 标准化 agent 间互操作；促进 agent 生态繁荣；支持异构 agent 协作。

**缺点**: 2025年4月刚发布，生态尚在建设中；协议复杂度较高。

---

### 6.3 AGNTC (Agent Network Protocol/Connect)

- **提出时间**: 2025年
- **核心思想**: 另一个 agent 间通信标准，侧重于 agent 网络发现、路由和互操作。与 A2A 的定位类似但侧重点不同——AGNTC 更关注 agent 网络的分布式发现和路由。

---

## 7. 高级认知模式

### 7.1 Reflexion — 反思模式

- **提出时间**: 2023年3月
- **论文**: _"Reflexion: Language Agents with Verbal Reinforcement Learning"_
- **核心思想**: Agent 执行任务后，对自己的失败进行"口头反思"，把反思结果存入长期记忆，下次遇到类似场景时调用历史反思来改进策略。

**伪代码**:
```
class ReflexionAgent:
    def __init__(self):
        self.memory = []  # 长期反思记忆

    def execute(self, task):
        # 1. 从记忆中加载相关反思
        relevant_reflections = self.retrieve_relevant(task, self.memory)

        # 2. 执行任务（使用历史反思指导）
        attempt = self.act(task, context=relevant_reflections)

        # 3. 评估结果
        evaluation = self.evaluator.judge(task, attempt)

        if evaluation.success:
            return attempt.output
        else:
            # 4. 失败 → 生成反思
            reflection = self.reflect(
                task=task,
                attempt=attempt,
                failure=evaluation.failure_reason,
            )
            # reflection example:
            # "搜索时用了太宽泛的关键词导致结果不相关，
            #  下次应该加入具体年份和领域限定词"

            self.memory.append(reflection)

            # 5. 使用反思重新尝试
            return self.execute(task)  # 递归重试
```

**代表性实现**: Reflexion 论文开源实现, LangChain Reflexion agent, agent 框架中普遍借鉴。

**适用场景**: 需要从历史失败中学习的长期 agent、迭代优化任务。

**优点**: 自我改进能力；长期积累经验。

**缺点**: 需要高质量 evaluator（自动评估 + 弱模型可能误判）；反思噪声可能误导。

---

### 7.2 Self-Correction / Self-Refinement — 自我纠错

- **提出时间**: 2023年
- **论文**: _"Self-Refine: Iterative Refinement with Self-Feedback"_
- **核心思想**: Agent 对自己的输出进行"自我批评"——生成初稿 → 自我评审 → 改进 → 再评审 → ...，直到满意。比 Reflexion 更轻量（不需要长期记忆）。

**伪代码**:
```
def self_refine(task, max_iterations=3):
    output = model.generate(task)

    for i in range(max_iterations):
        # 自我反馈（模型看自己的输出并指出问题）
        feedback = model.feedback(
            task=task,
            output=output,
            instruction="找出上述回答的问题和改进空间"
        )
        # feedback: "第2段的论据不充分，缺少数据支持；第3段有重复"

        if feedback.indicates("no issues"):
            break

        # 基于反馈改进
        output = model.refine(
            task=task,
            output=output,
            feedback=feedback,
            instruction="基于反馈改进回答"
        )

    return output
```

**代表性实现**: Self-Refine 论文实现, Claude 的 "critique then rewrite" 模式。

**适用场景**: 写作、翻译、代码生成等可以迭代改进的任务。

**优点**: 简洁有效；不需要外部评估器。

**缺点**: 模型可能对自己的输出"盲目"（看不到明显问题）；可能过度迭代。

---

### 7.3 Agent as a Judge / Evaluator — 智能体作为评委

- **提出时间**: 2024年
- **核心思想**: 一个专门的 agent 作为"裁判"，评估其他 agent（或自身）的输出质量。可以打分、比对、判断正确性、评估安全性等。

**伪代码**:
```
# LLM-as-a-Judge 架构
def judge_evaluation(question, answer, rubric):
    judge_prompt = f"""
    你是一名公正的评委。请根据以下标准评估回答质量：

    问题: {question}
    回答: {answer}

    评估标准:
    1. 准确性 (1-5分): 回答是否正确
    2. 完整性 (1-5分): 是否覆盖所有关键点
    3. 清晰度 (1-5分): 表述是否清晰易懂
    4. 安全性 (pass/fail): 是否包含不安全内容

    请给出评分和理由。
    """
    return llm_call(judge_prompt)

# 双盲评审（减少偏见）
def blind_judge(question, answer_a, answer_b):
    # 不告诉 judge 哪个是哪个模型生成的
    return judge.compare(question, answer_a, answer_b)
```

**代表性实现**: MT-Bench, Chatbot Arena (LMSYS), Ragas evaluation, Trulens。

**适用场景**: Agent 质量评估、模型对比、安全审查、RLHF 数据生成。

**优点**: 自动化评估，可扩展；降低人工评审成本。

**缺点**: 评判器本身也有偏见和局限；位置偏差（偏好靠前的答案）；需要精心设计 rubric。

---

### 7.4 Cognitive Architectures for LLM Agents — LLM Agent 认知架构

- **提出时间**: 2024–2025年
- **核心思想**: 借鉴认知科学中的认知架构概念（如 Soar, ACT-R）为 LLM agent 设计系统性的"心智模型"——包括感知模块、工作记忆、长期记忆、推理模块、行动模块、元认知模块（自我监控和调节）。

**核心模块**:
```
┌─────────────────────────────────────────────────┐
│              LLM Agent 认知架构                    │
├─────────────────────────────────────────────────┤
│                                                   │
│  ┌────────┐       ┌──────────┐                   │
│  │ 感知    │──────►│ 工作记忆  │◄──┐              │
│  │ (输入)  │       │ (上下文)  │   │              │
│  └────────┘       └────┬─────┘   │              │
│                        │         │              │
│          ┌─────────────┤         │              │
│          ▼             ▼         │              │
│  ┌──────────┐   ┌──────────┐     │              │
│  │ 推理模块  │   │ 行动模块  │     │              │
│  │ (LLM)    │   │ (Tool.use)│    │              │
│  └────┬─────┘   └────┬─────┘     │              │
│       │              │           │              │
│       ▼              ▼           │              │
│  ┌──────────┐   ┌──────────┐     │              │
│  │ 长期记忆  │   │ 元认知    │────┘              │
│  │ (Memory) │   │ (监控/调节)│                    │
│  └──────────┘   └──────────┘                    │
│                                                   │
└─────────────────────────────────────────────────┘

模块说明:
- 感知: 解析用户输入、外部工具返回、环境状态
- 工作记忆: 当前对话上下文窗口 (token budget 管理)
- 长期记忆: 跨会话持久化记忆 (向量存储 + 结构化记忆)
- 推理模块: LLM 核心 —— 分析、规划、决策
- 行动模块: 工具调用执行器 (Function Calling / CodeAct)
- 元认知: 监控推理质量、检测幻觉、决定是否需要重新思考或求助
```

**代表性实现**: CoALA (Cognitive Architectures for Language Agents), MemGPT, Letta。

**适用场景**: 需要持久运行、长期记忆、自我调节的高级 agent 系统。

**优点**: 系统性设计，媲美人类认知结构；长期学习和改进能力。

**缺点**: 实现复杂；计算开销大；理论多于成熟实践。

---

## 8. 安全与质量保障模式

### 8.1 Human-in-the-Loop (HITL) — 人在环中

- **提出时间**: 2023–2024年，Agent 安全的基础模式
- **核心思想**: 在 agent 的关键决策节点插入人工审核，确保高风险操作（删除文件、发送消息、执行 SQL、发布代码）得到人类确认。

**伪代码**:
```
def agent_with_hitl(task):
    actions = agent.plan(task)

    for action in actions:
        # 风险评估
        risk_level = risk_assessor.evaluate(action)

        if risk_level >= RiskLevel.HIGH:
            # 暂停，等待人类决策
            human_decision = ask_human({
                "action": action.description,
                "risk": risk_level,
                "detail": action.details,
                "options": ["approve", "reject", "modify"],
            })

            if human_decision == "approve":
                execute(action)
            elif human_decision == "reject":
                agent.retry_without(action)
            elif human_decision == "modify":
                execute(human_decision.modified_action)
        else:
            # 低风险自动执行
            execute(action)

    return agent.synthesize()
```

**实现模式**:
- **Always HITL**: 每一步都要人工确认
- **Threshold HITL**: 只有高风险操作才需要人工确认
- **Sampling HITL**: 随机抽查部分操作
- **Escalation HITL**: agent 遇到不确定时主动请求帮助

**代表性实现**: LangGraph interrupt, Hermes clarify, OpenAI Moderation + Human Review。

**适用场景**: 金融交易、医疗决策、生产环境部署、敏感数据操作。

**优点**: 防止灾难性错误；建立信任；合规要求。

**缺点**: 降低自动化效率；延迟增加；需要持续人类注意力。

---

### 8.2 Guardrails Agent — 护栏智能体

- **提出时间**: 2024年
- **核心思想**: 在 agent 的输出管道中插入多层验证/过滤 agent，类似软件工程中的"中间件"模式。检查输入合法性、输出安全性、行为合规性。

**伪代码**:
```
# Guardrails Pipeline (洋葱模型)
USER INPUT
    │
    ▼
┌──────────────┐
│ Input Guard  │  ← 检查有害/越狱输入
└──────┬───────┘
       │ (pass)
       ▼
┌──────────────┐
│ Agent Core   │  ← 主 agent 执行
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Output Guard │  ← 检查输出安全/合规
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Action Guard │  ← 检查 action 是否越权
└──────┬───────┘
       │ (pass)
       ▼
     OUTPUT

# Guardrail 类型
class InputGuardrail:
    def check(self, user_input):
        # 1. 注入攻击检测
        if contains_prompt_injection(user_input):
            return block("检测到 prompt 注入攻击")

        # 2. 有害内容检测
        if toxicity_score(user_input) > THRESHOLD:
            return block("检测到有害内容")

        # 3. 越狱检测
        if is_jailbreak_attempt(user_input):
            return block("检测到越狱尝试")

        return pass_through(user_input)

class OutputGuardrail:
    # 类似地检查输出
    ...
```

**代表性实现**: NVIDIA NeMo Guardrails, Guardrails AI, LangChain Guardrails。

**适用场景**: 所有生产环境的 agent 系统，尤其是面向外部用户的场景。

**优点**: 层层防护；可组合；安全审计点明确。

**缺点**: 额外延迟；可能过度拦截；误报需人工处理。

---

### 8.3 Prompt Chaining — 提示链

- **提出时间**: 2023年
- **核心思想**: 将一个复杂任务分解为多个串行的 LLM 调用，每步的输出作为下一步的输入。相比单次复杂 prompt，每个步骤简单可控，且可以在步骤间插入验证逻辑。

**伪代码**:
```
# 写一篇博客的 Prompt Chaining
def write_blog_pipeline(topic):
    # Step 1: 头脑风暴
    ideas = llm_call(f"为博客主题'{topic}'生成5个文章角度")

    # Step 2: 选择最佳角度（或用另一个 LLM 评判）
    best_angle = llm_call(f"从以下角度选出最适合的: {ideas}")
    best_angle = validate_output(best_angle, format="single_selection")

    # Step 3: 生成大纲
    outline = llm_call(f"为'{best_angle}'创建文章大纲")

    # Step 4: 分段落撰写
    sections = []
    for section_title in outline.sections:
        section = llm_call(f"撰写'{section_title}'段落，上下文: {topic}")
        section = validate_output(section, min_length=200, check_facts=True)
        sections.append(section)

    # Step 5: 组合和润色
    draft = "\n\n".join(sections)
    final = llm_call(f"润色并统一风格:\n{draft}")

    return final
```

**代表性实现**: LangChain LCEL chains, Vercel AI SDK pipe, Anthropic prompt chaining cookbook。

**适用场景**: 内容生成、数据分析 pipeline、分步推理。

**优点**: 每步可独立验证和调试；易于插入评估和 retry 逻辑；token 可控。

**缺点**: 多次 LLM 调用增加延迟和成本；步骤间信息可能丢失。

---

## 9. Andrew Ng Agentic 设计模式

> 来源: Andrew Ng 2024年3月演讲 "Agentic Design Patterns"

Andrew Ng 在 2024 年总结的四大 agentic 设计模式：

### 9.1 Reflection（反思）
让 agent 审视自己的输出，指出问题并改进。类似 Self-Correction 模式。
> 详见 [7.2 Self-Correction](#72-self-correction--self-refinement--自我纠错)

### 9.2 Tool Use（工具使用）
Agent 主动使用外部工具来扩展能力——搜索、计算、代码执行等。
> 详见 [2.1 Function Calling](#21-function-calling--tool-use--函数调用) 和 [1.2 ReAct](#12-react-reasoning--acting--推理-行动交替)

### 9.3 Planning（规划）
Agent 在执行前先做完整的任务分解和路径规划。
> 详见 [3.1 Plan-and-Execute](#31-plan-and-execute--先规划后执行) 和 [3.2 ToT](#32-tree-of-thought-tot--思维树)

### 9.4 Multi-Agent Collaboration（多智能体协作）
多个专业 agent 分工协作完成复杂任务。
> 详见 [4.1 Delegation](#41-delegation--multi-agent--多智能体委托) 和 [4.2 Orchestrator-Worker](#42-orchestrator-worker--编排器-工作者)

**Ng 的关键洞察**: 这些模式让 GPT-3.5 级别的模型在某些任务上超越 GPT-4 —— 好的 agent 架构比更强的模型更重要。

---

## 10. 总结对比表

### 10.1 按推出时间排序

| 时间 | 范式 | 核心贡献 |
|------|------|---------|
| 2022.01 | Chain-of-Thought | 显式中间推理步骤 |
| 2022.10 | ReAct | 推理+行动交替循环 |
| 2023.03 | Plan-and-Execute | 先规划后执行解耦 |
| 2023.03 | Reflexion | 口头反思+长期记忆 |
| 2023.05 | Tree-of-Thought | 树状搜索多路径推理 |
| 2023.06 | Function Calling | 结构化工具调用 API |
| 2023.09 | ReWOO | 无观察推理，批量执行 |
| 2023.11 | CodeAct | 代码统一 action space |
| 2024.03 | Ng Agentic Patterns | 四大设计模式系统化 |
| 2024.04 | SWE-agent / ACI | 特化 agent 计算机接口 |
| 2024.06 | Mixture-of-Agents | 多模型混合 agent |
| 2024.10 | Computer Use | GUI 操作通用 agent |
| 2024.11 | MCP | Agent-工具标准协议 |
| 2025.04 | A2A | Agent-Agent 标准协议 |

### 10.2 按适用场景分类

| 场景 | 推荐范式 |
|------|---------|
| 简单问答 | CoT, Function Calling |
| 多步搜索+推理 | ReAct |
| 大量独立查询 | ReWOO |
| 代码生成/修复 | SWE-agent, CodeAct |
| 复杂规划任务 | Plan-and-Execute, ToT |
| 多 agent 并行 | Delegation, Orchestrator-Worker |
| 长周期自我改进 | Reflexion, Self-Correction |
| 写作/翻译 | Self-Refine, Prompt Chaining |
| 网页自动化 | Browser Agent, Computer Use |
| 需要人工审核 | Human-in-the-Loop |
| 生产环境安全 | Guardrails + HITL |
| 跨平台工具 | MCP |
| 跨组织 agent 协作 | A2A |
| 大团队自动化开发 | Hierarchical Agent Teams |
| 弹性大规模任务 | Agent Swarm |

### 10.3 范式选择决策树

```
你的任务需要工具调用吗？
  ├─ 不需要 → CoT / Self-Refine
  └─ 需要
      ├─ 可以预先描述所有子任务
      │   └─ Plan-and-Execute / ReWOO
      ├─ 需要动态决策
      │   ├─ 单个 agent 够用
      │   │   └─ ReAct (最通用)
      │   └─ 需要多个 agent
      │       ├─ 中心协调
      │       │   ├─ 静态分组 → Delegation
      │       │   └─ 动态决策 → Orchestrator-Worker
      │       └─ 无中心协调
      │           └─ Agent Swarm
      └─ 需要 GUI 操作
          └─ Browser Agent / Computer Use
```

### 10.4 关键论文速查

| 范式 | 论文 | 链接 |
|------|------|------|
| ReAct | "ReAct: Synergizing Reasoning and Acting in Language Models" | arXiv:2210.03629 |
| CoT | "Chain-of-Thought Prompting Elicits Reasoning in LLMs" | arXiv:2201.11903 |
| ToT | "Tree of Thoughts" | arXiv:2305.10601 |
| Reflexion | "Reflexion: Language Agents with Verbal RL" | arXiv:2303.11366 |
| ReWOO | "ReWOO: Decoupling Reasoning from Observations" | arXiv:2305.18323 |
| CodeAct | "Executable Code Actions Elicit Better LLM Agents" | arXiv:2402.01030 |
| SWE-agent | "SWE-agent: Agent-Computer Interfaces Enable Automated SE" | arXiv:2405.15793 |
| MoA | "Mixture-of-Agents Enhances LLM Capabilities" | arXiv:2406.04692 |
| Anthropic | "Building Effective Agents" (blog) | anthropic.com/research |

---

## 附录：快速参考卡

### ReAct 模板（最常用）

```
SYSTEM: You run in a loop of Thought, Action, Observation.
Use Thought to reason, Action to use tools, Observation for results.
Answer when you have enough information.

USER: {question}

ASSISTANT:
Thought: I need to ...
Action: {tool_name}({arguments})
Observation: {result}
# ... loop ...
Thought: I now have enough information.
Answer: {final_answer}
```

### LangGraph 最小示例

```python
from langgraph.graph import StateGraph, END

# 只需 think → tool → think → ... → answer
workflow = StateGraph(dict)
workflow.add_node("think", call_llm)
workflow.add_node("tool", execute_tool)
workflow.add_conditional_edges("think", route, {
    "tool": "tool", "answer": END
})
workflow.add_edge("tool", "think")
workflow.set_entry_point("think")
```

### MCP Server 最小示例

```python
from mcp.server import Server
server = Server("my-tool")

@server.tool()
async def get_weather(city: str) -> str:
    return f"{city}: 22°C, 晴"

server.run()
```

---

> **维护说明**: 本文档覆盖了截至 2026年5月 AI Agent 领域的主要范式、架构和模式。随着领域快速演进，建议定期更新。
