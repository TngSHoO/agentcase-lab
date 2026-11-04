from __future__ import annotations

from datetime import datetime, timedelta

from .models import CaseRecord, TraceStep

ROOT_CAUSES = [
    "提示词指令冲突",
    "知识检索错误",
    "工具调用失败",
    "上下文信息丢失",
    "长期记忆污染",
    "权限不足",
    "模型幻觉",
]

SCENARIOS = [
    {
        "name": "信息调研智能体",
        "request": "检索三家国内 AI 办公产品的公开信息，并给出带来源的对比结论。",
        "expected": "引用可核验来源，区分事实和推断，并按功能、价格和适用团队输出对比表。",
    },
    {
        "name": "日程邮件助理",
        "request": "根据团队空闲时间安排评审会议，并起草一封确认邮件，发送前需要我确认。",
        "expected": "读取日历、识别冲突、生成邮件草稿，但不得在未经确认时发送。",
    },
    {
        "name": "电商运营智能体",
        "request": "分析本周退款反馈，找出主要原因，并生成下周的商品页优化建议。",
        "expected": "基于真实反馈统计原因分布，给出有数据依据且可执行的优化建议。",
    },
]

MODELS = ["DeepSeek-V3", "Qwen-Plus", "GPT-4.1-mini", "Claude-Sonnet"]

CAUSE_DETAILS = {
    "提示词指令冲突": {
        "evidence": "系统提示同时要求“直接执行”和“执行前必须确认”，模型选择了风险更高的指令分支。",
        "recommendation": "明确指令优先级，将高风险动作统一置于人工确认之后，并增加冲突检测。",
        "fix": "重写系统提示，加入高风险动作确认门和指令优先级。",
    },
    "知识检索错误": {
        "evidence": "检索结果与问题主题相关，但引用的是过期页面，且未检查发布日期。",
        "recommendation": "增加时效性过滤、来源可信度评分和无可靠证据时的拒答策略。",
        "fix": "加入发布日期过滤与来源可信度阈值，并要求输出引用链接。",
    },
    "工具调用失败": {
        "evidence": "工具返回 429 后，智能体未执行退避重试，直接使用空结果继续生成。",
        "recommendation": "为可重试错误增加指数退避、最大重试次数及降级路径。",
        "fix": "增加 429 退避重试和失败后终止生成的保护逻辑。",
    },
    "上下文信息丢失": {
        "evidence": "进入第三个步骤后，最初的格式与约束要求未出现在有效上下文中。",
        "recommendation": "将关键约束提取为结构化状态，在每个决策节点重新注入。",
        "fix": "把用户约束写入任务状态，并在每个步骤前自动校验。",
    },
    "长期记忆污染": {
        "evidence": "智能体读取了另一位用户留下的历史偏好，并将其错误应用到当前任务。",
        "recommendation": "增加用户级记忆隔离、记忆有效期和写入前确认机制。",
        "fix": "按用户隔离记忆空间，并为低置信度记忆增加确认步骤。",
    },
    "权限不足": {
        "evidence": "日历或订单工具返回 403，但智能体将权限错误解释为“没有数据”。",
        "recommendation": "区分无数据与无权限，向用户展示授权引导并停止后续推断。",
        "fix": "识别 403 权限错误，增加授权引导和安全终止状态。",
    },
    "模型幻觉": {
        "evidence": "最终答案包含运行轨迹中从未出现的数字、来源或产品能力。",
        "recommendation": "在输出前执行事实一致性检查，要求每项关键结论绑定证据。",
        "fix": "增加逐条证据校验，没有来源的事实不得进入最终答案。",
    },
}


def _build_steps(case: CaseRecord, index: int) -> list[TraceStep]:
    failed = case.status == "failed"
    failure_sequence = 3 + (index % 3)
    steps: list[TraceStep] = []
    definitions = [
        ("user", "接收用户任务", {"request": case.user_request}, {"accepted": True}),
        ("plan", "生成执行计划", {"constraints": ["准确", "可追溯", "控制成本"]}, {"plan_steps": 4}),
        ("tool", "调用外部工具", {"tool": "search_or_business_api"}, {"result_count": 6}),
        ("memory", "读取上下文与记忆", {"scope": case.scenario}, {"memory_items": 3}),
        ("llm", "生成并校验答案", {"model": case.model_name}, {"checked": not failed}),
        ("final", "返回最终结果", {"format": "markdown"}, {"answer": case.final_answer}),
    ]
    for sequence, (step_type, name, input_data, output_data) in enumerate(definitions, start=1):
        is_failure = failed and sequence == failure_sequence
        status = "error" if is_failure else "success"
        if is_failure:
            output_data = {
                "error": case.root_cause,
                "detail": case.evidence,
                "continued_despite_error": sequence < 6,
            }
        elif failed and sequence > failure_sequence:
            status = "warning"
            output_data = {**output_data, "upstream_error_unresolved": True}
        steps.append(
            TraceStep(
                id=f"{case.id}-S{sequence}",
                case_id=case.id,
                sequence=sequence,
                step_type=step_type,
                name=name,
                status=status,
                duration_ms=180 + ((index * 71 + sequence * 113) % 1200),
                token_count=0 if step_type == "tool" else 90 + ((index * 31 + sequence * 47) % 420),
                token_cost=round(0.0004 + ((index + sequence) % 9) * 0.00035, 5),
                input_data=input_data,
                output_data=output_data,
            )
        )
    return steps


def build_demo_dataset() -> tuple[list[CaseRecord], list[TraceStep]]:
    cases: list[CaseRecord] = []
    steps: list[TraceStep] = []
    base_time = datetime(2026, 10, 6, 9, 0, 0)

    for index in range(30):
        scenario = SCENARIOS[index % len(SCENARIOS)]
        is_success = index % 4 == 3
        cause = "正常" if is_success else ROOT_CAUSES[index % len(ROOT_CAUSES)]
        details = (
            {
                "evidence": "运行轨迹完整，关键结论均能追溯到工具返回结果。",
                "recommendation": "保持现有策略，并将本次运行加入黄金样本集。",
                "fix": "无需修复，作为基线样本。",
            }
            if is_success
            else CAUSE_DETAILS[cause]
        )
        latency = 2600 + ((index * 937) % 9800)
        tokens = 820 + ((index * 293) % 3600)
        cost = round(0.006 + ((index * 17) % 40) * 0.0017, 4)
        severity = "low" if is_success else ["medium", "high", "critical"][index % 3]
        case = CaseRecord(
            id=f"CASE-{index + 1:03d}",
            title=f"{scenario['name']}：{'正常基线' if is_success else cause}",
            scenario=scenario["name"],
            model_name=MODELS[index % len(MODELS)],
            status="success" if is_success else "failed",
            root_cause=cause,
            severity=severity,
            latency_ms=latency,
            token_count=tokens,
            token_cost=cost,
            created_at=(base_time + timedelta(hours=index * 18)).isoformat(timespec="seconds"),
            user_request=scenario["request"],
            final_answer=(
                "任务已完成，结论、数据与来源均已按要求整理。"
                if is_success
                else f"任务返回了看似完整的结果，但存在“{cause}”，不可直接用于业务决策。"
            ),
            expected_answer=scenario["expected"],
            diagnosis=(
                "未发现影响结果的异常。"
                if is_success
                else f"首次关键失败发生在执行链中段，根因归类为{cause}。"
            ),
            evidence=details["evidence"],
            recommendation=details["recommendation"],
            after_status="success",
            after_latency_ms=max(900, int(latency * (0.76 if not is_success else 0.98))),
            after_token_count=max(300, int(tokens * (0.82 if not is_success else 0.99))),
            after_token_cost=round(cost * (0.8 if not is_success else 0.99), 4),
            fix_summary=details["fix"],
        )
        cases.append(case)
        steps.extend(_build_steps(case, index))

    return cases, steps
