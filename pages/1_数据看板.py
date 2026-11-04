from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from agentcase.metrics import cause_distribution, model_performance, overview_metrics
from agentcase.repository import get_cases
from agentcase.ui import configure_page

configure_page("数据看板")
cases = get_cases()
metrics = overview_metrics(cases)

st.title("数据看板")
st.caption("观察 Agent 的任务质量、成本、延迟和故障结构。")

cols = st.columns(5)
cols[0].metric("任务总数", int(metrics["total"]))
cols[1].metric("任务成功率", f"{metrics['success_rate']:.1%}")
cols[2].metric("平均响应时间", f"{metrics['avg_latency_ms'] / 1000:.1f}s")
cols[3].metric("平均调用成本", f"¥{metrics['avg_cost'] * 7.2:.3f}")
cols[4].metric("失败案例修复率", f"{metrics['repair_rate']:.1%}")

left, right = st.columns(2)
with left:
    cause_df = pd.DataFrame(cause_distribution(cases))
    figure = px.bar(
        cause_df,
        x="案例数",
        y="根因",
        orientation="h",
        title="失败根因分布",
        color="案例数",
        color_continuous_scale="Blues",
    )
    figure.update_layout(coloraxis_showscale=False, yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(figure, use_container_width=True)

with right:
    status_df = pd.DataFrame(cases)
    status_df["状态"] = status_df["status"].map({"success": "成功", "failed": "失败"})
    scenario_status = status_df.groupby(["scenario", "状态"]).size().reset_index(name="案例数")
    figure = px.bar(
        scenario_status,
        x="scenario",
        y="案例数",
        color="状态",
        barmode="stack",
        title="不同场景的成功与失败",
        labels={"scenario": "智能体场景"},
        color_discrete_map={"成功": "#3aa675", "失败": "#df5b5b"},
    )
    st.plotly_chart(figure, use_container_width=True)

st.markdown("### 模型表现")
model_df = pd.DataFrame(model_performance(cases))
display_df = model_df.copy()
display_df["成功率"] = display_df["成功率"].map(lambda value: f"{value:.1%}")
display_df["平均耗时秒"] = display_df["平均耗时秒"].map(lambda value: f"{value:.2f}")
display_df["平均成本"] = display_df["平均成本"].map(lambda value: f"${value:.4f}")
st.dataframe(display_df, use_container_width=True, hide_index=True)

st.info("演示数据用于展示产品流程，不代表模型的真实公开排名。")
