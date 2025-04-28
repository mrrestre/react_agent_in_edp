import json
import re

from experiments.util.fact_score.settings import FactScoreSettings
from react_agent.src.util.llm_proxy import LLM_PROXY

FACT_GENERATOR_SETTINGS = FactScoreSettings()


class AtomicFactGenerator:
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
            FACT_GENERATOR_SETTINGS.path_to_example_demos, encoding="utf-8"
        ) as file:
            demons: list[dict[str, list[str]]] = json.load(file)

        return demons

    async def get_atomic_facts(self, text: str) -> list[str]:
        atoms = None

        examples = "\n".join(
            f"Text:\n{demon['Sentence']}\nIndependent Facts:\n{"\n-".join(demon["Independent Facts"])}"
            for demon in self.demons
        )

        prompt = FACT_GENERATOR_SETTINGS.sys_prompt.format(
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
