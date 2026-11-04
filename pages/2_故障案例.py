from __future__ import annotations

import pandas as pd
import streamlit as st

from agentcase.repository import get_cases
from agentcase.ui import configure_page, format_case

configure_page("故障案例")
cases = get_cases()

st.title("故障案例")
st.caption("筛选、浏览并定位需要复盘的 Agent 运行。")

filter_cols = st.columns(3)
with filter_cols[0]:
    status = st.selectbox("运行状态", ["全部", "失败", "成功"])
with filter_cols[1]:
    scenarios = ["全部"] + sorted({case["scenario"] for case in cases})
    scenario = st.selectbox("智能体场景", scenarios)
with filter_cols[2]:
    causes = ["全部"] + sorted({case["root_cause"] for case in cases if case["root_cause"] != "正常"})
    cause = st.selectbox("根因类型", causes)

filtered = cases
if status != "全部":
    filtered = [case for case in filtered if case["status"] == ("failed" if status == "失败" else "success")]
if scenario != "全部":
    filtered = [case for case in filtered if case["scenario"] == scenario]
if cause != "全部":
    filtered = [case for case in filtered if case["root_cause"] == cause]

table = pd.DataFrame(filtered)
if table.empty:
    st.warning("没有符合条件的案例。")
    st.stop()

table["状态"] = table["status"].map({"success": "成功", "failed": "失败"})
table["响应时间"] = table["latency_ms"].map(lambda value: f"{value / 1000:.2f}s")
table["成本"] = table["token_cost"].map(lambda value: f"${value:.4f}")
st.dataframe(
    table[["id", "title", "scenario", "model_name", "状态", "root_cause", "severity", "响应时间", "成本"]],
    use_container_width=True,
    hide_index=True,
    column_config={
        "id": "案例编号",
        "title": "案例名称",
        "scenario": "场景",
        "model_name": "模型",
        "root_cause": "根因",
        "severity": "严重程度",
    },
)

st.markdown("### 案例详情")
selected_id = st.selectbox(
    "选择案例",
    [case["id"] for case in filtered],
    format_func=lambda cid: format_case(next(item for item in filtered if item["id"] == cid)),
)
selected = next(case for case in filtered if case["id"] == selected_id)

left, right = st.columns(2)
with left:
    st.markdown("**用户任务**")
    st.write(selected["user_request"])
    st.markdown("**实际结果**")
    st.write(selected["final_answer"])
with right:
    st.markdown("**预期结果**")
    st.write(selected["expected_answer"])
    st.markdown("**当前判断**")
    st.write(selected["diagnosis"])

if selected["status"] == "failed":
    st.warning(f"关键证据：{selected['evidence']}")
else:
    st.success("该案例可作为正常基线样本。")
