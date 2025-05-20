"""Model to be used in the fact score"""

from enum import StrEnum
from typing import Optional
from pydantic import BaseModel, Field


class FactCategory(StrEnum):
    """Possible values for the classification of a fact"""

    DIRECT: str = "direct"
    SUPPORTING: str = "supporting"


class FactClassification(BaseModel):
    """A pair of a fact and a given category"""

    fact: str = Field(None, title="Fact", description="Atomic fact")
    classification: FactCategory = Field(
        None,
        title="Fact Classification",
        description="The classification of the fact according to the question",
    )
    id: Optional[str] = "-1"


class FactGeneratorExample(BaseModel):
    """The structure of an example data set"""

    question: str
    answer: str
    classified_facts: list[FactClassification]


class FactEvaluation(BaseModel):
    """Model to represent the if a fact is contained in a knowledge source."""

    fact: str
    is_contained: bool
    reason: str


class FactEvaluationExample(FactEvaluation):
    """Model representing an LLM example for evaluating a fact within a knowledge source"""

    knowledge_source: str


class FactScoreResult(BaseModel):
    """Model representing the values of the fact score"""

    direct_fact_score: float = 0.0
    supporting_fact_score: float = 0.0
    combined_fact_score: float = 0.0

    direct_facts: list[FactEvaluation] = []
    supporting_facts: list[FactEvaluation] = []
