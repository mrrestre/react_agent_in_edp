"""Class to score facts based on a knowledge source."""

import json
import os

from experiments.util.fact_score.settings import FactScoreSettings
from react_agent.src.util.llm_proxy import LLM_PROXY

FACT_SCORE_SETTINGS = FactScoreSettings()


class FactClassification:
    """Class to represent the classification of a fact."""

    fact: str
    is_contained: bool
    reason: str

    def __init__(self, fact: str, is_contained: bool, reason: str) -> None:
        self.fact = fact
        self.is_contained = is_contained
        self.reason = reason


class FactScorer:
    """Class to score facts based on a knowledge source."""

    def __init__(self) -> None:
        # Examples (demonstrations) that is used in prompt generation
        self.example_demons: list[dict[str, str]] = self.load_demons()

    def load_demons(self) -> list[dict[str, str]]:
        """
        Load examples (demonstrations) from a JSON file.
        This will be used in the prompt generation.

        Returns:
            list: A list of examples (demonstrations).
        """
        file_path = os.path.abspath(
            os.path.dirname(__file__) + FACT_SCORE_SETTINGS.path_to_scoring_demons
        )

        with open(file_path, encoding="utf-8") as file:
            demons: list[dict[str, str]] = json.load(file)
        return demons

    def prepare_prompt(self, fact: str, knowlede_source: str) -> str:
        """
        Prepare the prompt for the LLM using the fact and knowledge source.

        Args:
            fact (str): The atomic fact to be scored.
            knowlede_source (str): The knowledge source to be used for scoring.

        Returns:
            str: The prepared prompt.
        """
        examples = "\n".join(
            json.dumps(example, indent=4) for example in self.example_demons
        )

        prompt = FACT_SCORE_SETTINGS.fact_acoring_prompt.format(
            examples=examples,
            fact=fact,
            context=knowlede_source,
        )

        return prompt

    async def classify_facts_in_context(
        self, facts: list[str], knowledge_source: str
    ) -> list[FactClassification]:
        """
        Calculates the score of each atomic fact based on the knowledge source.
        The score is calculated by the amount of facts supported by amount of total facts.

        Args:
            facts (list): A list of atomic  to be scored.
            knowledge_source (str): The knowledge source to be used for scoring.

        Returns:
            list: A list of dictionaries containing the atomic fact and its score.
        """

        decisions: list[FactClassification] = []

        for atom in facts:
            stripped_atom = atom.strip()

            # Prompt that will be sent to GPT
            prompt = self.prepare_prompt(
                fact=stripped_atom, knowlede_source=knowledge_source
            )

            output: str = LLM_PROXY.invoke(prompt)

            # Parse the output
            try:
                json_output = json.loads(output)
            except json.JSONDecodeError:
                # Trim leading ```json and trailing ``` from the output
                output = output.strip().lstrip("```json").rstrip("```")
                try:
                    json_output = json.loads(output)
                except json.JSONDecodeError:
                    # If it still fails, log the error and continue
                    print(f"Failed to parse JSON: {output}")
                    continue

            classification = FactClassification(**json_output)

            decisions.append(classification)

        return decisions

    async def get_fact_score(self, facts: list[str], knowledge_source: str) -> float:
        """
        Calculates the score of each atomic fact based on the knowledge source.
        The score is calculated by the amount of facts supported by amount of total facts.

        Args:
            facts (list): A list of atomic  to be scored.
            knowledge_source (str): The knowledge source to be used for scoring.

        Returns:
            float: The score of the atomic facts.
        """
        decisions = await self.classify_facts_in_context(facts, knowledge_source)
        score = sum(1 for decision in decisions if decision.is_contained) / len(
            decisions
        )

        return score
