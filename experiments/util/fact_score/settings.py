"""Settings for the FactScore module."""

from pydantic_settings import BaseSettings


class FactScoreSettings(BaseSettings):
    """Settings for the FactScore module."""

    number_of_facts: int = 10
    path_to_example_demons: str = "./resources/atomic_facts_classified.json"
    path_to_scoring_demons: str = "/resources/fact_scorer_demons.json"

    fact_gen_prompt: str = """##Role
You are an assistant for extracting and classifying atomic facts from a given answer in the context of a specific question.

## Task
Given a question and an answer, extract at most {n} **atomic facts** from the answer. For each fact, classify it as either:

- "direct": if it explicitly answers the question or forms a necessary part of the direct answer.
- "supporting": if it does not answer the question directly, but provides helpful context, justification, or explanation related to the answer.

## Rules
- Only extract facts that are relevant to the question.
- Do not include opinions, assumptions, or irrelevant information.
- Each fact must be concise and independently meaningful.
- Do not fabricate or infer facts not found in the answer.
- If there are fewer than {n} relevant facts, extract only the meaningful ones.

## Output Format
Return a JSON array. Each element must have:
{response_schema}

## Example
{examples}

---

## Following the examples do that for this:
Question:
{question}

Answer:
{answer}
"""

    fact_scoring_prompt: str = """## Role
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
