"""HTTP 契约模型。"""

from __future__ import annotations

from pydantic import BaseModel, Field


class ClarificationTurn(BaseModel):
    """对话契约：保存一次系统追问和用户回答，供下一轮完整理解。"""

    question: str = Field(min_length=1, max_length=500)
    answer: str = Field(min_length=1, max_length=500)


class QueryRequest(BaseModel):
    """接口模型：接收原问题、500 行预览上限和完整澄清历史。"""

    question: str = Field(min_length=2, max_length=500)
    limit: int = Field(default=500, ge=1, le=500)
    confirmed_view: str | None = Field(default=None, max_length=100)
    clarification_answer: str | None = Field(default=None, max_length=500)
    clarification_history: list[ClarificationTurn] = Field(
        default_factory=list,
        max_length=10,
    )


class DashboardQueryRequest(BaseModel):
    """Dashboard 接口模型：接收概况问题和可选的多轮补充，使用独立查询上限。"""

    question: str = Field(min_length=2, max_length=500)
    limit: int = Field(default=100, ge=1, le=500)
    confirmed_view: str | None = Field(default=None, max_length=100)
    clarification_answer: str | None = Field(default=None, max_length=500)
    clarification_history: list[ClarificationTurn] = Field(
        default_factory=list,
        max_length=10,
    )
