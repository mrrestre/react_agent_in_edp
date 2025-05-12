"""Models for data preprocessing"""

from typing import Optional
from pydantic import BaseModel


class LabeledQAPair(BaseModel):
    """Pydantic representation of a single question answer pair"""

    id: str
    question: str
    answer: str
    product: Optional[str] = None
    category: Optional[str] = None
    source: Optional[str] = None
    persona: Optional[str] = None
    activity: Optional[str] = None
    country: Optional[str] = None


class LabeledQAPairFacts(LabeledQAPair):
    """Pydantic representation of a single question answer pair with facts"""

    facts: list[str] = []
