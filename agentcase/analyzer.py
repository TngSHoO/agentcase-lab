from __future__ import annotations

import json
import os
from typing import Any

import requests

from .models import RootCauseReport


def analyze_locally(case: dict[str, Any], steps: list[dict[str, Any]]) -> RootCauseReport:
    failed_step = next((step for step in steps if step["status"] == "error"), None)
    if case["status"] == "success":
        return RootCauseReport(
            root_cause="正常",
            confidence=0.98,
            failed_step="无",
            evidence=["所有步骤均成功完成", "最终答案满足预期要求"],
            impact="未发现影响任务结果的异常。",
            recommendations=["将本次运行加入黄金样本集", "持续监控成本和响应时间"],
        )
    return RootCauseReport(
        root_cause=case["root_cause"],
        confidence=0.86,
        failed_step=failed_step["name"] if failed_step else "最终结果",
        evidence=[case["evidence"], f"运行状态：{case['status']}", f"严重程度：{case['severity']}"],
        impact=f"该问题可能导致“{case['scenario']}”任务产生不可直接使用的结果。",
        recommendations=[case["recommendation"], case["fix_summary"]],
    )


def analyze_with_llm(case: dict[str, Any], steps: list[dict[str, Any]]) -> RootCauseReport:
    api_key = os.getenv("AGENTCASE_API_KEY")
    if not api_key:
        raise RuntimeError("未配置 AGENTCASE_API_KEY，将使用演示分析模式。")
    base_url = os.getenv("AGENTCASE_API_BASE", "https://api.deepseek.com/v1").rstrip("/")
    model = os.getenv("AGENTCASE_MODEL", "deepseek-chat")
    payload = {
        "model": model,
        "temperature": 0.1,
        "response_format": {"type": "json_object"},
        "messages": [
            {
                "role": "system",
                "content": (
                    "你是 AI Agent 质量分析专家。根据案例和轨迹输出 JSON，字段必须包括："
                    "root_cause, confidence, failed_step, evidence(数组), impact, recommendations(数组)。"
                    "不得编造轨迹中不存在的事实。"
                ),
            },
            {
                "role": "user",
                "content": json.dumps({"case": case, "steps": steps}, ensure_ascii=False),
            },
        ],
    }
    response = requests.post(
        f"{base_url}/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json=payload,
        timeout=60,
    )
    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"]
    parsed = json.loads(content)
    parsed["source"] = "llm"
    return RootCauseReport.model_validate(parsed)


def diagnose(case: dict[str, Any], steps: list[dict[str, Any]], use_llm: bool = False) -> RootCauseReport:
    if use_llm:
        return analyze_with_llm(case, steps)
    return analyze_locally(case, steps)
