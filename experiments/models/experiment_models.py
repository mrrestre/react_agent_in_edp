"""Models for data preprocessing"""

from enum import StrEnum
from typing import Optional
from pydantic import BaseModel

from experiments.metrics.fact_score.model.fact_score_models import FactClassification
from react_agent.src.agents.models.react_agent_models import ToolCall
from react_agent.src.config.system_parameters import TriageSettings
from react_agent.src.util.llm_proxy import TokenConsumption


class AgentJudgeOutcome(StrEnum):
    """Enum for trial outcomes."""

    FULLY_HELPFUL = "Fully Helpful"
    PARTIALLY_HELPFUL = "Partially Helpful"
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
    agent_judge_outcome: AgentJudgeOutcome = AgentJudgeOutcome.NOT_HELPFUL
    agent_judge_reasoning: str = ""
    agent_judge_model: str = ""
    agent_judge_call_count: int = 0
    agent_judge_tokens_consumed: TokenConsumption = TokenConsumption()

    # Result
    generated_answer: str = ""

    # Experiment setting
    model_used: str = ""

    # Runtime details
    triage_category: TriageSettings.Categories = TriageSettings.Categories.ALL
    tools_used: list[ToolCall] = []
    tool_calls_count: int = 0
    excecution_time_seconds: float = 0.0

    # LLM usage statistics
    tokens_consumed: TokenConsumption = TokenConsumption()
    llm_call_count: int = 0
