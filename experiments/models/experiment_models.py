"""Models for data preprocessing"""

from typing import Optional
from pydantic import BaseModel

from react_agent.src.agents.models.react_agent_models import ToolCall
from react_agent.src.util.llm_proxy import TokenConsumption


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

    facts: list[str] = []


class ExperimentResult(LabeledQAPairFacts):
    """Pydantic model containing the orignial labeld question, with the generated facts and the calculated scores"""

    fact_score: float = 0.0
    bert_score: float = 0.0
    rouge_score: float = 0.0

    tools_used: list[ToolCall] = []
    excecution_time_seconds: float = 0.0
    model_used: str = ""
    tokens_consumed: TokenConsumption = TokenConsumption()
    llm_call_count: int = 0
