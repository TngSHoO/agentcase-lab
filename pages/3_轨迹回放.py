from __future__ import annotations

import streamlit as st

from agentcase.repository import get_cases, get_steps
from agentcase.ui import configure_page, format_case, render_trace

configure_page("轨迹回放")
cases = get_cases()

st.title("轨迹回放")
st.caption("沿执行时间线检查模型、工具、上下文和最终输出。")

failed_first = sorted(cases, key=lambda case: case["status"] == "success")
selected_id = st.selectbox(
    "选择运行案例",
    [case["id"] for case in failed_first],
    format_func=lambda cid: format_case(next(item for item in failed_first if item["id"] == cid)),
)
case = next(item for item in failed_first if item["id"] == selected_id)
steps = get_steps(selected_id)

columns = st.columns(4)
columns[0].metric("运行状态", "成功" if case["status"] == "success" else "失败")
columns[1].metric("总耗时", f"{case['latency_ms'] / 1000:.2f}s")
columns[2].metric("Token", f"{case['token_count']:,}")
columns[3].metric("成本", f"${case['token_cost']:.4f}")

if case["status"] == "failed":
    st.error(f"已定位根因：{case['root_cause']} · 严重程度：{case['severity']}")
else:
    st.success("本次运行未发现影响最终结果的故障。")

st.markdown("### 执行时间线")
render_trace(steps)
