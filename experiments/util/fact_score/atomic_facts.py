"""Creation of atomic facts from a given text using LLM."""

import json

from experiments.util.fact_score.settings import FactScoreSettings
from react_agent.src.util.llm_proxy import LLM_PROXY

FACT_GENERATOR_SETTINGS = FactScoreSettings()


class AtomicFactGenerator:
    """Class to generate atomic facts from a given text using LLM."""

    def __init__(self) -> None:
        # Examples (demonstrations) that is used in prompt generation
        self.demons: list[dict[str, list[str]]] = self.load_demons()

    def load_demons(self) -> list[dict[str, list[str]]]:
        """
        Load examples (demonstrations) from a JSON file.
        This will be used in the prompt generation.

        Returns:
            list: A list of examples (demonstrations).
        """
        with open(
            FACT_GENERATOR_SETTINGS.path_to_example_demons, encoding="utf-8"
        ) as file:
            demons: list[dict[str, list[str]]] = json.load(file)

        return demons

    async def get_atomic_facts(self, text: str) -> list[str]:
        """
        Generate atomic facts from the given text using LLM.
        The text is passed to the LLM, and the output is parsed to extract atomic facts.
        The output is cleaned and returned as a list of sentences.
        The prompt is generated using the examples (demonstrations) loaded from the JSON file.
        """
        atoms = None

        examples = "\n".join(
            f"Text:\n{demon['Sentence']}\nIndependent Facts:\n{"\n-".join(demon["Independent Facts"])}"
            for demon in self.demons
        )

        prompt = FACT_GENERATOR_SETTINGS.fact_gen_prompt.format(
            n=FACT_GENERATOR_SETTINGS.number_of_facts,
            examples=examples,
            text=text,
        )

        output: str | None = LLM_PROXY.invoke(prompt)
        atoms = self.llm_output_to_sentences(str(output))

        return atoms

    def llm_output_to_sentences(self, text: str) -> list[str]:
        """
        Clears the output from LLM and returns a list of cleaned sentences.

        Args:
            text (str): The output from LLM.

        Returns:
            list: A list of cleaned sentences.
        """
        sentences = text.split("- ")[1:]
        sentences = [
            sent.strip()[:-1] if sent.strip()[-1] == "\n" else sent.strip()
            for sent in sentences
        ]

        sentences = [sent + "." if sent[-1] != "." else sent for sent in sentences]

        return sentences
