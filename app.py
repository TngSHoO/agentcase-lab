from __future__ import annotations

import streamlit as st

from agentcase.metrics import overview_metrics
from agentcase.repository import ensure_database, get_cases
from agentcase.ui import configure_page

configure_page("首页")
database_path = ensure_database()
cases = get_cases()
metrics = overview_metrics(cases)

st.title("AgentCase Lab")
st.subheader("AI 智能体故障复盘与根因分析平台")
st.markdown(
    """
    <div class="case-note">
    把一次失败的 Agent 运行拆成可回放的执行轨迹，定位提示词、检索、工具、记忆、权限或模型环节的问题，
    并比较修复前后的成功率、延迟与成本。
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")
columns = st.columns(4)
columns[0].metric("演示案例", int(metrics["total"]))
columns[1].metric("当前成功率", f"{metrics['success_rate']:.0%}")
columns[2].metric("平均响应时间", f"{metrics['avg_latency_ms'] / 1000:.1f} 秒")
columns[3].metric("失败案例修复率", f"{metrics['repair_rate']:.0%}")

st.divider()
left, right = st.columns([1.2, 1])
with left:
    st.markdown("### 推荐演示路径")
    st.markdown(
        """
        1. 在 **数据看板** 查看整体质量与根因分布。
        2. 在 **故障案例** 筛选一个失败案例。
        3. 在 **轨迹回放** 找到首次异常步骤。
        4. 在 **根因分析** 查看判断依据和修改建议。
        5. 在 **版本对比** 验证修复是否改善成功率、延迟和成本。
        """
    )
with right:
    st.markdown("### 当前版本")
    st.success("演示模式可直接使用，无需 API Key")
    st.info("配置模型接口后，可在根因分析页启用实时 AI 分析。")
    st.caption(f"本地数据库：{database_path}")

st.divider()
st.markdown("### 产品边界")
st.write("第一版聚焦于故障复盘和方案验证，不负责构建 Agent、不直接修改线上提示词，也不自动执行高风险修复。")
