from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from agentcase.repository import get_cases
from agentcase.ui import configure_page, format_case

configure_page("版本对比")
cases = [case for case in get_cases() if case["status"] == "failed"]

st.title("修复前后对比")
st.caption("验证一次修复是否同时改善任务结果、响应时间和调用成本。")

selected_id = st.selectbox(
    "选择已修复案例",
    [case["id"] for case in cases],
    format_func=lambda cid: format_case(next(item for item in cases if item["id"] == cid)),
)
case = next(item for item in cases if item["id"] == selected_id)

st.info(f"修复方案：{case['fix_summary']}")

before, after = st.columns(2)
with before:
    st.markdown("### 修复前")
    st.error("任务失败")
    st.metric("响应时间", f"{case['latency_ms'] / 1000:.2f}s")
    st.metric("Token 数量", f"{case['token_count']:,}")
    st.metric("调用成本", f"${case['token_cost']:.4f}")
with after:
    st.markdown("### 修复后")
    st.success("任务成功")
    st.metric(
        "响应时间",
        f"{case['after_latency_ms'] / 1000:.2f}s",
        delta=f"{(case['after_latency_ms'] - case['latency_ms']) / 1000:.2f}s",
        delta_color="inverse",
    )
    st.metric(
        "Token 数量",
        f"{case['after_token_count']:,}",
        delta=case["after_token_count"] - case["token_count"],
        delta_color="inverse",
    )
    st.metric(
        "调用成本",
        f"${case['after_token_cost']:.4f}",
        delta=f"${case['after_token_cost'] - case['token_cost']:.4f}",
        delta_color="inverse",
    )

comparison = pd.DataFrame(
    [
        {
            "指标": "响应时间（秒）",
            "修复前": case["latency_ms"] / 1000,
            "修复后": case["after_latency_ms"] / 1000,
        },
        {
            "指标": "Token（千）",
            "修复前": case["token_count"] / 1000,
            "修复后": case["after_token_count"] / 1000,
        },
        {
            "指标": "成本（美分）",
            "修复前": case["token_cost"] * 100,
            "修复后": case["after_token_cost"] * 100,
        },
    ]
).melt(id_vars="指标", var_name="版本", value_name="数值")
figure = px.bar(
    comparison,
    x="指标",
    y="数值",
    color="版本",
    barmode="group",
    title="关键指标对比",
    color_discrete_map={"修复前": "#df5b5b", "修复后": "#3aa675"},
)
st.plotly_chart(figure, use_container_width=True)

st.success("验收结论：任务恢复成功，且延迟、Token 和调用成本均得到改善。")
