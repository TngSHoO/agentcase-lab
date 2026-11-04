from __future__ import annotations

import json
from typing import Any

import streamlit as st

STATUS_LABELS = {"success": "成功", "failed": "失败", "warning": "警告", "error": "错误"}
STATUS_ICONS = {"success": "✅", "failed": "❌", "warning": "⚠️", "error": "❌"}


def configure_page(title: str) -> None:
    st.set_page_config(
        page_title=f"{title} | AgentCase Lab",
        page_icon=":material/schema:",
        layout="wide",
    )
    st.markdown(
        """
        <style>
        .block-container {padding-top: 2rem; padding-bottom: 3rem;}
        [data-testid="stMetric"] {
            background: #f7f8fc;
            border: 1px solid #e7e9f2;
            padding: 16px;
            border-radius: 12px;
        }
        .case-note {
            background:#f6f8ff;
            border-left:4px solid #5567d8;
            padding:12px 16px;
            border-radius:8px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def format_case(case: dict[str, Any]) -> str:
    icon = "✅" if case["status"] == "success" else "❌"
    return f"{icon} {case['id']} · {case['title']}"


def render_trace(steps: list[dict[str, Any]]) -> None:
    for step in steps:
        icon = STATUS_ICONS.get(step["status"], "•")
        label = (
            f"{icon} {step['sequence']}. {step['name']} · "
            f"{step['duration_ms']} ms · {step['token_count']} tokens"
        )
        with st.expander(
            label,
            expanded=step["status"] in {"error", "warning"},
        ):
            left, right = st.columns(2)
            with left:
                st.caption("输入")
                st.code(json.dumps(step["input_data"], ensure_ascii=False, indent=2), language="json")
            with right:
                st.caption("输出")
                st.code(json.dumps(step["output_data"], ensure_ascii=False, indent=2), language="json")
