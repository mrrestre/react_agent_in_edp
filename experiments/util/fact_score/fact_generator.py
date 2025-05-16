"""Creation of atomic facts from a given text using LLM."""

import json

from experiments.util.fact_score.model.fact_score_models import (
    FactClassification,
    FactGeneratorExample,
)
from experiments.util.fact_score.settings import FactScoreSettings
from experiments.util.fact_score.util import Util
from react_agent.src.util.llm_proxy import LLM_PROXY

FACT_GENERATOR_SETTINGS = FactScoreSettings()


class AtomicFactGenerator:
    """Class to generate atomic facts from a given text using LLM."""

    def __init__(self) -> None:
        # Examples (demonstrations) that is used in prompt generation
        self.example_data_set: list[FactGeneratorExample] = self.load_examples()

    def load_examples(self) -> list[FactGeneratorExample]:
        """
        Load examples (demonstrations) from a JSON file.
        This will be used in the prompt generation.

        Returns:
            list: A list of examples (demonstrations).
        """
        with open(
            FACT_GENERATOR_SETTINGS.path_to_example_demons, encoding="utf-8"
        ) as file:
            json_data = json.load(file)
            example_data_set = [FactGeneratorExample(**item) for item in json_data]

        return example_data_set

    async def get_atomic_facts(
        self, question: str, answer: str, question_id: str
    ) -> list[FactClassification]:
        """
        Generate atomic facts from the given text using LLM.
        The text is passed to the LLM, and the output is parsed to extract atomic facts.
        The output is cleaned and returned as a list of sentences.
        The prompt is generated using the examples (demonstrations) loaded from the JSON file.
        """
        classified_facts = None

        examples = "\n".join(
            f"{example.model_dump()}" for example in self.example_data_set
        )

        prompt = FACT_GENERATOR_SETTINGS.fact_gen_prompt.format(
            n=FACT_GENERATOR_SETTINGS.number_of_facts,
            response_schema=FactClassification.model_json_schema(),
            examples=examples,
            question=question,
            answer=answer,
        )

        output: str = LLM_PROXY.invoke(prompt)
        cleansed_output = Util.remove_json_code_block_markers(output)

        try:
            json_output = json.loads(cleansed_output)
            classified_facts = [FactClassification(**item) for item in json_output]
        except Exception as exc:
            raise RuntimeError("Error while parsing the response of the LLM") from exc

        id_helper = 1
        for fact in classified_facts:
            fact.id = f"{question_id}-{id_helper}"
            id_helper += 1

        return classified_facts
