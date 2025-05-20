"""Class to score facts based on a knowledge source."""

import json
import os
from typing import Optional

from experiments.fact_score.model.fact_score_models import (
    FactCategory,
    FactClassification,
    FactEvaluation,
    FactEvaluationExample,
    FactScoreResult,
)
from experiments.fact_score.settings import FactScoreSettings
from experiments.fact_score.util import Util
from react_agent.src.util.llm_proxy import LLM_PROXY

FACT_SCORE_SETTINGS = FactScoreSettings()


class FactScorer:
    """Class to score facts based on a knowledge source."""

    def __init__(self) -> None:
        # Examples (demonstrations) that is used in prompt generation
        self.examples: list[FactEvaluationExample] = self.load_examples()

    def load_examples(self) -> list[FactEvaluationExample]:
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
            json_data = json.load(file)
            example_data_set = [FactEvaluationExample(**item) for item in json_data]

        return example_data_set

    def prepare_prompt(self, fact: str, knowlede_source: str) -> str:
        """
        Prepare the prompt for the LLM using the fact and knowledge source.

        Args:
            fact (str): The atomic fact to be scored.
            knowlede_source (str): The knowledge source to be used for scoring.

        Returns:
            str: The prepared prompt.
        """
        examples = "\n".join(f"{example.model_dump()}" for example in self.examples)

        prompt = FACT_SCORE_SETTINGS.fact_scoring_prompt.format(
            examples=examples,
            fact=fact,
            context=knowlede_source,
        )

        return prompt

    async def evaluate_facts_in_context(
        self, facts: list[FactClassification], knowledge_source: str
    ) -> dict[FactEvaluation]:
        """
        Calculates the score of each atomic fact based on the knowledge source.
        The score is calculated by the amount of facts supported by amount of total facts.

        Args:
            facts (list[FactClassification]): The list of atomic facts to be scored.
            knowledge_source (str): The knowledge source to be used for scoring.

        Returns:
            dict[FactEvaluation]: A dictionary containing the evaluation of each fact.
        """

        decisions: dict[FactEvaluation] = {}

        for fact in facts:
            # Prompt that will be sent to GPT
            prompt = self.prepare_prompt(
                fact=fact.fact, knowlede_source=knowledge_source
            )

            output: str = LLM_PROXY.invoke(prompt)
            cleansed_output = Util.remove_json_code_block_markers(output)

            # Parse the output
            try:
                json_output = json.loads(cleansed_output)
                evaluation = FactEvaluation(**json_output)
            except Exception as exc:
                raise RuntimeError(
                    "Error while parsing the response of the LLM"
                ) from exc

            decisions[fact.id] = evaluation

        return decisions

    async def get_fact_score(
        self,
        facts: list[FactClassification],
        knowledge_source: str,
        debug: Optional[bool] = False,
    ) -> FactScoreResult:
        """
        Calculates the score of each atomic fact based on the knowledge source.
        The score is calculated by the amount of facts supported by amount of total facts.
        The score is between 0 and 1, where 1 means all facts are supported by the knowledge source.
        The debug flag is used to print the details of the classification.

        Args:
            facts (list[FactClassification]): The list of atomic facts to be scored.
            knowledge_source (str): The knowledge source to be used for scoring.
            debug (bool, optional): If True, print the details of the classification. Defaults to False.
        Returns:
            FactScoreResult: The result of the scoring process, including the score and the details of the classification.
        """
        result: FactScoreResult = FactScoreResult()
        decisions = await self.evaluate_facts_in_context(facts, knowledge_source)

        for fact in facts:
            if fact.classification == FactCategory.DIRECT:
                result.direct_facts.append(decisions.get(fact.id))
            elif fact.classification == FactCategory.SUPPORTING:
                result.supporting_facts.append(decisions.get(fact.id))

        if debug:
            for direct_fact in result.direct_facts:
                print(f"Direct Fact: {direct_fact.fact}")
                print(f"Is contained: {direct_fact.is_contained}")
                print(f"Reason: {direct_fact.reason}\n")
            for supporting_fact in result.supporting_facts:
                print(f"Supporting Fact: {supporting_fact.fact}")
                print(f"Is contained: {supporting_fact.is_contained}")
                print(f"Reason: {supporting_fact.reason}\n")

        result.direct_fact_score = self._calculate_score(result.direct_facts)
        result.supporting_fact_score = self._calculate_score(result.supporting_facts)
        result.combined_fact_score = self._calculate_score(
            result.direct_facts + result.supporting_facts
        )

        return result

    def _calculate_score(self, decision_list: list[FactEvaluation]) -> float:
        """Calculates the amount of facts contained in the knowledge source divided by the amount of facts"""
        if len(decision_list) == 0:
            return 0.0
        else:
            return sum(1 for decision in decision_list if decision.is_contained) / len(
                decision_list
            )
