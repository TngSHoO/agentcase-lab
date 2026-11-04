from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

CaseStatus = Literal["success", "failed"]
StepStatus = Literal["success", "warning", "error"]


class CaseRecord(BaseModel):
    id: str
    title: str
    scenario: str
    model_name: str
    status: CaseStatus
    root_cause: str
    severity: Literal["low", "medium", "high", "critical"]
    latency_ms: int = Field(ge=0)
    token_count: int = Field(ge=0)
    token_cost: float = Field(ge=0)
    created_at: str
    user_request: str
    final_answer: str
    expected_answer: str
    diagnosis: str
    evidence: str
    recommendation: str
    after_status: CaseStatus
    after_latency_ms: int = Field(ge=0)
    after_token_count: int = Field(ge=0)
    after_token_cost: float = Field(ge=0)
    fix_summary: str


class TraceStep(BaseModel):
    id: str
    case_id: str
    sequence: int = Field(ge=1)
    step_type: str
    name: str
    status: StepStatus
    duration_ms: int = Field(ge=0)
    token_count: int = Field(ge=0)
    token_cost: float = Field(ge=0)
    input_data: dict[str, Any]
    output_data: dict[str, Any]


class RootCauseReport(BaseModel):
    root_cause: str
    confidence: float = Field(ge=0, le=1)
    failed_step: str
    evidence: list[str]
    impact: str
    recommendations: list[str]
    source: Literal["demo", "llm"] = "demo"
