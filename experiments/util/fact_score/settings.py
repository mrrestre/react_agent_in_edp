"""Settings for the FactScore module."""

from pydantic_settings import BaseSettings


class FactScoreSettings(BaseSettings):
    """Settings for the FactScore module."""

    number_of_facts: int = 10
    path_to_example_demos: str = "./ressources/atomic_facts_demons.json"

    sys_prompt: str = """You are an atomic fact extraction assistant.
Given the following text, extract at most {n} of the most important and relevant atomic facts.

## Instructions
- An atomic fact is a concise, standalone piece of information that can be independently understood.
- Focus on atomic facts that are central to the topic or critical for understanding the overall content.
- Ignore minor details, opinions, or unverified claims unless they are core to the topic.
- If fewer than {n} important facts exist, list only those that meet the criteria.

## Examples
{examples}

## Task
Extract at most {n} atomic facts from the following text as a list of bullet points:
{text}
"""
