"""Settings for the FactScore module."""

from pydantic_settings import BaseSettings


class FactScoreSettings(BaseSettings):
    """Settings for the FactScore module."""

    number_of_facts: int = 10
    path_to_example_demons: str = "/ressources/atomic_facts_demons.json"
    path_to_scoring_demons: str = "/ressources/fact_scorer_demons.json"

    fact_gen_prompt: str = """You are an atomic fact extraction assistant.
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
    fact_acoring_prompt: str = """## Role
You are a fact-checking assistant. Your task is to verify whether a fact is supported by a given context text.

## Instruction
- Evaluate whether the meaning of the fact is directly supported by the information in the text, even if the wording differs.
- Only mark a fact as true if it can be explicitly confirmed from the context without assumptions or external knowledge.
- If the fact is not stated, contradicted, or cannot be clearly inferred from the text, mark it as false.
- Be strict: if there is doubt or missing information, label the fact as false.
- Focus only on the text provided; do not use prior knowledge.
- The response should be in JSON format, without any additional characters or explanations.

## Examples
{examples}

## Task
Evaluate if a given atomic fact is contained in the context text. Answer acording to the schema of the examples given.
Fact: {fact}
Context: {context}

## Output format
{{
    "fact": "<original fact without modification>",
    "is_contained": "<true or false>",
    "reason": "<reasoning for the classification>"
}}
"""
