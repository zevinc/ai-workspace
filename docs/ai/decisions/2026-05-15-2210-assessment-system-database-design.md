---
title: 通用考试考核系统数据库与API设计方案
tags:
  - exam-system
  - assessment
  - workflow-engine
  - database-design
  - spring-boot
  - dynamic-workflow
summary: >
  支持三种考核类型（考试排考/绩效考核/技能评估）的通用系统设计方案。
  核心设计：模板-实例模式 + JSON配置驱动的动态流程引擎，
  覆盖完整数据库表结构、RESTful API设计、三种考核类型的流程配置示例、
  以及关键技术决策与实现建议。
created: 2026-05-15
---

# 通用考试考核系统设计方案

## 1. 设计目标

构建一套通用考核引擎，支持三种业务场景：

| 类型 | 业务场景 | 典型流程 |
|------|---------|---------|
| EXAM | 考试排考 | 创建计划 → 报名 → 出卷 → 考场分配 → 考试 → 阅卷 → 成绩发布 → 申诉 → 归档 |
| PERFORMANCE | 绩效考核 | 创建计划 → 自评 → 同事评价 → 上级评价 → 复核 → 沟通 → 归档 |
| TECHNICAL | 技能评估 | 创建计划 → 题库组卷 → 在线答题 → 自动/人工评分 → 结果发布 → 归档 |

**核心约束：流程不可硬编码，须由业务方动态配置。**

---

## 2. 架构概览

```
┌──────────────────────────────────────────────────────────┐
│                    考核模板 (Template)                     │
│  定义考核类型 + 流程阶段配置 (JSON) + 默认规则              │
└──────────────────────┬───────────────────────────────────┘
                       │ 实例化
                       ▼
┌──────────────────────────────────────────────────────────┐
│                    考核计划 (Plan)                         │
│  绑定模板 + 时间范围 + 参与人员 + 运行时状态                │
│                                                          │
│  ┌────────────────────────────────────────────────────┐  │
│  │              流程引擎 (Workflow Engine)              │  │
│  │  读取模板 JSON → 创建阶段实例 → 校验前置条件         │  │
│  │  → 角色权限校验 → 执行动作 → 状态转移 → 记录日志     │  │
│  └────────────────────────────────────────────────────┘  │
│                                                          │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────────┐ │
│  │ 阶段 1   │→│ 阶段 2   │→│ 阶段 3   │→│   ... 归档   │ │
│  │ PENDING  │  │ ACTIVE   │  │ PENDING  │  │  COMPLETED  │ │
│  └─────────┘  └─────────┘  └─────────┘  └─────────────┘ │
└──────────────────────────────────────────────────────────┘
```

---

## 3. 数据库表设计

### 3.1 核心表关系总览

```
assessment_template (1) ──< (N) workflow_stage_def
       │
       │ 1
       │
       ▼ N
assessment_plan ──< plan_participant (用户角色分配)
       │
       │ 1
       ├──< plan_stage_instance (运行时阶段状态)
       │
       ├──< stage_action_log (操作审计日志)
       │
       └──< assessment_result (考核结果)
```

### 3.2 考核模板表 `assessment_template`

```sql
CREATE TABLE assessment_template (
    id            BIGINT AUTO_INCREMENT PRIMARY KEY,
    name          VARCHAR(200)  NOT NULL COMMENT '模板名称',
    description   TEXT          COMMENT '模板描述',
    type          VARCHAR(30)   NOT NULL COMMENT '考核类型: EXAM / PERFORMANCE / TECHNICAL',
    status        VARCHAR(20)   NOT NULL DEFAULT 'DRAFT' COMMENT 'DRAFT / PUBLISHED / ARCHIVED',
    workflow_config JSON        NOT NULL COMMENT '流程阶段配置 (JSON)',
    default_rules JSON          COMMENT '默认规则配置 (JSON)',
    created_by    BIGINT        NOT NULL,
    created_at    DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    DATETIME      ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_type (type),
    INDEX idx_status (status)
) COMMENT '考核模板';
```

### 3.3 流程阶段定义表 `workflow_stage_def`

> 注：此表是 `workflow_config` JSON 的关系化冗余存储，用于查询加速。
> 系统以 JSON 为准，本表在保存模板时同步写入。

```sql
CREATE TABLE workflow_stage_def (
    id              BIGINT AUTO_INCREMENT PRIMARY KEY,
    template_id     BIGINT        NOT NULL,
    stage_code      VARCHAR(50)   NOT NULL COMMENT '阶段编码，如 REGISTRATION、EXAM',
    stage_name      VARCHAR(100)  NOT NULL COMMENT '阶段名称',
    sort_order      INT           NOT NULL COMMENT '排序号',
    stage_config    JSON          NOT NULL COMMENT '阶段配置 (JSON)',

    UNIQUE KEY uk_template_stage (template_id, stage_code),
    INDEX idx_template_order (template_id, sort_order),
    FOREIGN KEY (template_id) REFERENCES assessment_template(id)
) COMMENT '流程阶段定义';
```

**`stage_config` JSON 结构：**

```json
{
  "allowed_roles": ["ADMIN", "EXAMINER"],
  "precondition_stages": ["REGISTRATION"],
  "actions": [
    {"code": "approve", "name": "审核通过", "target_status": "COMPLETED"},
    {"code": "reject",  "name": "驳回",     "target_status": "REJECTED"}
  ],
  "auto_transition": false,
  "timeout_hours": 48,
  "required_fields": ["comment"],
  "notify_on_enter": true,
  "notify_on_complete": true
}
```

**字段说明：**

| 字段 | 说明 |
|------|------|
| `allowed_roles` | 哪些角色可以在此阶段操作 |
| `precondition_stages` | 必须完成的前置阶段（stage_code 列表） |
| `actions` | 可执行的操作列表，每个操作定义目标状态 |
| `auto_transition` | 是否满足条件后自动流转 |
| `timeout_hours` | 超时时间，超时后触发 `on_timeout` 动作 |
| `required_fields` | 操作时需要填写的必填字段 |
| `notify_on_enter` | 进入阶段时是否通知相关人员 |
| `notify_on_complete` | 完成阶段时是否通知相关人员 |

### 3.4 考核计划表 `assessment_plan`

```sql
CREATE TABLE assessment_plan (
    id            BIGINT AUTO_INCREMENT PRIMARY KEY,
    template_id   BIGINT        NOT NULL,
    name          VARCHAR(200)  NOT NULL COMMENT '计划名称',
    description   TEXT,
    type          VARCHAR(30)   NOT NULL COMMENT '冗余模板类型，便于查询',
    status        VARCHAR(30)   NOT NULL DEFAULT 'DRAFT'
                  COMMENT 'DRAFT / IN_PROGRESS / COMPLETED / CANCELLED',
    current_stage VARCHAR(50)   COMMENT '当前所处阶段 stage_code',
    start_time    DATETIME      COMMENT '计划开始时间',
    end_time      DATETIME      COMMENT '计划结束时间',
    created_by    BIGINT        NOT NULL,
    created_at    DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    DATETIME      ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_type (type),
    INDEX idx_status (status),
    INDEX idx_template (template_id),
    FOREIGN KEY (template_id) REFERENCES assessment_template(id)
) COMMENT '考核计划';
```

### 3.5 计划参与者表 `plan_participant`

```sql
CREATE TABLE plan_participant (
    id            BIGINT AUTO_INCREMENT PRIMARY KEY,
    plan_id       BIGINT        NOT NULL,
    user_id       BIGINT        NOT NULL,
    role          VARCHAR(20)   NOT NULL COMMENT 'ADMIN / EXAMINER / CANDIDATE',
    assigned_at   DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    assigned_by   BIGINT,

    UNIQUE KEY uk_plan_user_role (plan_id, user_id, role),
    INDEX idx_plan_role (plan_id, role),
    FOREIGN KEY (plan_id) REFERENCES assessment_plan(id)
) COMMENT '计划参与者（同一用户可在同一计划中担任多个角色）';
```

### 3.6 计划阶段实例表 `plan_stage_instance`

> 运行时状态表，每个计划在每个阶段产生一条记录。

```sql
CREATE TABLE plan_stage_instance (
    id              BIGINT AUTO_INCREMENT PRIMARY KEY,
    plan_id         BIGINT        NOT NULL,
    stage_def_id    BIGINT        NOT NULL,
    stage_code      VARCHAR(50)   NOT NULL,
    status          VARCHAR(20)   NOT NULL DEFAULT 'PENDING'
                    COMMENT 'PENDING / IN_PROGRESS / COMPLETED / SKIPPED / REJECTED / TIMEOUT',
    started_at      DATETIME,
    completed_at    DATETIME,
    operator_id     BIGINT        COMMENT '操作人',
    result_data     JSON          COMMENT '阶段产出的数据 (JSON)',
    remark          TEXT,

    UNIQUE KEY uk_plan_stage (plan_id, stage_code),
    INDEX idx_plan_status (plan_id, status),
    FOREIGN KEY (plan_id) REFERENCES assessment_plan(id),
    FOREIGN KEY (stage_def_id) REFERENCES workflow_stage_def(id)
) COMMENT '计划阶段实例（运行时状态）';
```

### 3.7 考核结果表 `assessment_result`

```sql
CREATE TABLE assessment_result (
    id              BIGINT AUTO_INCREMENT PRIMARY KEY,
    plan_id         BIGINT        NOT NULL,
    candidate_id    BIGINT        NOT NULL COMMENT '被考核人',
    examiner_id     BIGINT        COMMENT '评分人',
    eval_type       VARCHAR(30)   COMMENT '评价类型: SELF / PEER / MANAGER / AUTO',
    score           DECIMAL(10,2) COMMENT '分数',
    grade           VARCHAR(20)   COMMENT '等级: A/B/C/D',
    status          VARCHAR(20)   NOT NULL DEFAULT 'DRAFT'
                    COMMENT 'DRAFT / SUBMITTED / CONFIRMED / APPEALED',
    detail_data     JSON          COMMENT '详细评分数据 (JSON)',
    comment         TEXT,
    submitted_at    DATETIME,

    INDEX idx_plan_candidate (plan_id, candidate_id),
    INDEX idx_plan_eval_type (plan_id, eval_type),
    FOREIGN KEY (plan_id) REFERENCES assessment_plan(id)
) COMMENT '考核结果';
```

### 3.8 阶段操作日志表 `stage_action_log`

```sql
CREATE TABLE stage_action_log (
    id            BIGINT AUTO_INCREMENT PRIMARY KEY,
    plan_id       BIGINT        NOT NULL,
    stage_code    VARCHAR(50)   NOT NULL,
    action        VARCHAR(50)   NOT NULL COMMENT '操作编码',
    operator_id   BIGINT        NOT NULL,
    from_status   VARCHAR(20),
    to_status     VARCHAR(20),
    detail        JSON          COMMENT '操作详情 (JSON)',
    created_at    DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_plan (plan_id),
    INDEX idx_operator_time (operator_id, created_at),
    FOREIGN KEY (plan_id) REFERENCES assessment_plan(id)
) COMMENT '阶段操作审计日志';
```

### 3.9 扩展表（按考核类型按需启用）

```sql
-- 考试排考专用
CREATE TABLE exam_session (
    id            BIGINT AUTO_INCREMENT PRIMARY KEY,
    plan_id       BIGINT        NOT NULL,
    room_name     VARCHAR(200)  NOT NULL COMMENT '考场名称',
    location      VARCHAR(300)  COMMENT '考场地点',
    capacity      INT           NOT NULL DEFAULT 0,
    start_time    DATETIME      NOT NULL,
    end_time      DATETIME      NOT NULL,
    proctor_ids   JSON          COMMENT '监考人 ID 列表',
    status        VARCHAR(20)   NOT NULL DEFAULT 'PENDING',

    INDEX idx_plan (plan_id),
    FOREIGN KEY (plan_id) REFERENCES assessment_plan(id)
) COMMENT '考试场次（EXAM 类型专用）';

CREATE TABLE exam_seat (
    id            BIGINT AUTO_INCREMENT PRIMARY KEY,
    session_id    BIGINT        NOT NULL,
    candidate_id  BIGINT        NOT NULL,
    seat_number   VARCHAR(20),

    UNIQUE KEY uk_session_candidate (session_id, candidate_id),
    FOREIGN KEY (session_id) REFERENCES exam_session(id)
) COMMENT '考生座位分配（EXAM 类型专用）';

-- 技能评估专用
CREATE TABLE question_bank (
    id            BIGINT AUTO_INCREMENT PRIMARY KEY,
    type          VARCHAR(30)   NOT NULL COMMENT 'SINGLE_CHOICE / MULTI_CHOICE / SHORT_ANSWER / CODING',
    category      VARCHAR(100)  COMMENT '分类',
    difficulty    VARCHAR(10)   NOT NULL DEFAULT 'MEDIUM' COMMENT 'EASY / MEDIUM / HARD',
    content       TEXT          NOT NULL COMMENT '题目内容 (JSON: 题干 + 选项)',
    answer        TEXT          COMMENT '参考答案 (JSON)',
    score         DECIMAL(5,2)  NOT NULL DEFAULT 0,
    tags          JSON          COMMENT '标签',
    status        VARCHAR(20)   NOT NULL DEFAULT 'ACTIVE',

    INDEX idx_type_category (type, category),
    INDEX idx_difficulty (difficulty)
) COMMENT '题库（TECHNICAL 类型专用）';

CREATE TABLE exam_paper (
    id            BIGINT AUTO_INCREMENT PRIMARY KEY,
    plan_id       BIGINT        NOT NULL,
    name          VARCHAR(200)  NOT NULL,
    total_score   DECIMAL(8,2)  NOT NULL DEFAULT 0,
    pass_score    DECIMAL(8,2),
    duration_min  INT           COMMENT '考试时长（分钟）',
    questions     JSON          NOT NULL COMMENT '试卷题目列表 (JSON)',
    created_at    DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_plan (plan_id),
    FOREIGN KEY (plan_id) REFERENCES assessment_plan(id)
) COMMENT '试卷（TECHNICAL 类型专用）';

CREATE TABLE candidate_answer (
    id            BIGINT AUTO_INCREMENT PRIMARY KEY,
    paper_id      BIGINT        NOT NULL,
    candidate_id  BIGINT        NOT NULL,
    answers       JSON          COMMENT '考生答案 (JSON)',
    score         DECIMAL(8,2),
    auto_score    DECIMAL(8,2)  COMMENT '自动评分分数',
    status        VARCHAR(20)   NOT NULL DEFAULT 'ANSWERING'
                  COMMENT 'ANSWERING / SUBMITTED / GRADED',
    started_at    DATETIME,
    submitted_at  DATETIME,

    UNIQUE KEY uk_paper_candidate (paper_id, candidate_id),
    FOREIGN KEY (paper_id) REFERENCES exam_paper(id)
) COMMENT '考生答卷（TECHNICAL 类型专用）';
```

---

## 4. 流程引擎设计

### 4.1 核心状态机

```
                    ┌──────────────────────────────┐
                    │      Workflow Engine          │
                    │                              │
   execute_action() │  1. 加载模板 workflow_config  │
   ───────────────► │  2. 校验当前阶段状态          │
                    │  3. 校验前置阶段是否完成       │
                    │  4. 校验操作人角色权限         │
                    │  5. 执行 action 逻辑           │
                    │  6. 更新 plan_stage_instance   │
                    │  7. 判断是否触发自动流转       │
                    │  8. 记录操作日志               │
                    │  9. 发送通知（事件驱动）       │
                    └──────────────────────────────┘
```

### 4.2 workflow_config JSON 完整示例

#### 考试排考 (EXAM)

```json
{
  "type": "EXAM",
  "version": "1.0",
  "stages": [
    {
      "code": "PLAN_INIT",
      "name": "计划创建",
      "order": 1,
      "allowed_roles": ["ADMIN"],
      "precondition_stages": [],
      "actions": [
        {"code": "publish", "name": "发布计划", "target_status": "COMPLETED"}
      ],
      "auto_transition": false,
      "required_fields": ["name", "start_time", "end_time"]
    },
    {
      "code": "REGISTRATION",
      "name": "考生报名",
      "order": 2,
      "allowed_roles": ["CANDIDATE", "ADMIN"],
      "precondition_stages": ["PLAN_INIT"],
      "actions": [
        {"code": "register",   "name": "报名",     "target_status": ""},
        {"code": "close_reg",  "name": "截止报名",  "target_status": "COMPLETED"}
      ],
      "notify_on_enter": true,
      "notify_target": "CANDIDATE"
    },
    {
      "code": "PAPER_PREPARE",
      "name": "出卷",
      "order": 3,
      "allowed_roles": ["EXAMINER"],
      "precondition_stages": ["REGISTRATION"],
      "actions": [
        {"code": "submit_paper", "name": "提交试卷", "target_status": "COMPLETED"}
      ],
      "timeout_hours": 72
    },
    {
      "code": "ROOM_ASSIGN",
      "name": "考场分配",
      "order": 4,
      "allowed_roles": ["ADMIN"],
      "precondition_stages": ["REGISTRATION"],
      "actions": [
        {"code": "assign_room",   "name": "分配考场",   "target_status": ""},
        {"code": "publish_seat",  "name": "发布座位",    "target_status": "COMPLETED"}
      ]
    },
    {
      "code": "EXAM",
      "name": "考试中",
      "order": 5,
      "allowed_roles": ["CANDIDATE", "EXAMINER"],
      "precondition_stages": ["PAPER_PREPARE", "ROOM_ASSIGN"],
      "actions": [
        {"code": "start_exam", "name": "开始考试", "target_status": "IN_PROGRESS"},
        {"code": "submit",     "name": "交卷",     "target_status": "COMPLETED"}
      ],
      "auto_transition": false
    },
    {
      "code": "GRADING",
      "name": "阅卷评分",
      "order": 6,
      "allowed_roles": ["EXAMINER"],
      "precondition_stages": ["EXAM"],
      "actions": [
        {"code": "submit_score", "name": "提交成绩", "target_status": "COMPLETED"}
      ]
    },
    {
      "code": "RESULT_PUBLISH",
      "name": "成绩发布",
      "order": 7,
      "allowed_roles": ["ADMIN"],
      "precondition_stages": ["GRADING"],
      "actions": [
        {"code": "publish", "name": "发布成绩", "target_status": "COMPLETED"},
        {"code": "recall",  "name": "撤回成绩", "target_status": "IN_PROGRESS"}
      ],
      "notify_on_complete": true,
      "notify_target": "CANDIDATE"
    },
    {
      "code": "APPEAL",
      "name": "成绩申诉",
      "order": 8,
      "allowed_roles": ["CANDIDATE", "EXAMINER"],
      "precondition_stages": ["RESULT_PUBLISH"],
      "actions": [
        {"code": "appeal",  "name": "发起申诉", "target_status": "IN_PROGRESS"},
        {"code": "resolve", "name": "处理申诉", "target_status": "COMPLETED"},
        {"code": "skip",    "name": "跳过申诉", "target_status": "SKIPPED"}
      ],
      "optional": true
    },
    {
      "code": "ARCHIVE",
      "name": "归档",
      "order": 9,
      "allowed_roles": ["ADMIN"],
      "precondition_stages": ["APPEAL"],
      "precondition_logic": "ANY",
      "actions": [
        {"code": "archive", "name": "归档", "target_status": "COMPLETED"}
      ]
    }
  ]
}
```

#### 绩效考核 (PERFORMANCE)

```json
{
  "type": "PERFORMANCE",
  "version": "1.0",
  "stages": [
    {
      "code": "PLAN_INIT",
      "name": "创建考核计划",
      "order": 1,
      "allowed_roles": ["ADMIN"],
      "precondition_stages": [],
      "actions": [
        {"code": "publish", "name": "发布计划", "target_status": "COMPLETED"}
      ],
      "required_fields": ["name", "eval_period_start", "eval_period_end"]
    },
    {
      "code": "SELF_EVAL",
      "name": "自评",
      "order": 2,
      "allowed_roles": ["CANDIDATE"],
      "precondition_stages": ["PLAN_INIT"],
      "actions": [
        {"code": "submit_self", "name": "提交自评", "target_status": "COMPLETED"}
      ],
      "notify_on_enter": true,
      "notify_target": "CANDIDATE",
      "timeout_hours": 168
    },
    {
      "code": "PEER_EVAL",
      "name": "同事互评",
      "order": 3,
      "allowed_roles": ["CANDIDATE"],
      "precondition_stages": ["SELF_EVAL"],
      "actions": [
        {"code": "submit_peer", "name": "提交互评", "target_status": "COMPLETED"}
      ],
      "timeout_hours": 168
    },
    {
      "code": "MANAGER_EVAL",
      "name": "上级评价",
      "order": 4,
      "allowed_roles": ["EXAMINER"],
      "precondition_stages": ["SELF_EVAL"],
      "actions": [
        {"code": "submit_eval", "name": "提交评价", "target_status": "COMPLETED"}
      ],
      "required_fields": ["score", "comment", "strengths", "improvements"]
    },
    {
      "code": "REVIEW",
      "name": "结果复核",
      "order": 5,
      "allowed_roles": ["ADMIN"],
      "precondition_stages": ["PEER_EVAL", "MANAGER_EVAL"],
      "actions": [
        {"code": "approve", "name": "审批通过", "target_status": "COMPLETED"},
        {"code": "adjust", "name": "调整分数", "target_status": "COMPLETED"},
        {"code": "reject", "name": "驳回重评", "target_status": "REJECTED"}
      ]
    },
    {
      "code": "FEEDBACK",
      "name": "结果沟通",
      "order": 6,
      "allowed_roles": ["EXAMINER"],
      "precondition_stages": ["REVIEW"],
      "actions": [
        {"code": "confirm",       "name": "确认沟通",     "target_status": "COMPLETED"},
        {"code": "candidate_ack", "name": "被考核人确认",  "target_status": "COMPLETED"}
      ]
    },
    {
      "code": "ARCHIVE",
      "name": "归档",
      "order": 7,
      "allowed_roles": ["ADMIN"],
      "precondition_stages": ["FEEDBACK"],
      "actions": [
        {"code": "archive", "name": "归档", "target_status": "COMPLETED"}
      ]
    }
  ]
}
```

#### 技能评估 (TECHNICAL)

```json
{
  "type": "TECHNICAL",
  "version": "1.0",
  "stages": [
    {
      "code": "PLAN_INIT",
      "name": "创建考核计划",
      "order": 1,
      "allowed_roles": ["ADMIN"],
      "actions": [
        {"code": "publish", "name": "发布计划", "target_status": "COMPLETED"}
      ]
    },
    {
      "code": "PAPER_GEN",
      "name": "组卷",
      "order": 2,
      "allowed_roles": ["EXAMINER"],
      "precondition_stages": ["PLAN_INIT"],
      "actions": [
        {"code": "auto_gen",   "name": "自动组卷", "target_status": "COMPLETED"},
        {"code": "manual_gen", "name": "手动组卷", "target_status": "COMPLETED"}
      ],
      "config": {
        "auto_gen_rules": {
          "strategy": "RANDOM_BY_DIFFICULTY",
          "easy_count": 10,
          "medium_count": 15,
          "hard_count": 5
        }
      }
    },
    {
      "code": "EXAM",
      "name": "在线答题",
      "order": 3,
      "allowed_roles": ["CANDIDATE"],
      "precondition_stages": ["PAPER_GEN"],
      "actions": [
        {"code": "start",  "name": "开始答题", "target_status": "IN_PROGRESS"},
        {"code": "submit", "name": "交卷",     "target_status": "COMPLETED"}
      ],
      "timeout_hours": 2,
      "notify_on_enter": true
    },
    {
      "code": "GRADING",
      "name": "评分",
      "order": 4,
      "allowed_roles": ["EXAMINER"],
      "precondition_stages": ["EXAM"],
      "actions": [
        {"code": "auto_grade",  "name": "自动评分", "target_status": "COMPLETED"},
        {"code": "manual_grade","name": "人工复核", "target_status": "COMPLETED"}
      ],
      "auto_transition": true
    },
    {
      "code": "RESULT_PUBLISH",
      "name": "结果发布",
      "order": 5,
      "allowed_roles": ["ADMIN"],
      "precondition_stages": ["GRADING"],
      "actions": [
        {"code": "publish", "name": "发布结果", "target_status": "COMPLETED"}
      ],
      "notify_on_complete": true
    },
    {
      "code": "ARCHIVE",
      "name": "归档",
      "order": 6,
      "allowed_roles": ["ADMIN"],
      "precondition_stages": ["RESULT_PUBLISH"],
      "actions": [
        {"code": "archive", "name": "归档", "target_status": "COMPLETED"}
      ]
    }
  ]
}
```

### 4.3 前置条件逻辑

```json
// ALL 模式（默认）：所有前置阶段都必须完成
"precondition_stages": ["PAPER_PREPARE", "ROOM_ASSIGN"]

// ANY 模式：任一前置阶段完成即可
"precondition_stages": ["APPEAL"],
"precondition_logic": "ANY"
// 含义：申诉阶段要么 COMPLETED 要么 SKIPPED，任一满足即可进入归档
```

### 4.4 引擎伪代码

```java
@Service
public class WorkflowEngine {

    /**
     * 执行阶段动作
     */
    @Transactional
    public StageActionResult executeAction(Long planId, String stageCode,
                                            String actionCode, Long operatorId,
                                            Map<String, Object> actionData) {

        AssessmentPlan plan = planRepo.findById(planId)
            .orElseThrow(() -> new NotFoundException("Plan not found"));

        AssessmentTemplate template = templateRepo.findById(plan.getTemplateId())
            .orElseThrow(() -> new NotFoundException("Template not found"));

        // 1. 解析 workflow_config
        WorkflowConfig config = WorkflowConfig.fromJson(template.getWorkflowConfig());
        StageConfig stageConfig = config.findStage(stageCode);

        // 2. 校验当前阶段状态
        PlanStageInstance instance = stageInstanceRepo
            .findByPlanIdAndStageCode(planId, stageCode)
            .orElseThrow(() -> new IllegalStateException("Stage not initialized"));
        if (instance.getStatus() != StageStatus.IN_PROGRESS
                && instance.getStatus() != StageStatus.PENDING) {
            throw new IllegalStateException("Stage is not actionable");
        }

        // 3. 校验前置阶段
        validatePreconditions(planId, stageConfig);

        // 4. 校验操作人角色
        PlanParticipant participant = participantRepo
            .findByPlanIdAndUserId(planId, operatorId)
            .orElseThrow(() -> new ForbiddenException("Not a participant"));
        if (!stageConfig.getAllowedRoles().contains(participant.getRole())) {
            throw new ForbiddenException("Role not authorized for this stage");
        }

        // 5. 查找 action 定义
        ActionDef actionDef = stageConfig.findAction(actionCode);

        // 6. 执行 action（可扩展：调用对应的 ActionHandler）
        ActionHandler handler = handlerRegistry.get(actionCode);
        ActionResult result = handler.execute(planId, operatorId, actionData);

        // 7. 更新阶段实例状态
        instance.setStatus(actionDef.getTargetStatus());
        instance.setOperatorId(operatorId);
        instance.setResultData(result.getData());
        instance.setCompletedAt(LocalDateTime.now());
        stageInstanceRepo.save(instance);

        // 8. 检查是否触发自动流转
        tryAutoTransition(planId, config, stageCode);

        // 9. 记录日志
        logAction(planId, stageCode, actionCode, operatorId,
                  instance.getStatus(), actionDef.getTargetStatus(), actionData);

        // 10. 发布事件（异步通知）
        eventPublisher.publish(new StageCompletedEvent(planId, stageCode, operatorId));

        return StageActionResult.success(instance);
    }

    private void tryAutoTransition(Long planId, WorkflowConfig config,
                                    String completedStageCode) {
        config.getStages().stream()
            .filter(s -> s.getPreconditionStages().contains(completedStageCode))
            .filter(StageConfig::getAutoTransition)
            .filter(s -> checkPreconditionsMet(planId, s))
            .forEach(s -> activateStage(planId, s.getCode()));
    }
}
```

---

## 5. RESTful API 设计

### 5.1 基础路径

```
/api/v1/assessment-templates   — 模板管理
/api/v1/assessment-plans       — 计划管理
/api/v1/assessment-plans/{planId}/stages    — 阶段操作
/api/v1/assessment-plans/{planId}/results   — 结果管理
```

### 5.2 模板管理

```
POST   /api/v1/assessment-templates
       创建考核模板
       Body: { name, description, type, workflowConfig }

GET    /api/v1/assessment-templates
       模板列表，支持 type/status 筛选

GET    /api/v1/assessment-templates/{id}
       模板详情，含完整 workflow_config

PUT    /api/v1/assessment-templates/{id}
       更新模板（仅 DRAFT 状态可编辑）

PUT    /api/v1/assessment-templates/{id}/workflow
       单独更新流程配置

POST   /api/v1/assessment-templates/{id}/publish
       发布模板（状态变为 PUBLISHED）

DELETE /api/v1/assessment-templates/{id}
       删除模板（仅无关联计划时可删）
```

### 5.3 计划管理

```
POST   /api/v1/assessment-plans
       创建考核计划（从模板实例化）
       Body: { templateId, name, description, startTime, endTime }

GET    /api/v1/assessment-plans
       计划列表，支持 type/status/dateRange 筛选

GET    /api/v1/assessment-plans/{id}
       计划详情，含当前阶段、参与者、进度

PUT    /api/v1/assessment-plans/{id}
       更新计划基本信息

POST   /api/v1/assessment-plans/{id}/publish
       发布计划，初始化所有阶段实例

POST   /api/v1/assessment-plans/{id}/cancel
       取消计划

--- 参与者 ---

POST   /api/v1/assessment-plans/{id}/participants
       批量分配参与者
       Body: [{ userId, role }]

GET    /api/v1/assessment-plans/{id}/participants
       参与者列表，按 role 筛选

DELETE /api/v1/assessment-plans/{id}/participants/{userId}
       移除参与者
```

### 5.4 阶段操作（核心 API）

```
GET    /api/v1/assessment-plans/{id}/stages
       获取所有阶段及状态
       Response: [
         { stageCode, stageName, status, sortOrder,
           allowedActions: [{ code, name }],
           startedAt, completedAt, operatorName }
       ]

GET    /api/v1/assessment-plans/{id}/stages/current
       获取当前可操作阶段
       Response: {
         stageCode, stageName,
         allowedActions: [{ code, name, requiredFields }],
         preconditionStatus: { PAPER_PREPARE: "COMPLETED", ROOM_ASSIGN: "IN_PROGRESS" }
       }

POST   /api/v1/assessment-plans/{id}/stages/{stageCode}/actions
       执行阶段动作
       Body: { actionCode, data: { ... } }

GET    /api/v1/assessment-plans/{id}/stages/{stageCode}/logs
       阶段操作日志
```

### 5.5 结果管理

```
POST   /api/v1/assessment-plans/{id}/results
       提交考核结果
       Body: { candidateId, evalType, score, grade, detailData, comment }

GET    /api/v1/assessment-plans/{id}/results
       查询考核结果，支持 candidateId/evalType 筛选

PUT    /api/v1/assessment-plans/{id}/results/{resultId}
       修改考核结果

GET    /api/v1/assessment-plans/{id}/results/summary
       结果汇总统计（平均分、分布、通过率等）
```

### 5.6 我的任务（按角色视角）

```
GET    /api/v1/assessment-plans/my-tasks
       当前用户的待办考核任务
       Response: [
         { planId, planName, type, stageCode, stageName,
           actions: [...], deadline }
       ]
```

---

## 6. 包结构建议

```
com.example.assessment
├── AssessmentApplication.java
├── template/
│   ├── AssessmentTemplate.java          (Entity)
│   ├── AssessmentTemplateRepository.java
│   ├── AssessmentTemplateService.java
│   ├── AssessmentTemplateController.java
│   └── dto/
│       ├── TemplateCreateRequest.java
│       └── TemplateResponse.java
├── plan/
│   ├── AssessmentPlan.java              (Entity)
│   ├── AssessmentPlanRepository.java
│   ├── AssessmentPlanService.java
│   ├── AssessmentPlanController.java
│   └── dto/
├── workflow/
│   ├── WorkflowEngine.java              (核心引擎)
│   ├── WorkflowConfig.java              (JSON 解析模型)
│   ├── StageConfig.java                 (阶段配置模型)
│   ├── ActionDef.java                   (动作定义模型)
│   ├── ActionHandler.java               (动作处理器接口)
│   ├── handlers/
│   │   ├── PublishPlanHandler.java
│   │   ├── SubmitScoreHandler.java
│   │   └── ...
│   ├── WorkflowStageDef.java            (Entity)
│   ├── PlanStageInstance.java           (Entity)
│   ├── StageInstanceRepository.java
│   └── StageActionLog.java              (Entity)
├── participant/
│   ├── PlanParticipant.java
│   ├── PlanParticipantRepository.java
│   └── PlanParticipantService.java
├── result/
│   ├── AssessmentResult.java
│   ├── AssessmentResultRepository.java
│   └── AssessmentResultService.java
├── exam/           (考试排考扩展)
│   ├── ExamSession.java
│   ├── ExamSeat.java
│   └── ExamSessionService.java
├── question/       (技能评估扩展)
│   ├── QuestionBank.java
│   ├── ExamPaper.java
│   └── CandidateAnswer.java
└── common/
    ├── config/
    ├── exception/
    │   ├── ForbiddenException.java
    │   ├── StageNotActionableException.java
    │   └── GlobalExceptionHandler.java
    └── event/
        ├── StageCompletedEvent.java
        └── WorkflowEventListener.java
```

---

## 7. 关键技术决策

### 7.1 为什么用 JSON 配置而非工作流引擎（Activiti/Camunda）？

| 维度 | JSON 配置 | 工作流引擎 |
|------|----------|-----------|
| 学习成本 | 低（纯 JSON） | 高（BPMN 建模 + 引擎 API） |
| 灵活性 | 极高（管理员可随时改） | 中（需要部署流程定义） |
| 运维复杂度 | 低（无额外服务） | 高（引擎配置、数据库42张表） |
| 可视化 | 需自建 | 内置 |
| 适用场景 | 阶段数 < 20，分支少 | 复杂分支、并行、会签 |

本系统阶段数在 10 以内，分支逻辑简单，JSON 配置完全够用。

### 7.2 阶段实例的初始化时机

- **方案 A**：创建计划时一次性初始化所有阶段（PENDING 状态）✅ 推荐
- **方案 B**：每次流转时动态创建下一阶段

选 A，好处：
- 查询"计划进度"时直接查 plan_stage_instance 表即可
- 可以提前知道整个流程有多少阶段
- 修改模板不会影响已创建的计划（阶段定义已快照）

### 7.3 前置条件的存储

不存关系表，直接在 `workflow_config.stages[].precondition_stages` 中用 stage_code 数组表达。
引擎运行时去 `plan_stage_instance` 表查这些 stage_code 是否都已完成。

### 7.4 Action Handler 注册机制

```java
public interface ActionHandler {
    String getActionCode();
    ActionResult execute(Long planId, Long operatorId, Map<String, Object> data);
}

@Component
public class PublishPlanHandler implements ActionHandler {
    @Override
    public String getActionCode() { return "publish"; }

    @Override
    public ActionResult execute(Long planId, Long operatorId, Map<String, Object> data) {
        // 发布逻辑
        return ActionResult.success(...);
    }
}
```

Spring 自动收集所有 `ActionHandler` Bean，按 actionCode 注册到 Map，引擎通过 `handlerRegistry.get(actionCode)` 获取。

---

## 8. 实施建议

### Phase 1：核心引擎（~3天）
- assessment_template / assessment_plan / plan_stage_instance / plan_participant 基础 CRUD
- WorkflowEngine 核心逻辑
- 3 个基础 ActionHandler（publish / complete / skip）

### Phase 2：流程配置化（~2天）
- workflow_config JSON 解析与校验
- 阶段前置条件校验
- 自动流转逻辑
- 操作日志

### Phase 3：角色与权限（~1天）
- 角色校验集成
- "我的任务"聚合查询
- 通知事件

### Phase 4：扩展表（按需，~2-3天/类型）
- EXAM：exam_session / exam_seat
- PERFORMANCE：多维评分模板
- TECHNICAL：question_bank / exam_paper / candidate_answer + 自动评分

---

## 9. 风险与注意事项

| 风险 | 应对 |
|------|------|
| workflow_config JSON 越来越大难维护 | 提供前端可视化流程配置界面；JSON Schema 校验 |
| 历史计划关联的模板被修改 | 阶段定义在创建计划时快照到 plan_stage_instance，不受模板变更影响 |
| 同一用户多角色冲突 | plan_participant 支持同一用户多角色，引擎操作时取"当前阶段所需的角色" |
| 并发操作同一阶段 | 乐观锁（version 字段）或数据库行锁 |
| 流程配置错误导致死锁 | 模板发布前做 DAG 校验（检测循环依赖、孤立阶段） |
| 技能评估自动评分公平性 | 客观题自动评分；主观题标记为需人工复核，两阶段评分（auto → manual） |

---

## 相关文档

- Spring Boot Best Practices: `docs/ai/backend/` 下相关文档
- HTTP 协议面试题型: `docs/ai/backend/2026-05-14-1124-http-protocol-interview-questions.md`
