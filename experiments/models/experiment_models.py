"""Models for data preprocessing"""

from enum import StrEnum
from typing import Optional
from pydantic import BaseModel

from experiments.fact_score.model.fact_score_models import FactClassification
from react_agent.src.agents.models.react_agent_models import ToolCall
from react_agent.src.util.llm_proxy import TokenConsumption


class LLMJudgeOutcome(StrEnum):
    """Enum for trial outcomes."""

    HELPFUL = "Helpful"
    NOT_HELPFUL = "Not Helpful"


class LabeledQAPair(BaseModel):
    """Pydantic representation of a single question answer pair"""

    id: str
    question: str
    answer: str
    product: Optional[str] = None
    category: Optional[str] = None
    persona: Optional[str] = None
    activity: Optional[str] = None
    country: Optional[str] = None


class LabeledQAPairFacts(LabeledQAPair):
    """Pydantic representation of a single question answer pair with facts"""

    facts: list[FactClassification] = []


class ExperimentResult(LabeledQAPairFacts):
    """Pydantic model containing the orignial labeld question, with the generated facts and the calculated scores"""

    # Evaluation scores
    fact_score: float = 0.0
    bert_score: float = 0.0
    llm_judge_outcome: LLMJudgeOutcome = LLMJudgeOutcome.NOT_HELPFUL
    llm_judge_model: str = ""

    # Result
    generated_answer: str = ""

    # Experiment setting
    model_used: str = ""

    # Runtime details
    tools_used: list[ToolCall] = []
    tool_calls_count: int = 0
    excecution_time_seconds: float = 0.0

    # LLM usage statistics
    tokens_consumed: TokenConsumption = TokenConsumption()
    llm_call_count: int = 0
