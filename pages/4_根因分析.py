from __future__ import annotations

import os

import streamlit as st
from dotenv import load_dotenv

from agentcase.analyzer import diagnose
from agentcase.repository import get_cases, get_steps
from agentcase.ui import configure_page, format_case

load_dotenv()
configure_page("根因分析")
cases = get_cases()

st.title("根因分析")
st.caption("基于运行轨迹生成结构化诊断报告。")

failed_cases = [case for case in cases if case["status"] == "failed"]
selected_id = st.selectbox(
    "选择失败案例",
    [case["id"] for case in failed_cases],
    format_func=lambda cid: format_case(next(item for item in failed_cases if item["id"] == cid)),
)
case = next(item for item in failed_cases if item["id"] == selected_id)
steps = get_steps(selected_id)

has_key = bool(os.getenv("AGENTCASE_API_KEY"))
use_llm = st.toggle("使用实时大模型分析", value=False, disabled=not has_key)
if not has_key:
    st.caption("当前为演示分析模式。如需实时分析，请在 .env 中配置 AGENTCASE_API_KEY。")

if st.button("生成根因报告", type="primary", use_container_width=True):
    try:
        with st.spinner("正在分析运行轨迹……"):
            report = diagnose(case, steps, use_llm=use_llm)
        st.session_state["root_report"] = report.model_dump()
    except Exception as exc:
        st.error(f"实时分析失败：{exc}")
        st.info("你可以关闭实时大模型分析，继续使用演示模式。")

report = st.session_state.get("root_report")
if report:
    left, right, third = st.columns(3)
    left.metric("根因分类", report["root_cause"])
    right.metric("置信度", f"{report['confidence']:.0%}")
    third.metric("首次失败步骤", report["failed_step"])

    st.markdown("### 判断依据")
    for evidence in report["evidence"]:
        st.markdown(f"- {evidence}")

    st.markdown("### 影响评估")
    st.warning(report["impact"])

    st.markdown("### 修改建议")
    for index, recommendation in enumerate(report["recommendations"], start=1):
        st.markdown(f"{index}. {recommendation}")

    st.caption(f"报告来源：{'实时大模型' if report['source'] == 'llm' else '演示规则引擎'}")
else:
    st.info("选择案例并点击“生成根因报告”。")
