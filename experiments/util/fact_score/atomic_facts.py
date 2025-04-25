import json
import re

from experiments.util.fact_score.settings import FactScoreSettings
from react_agent.src.util.llm_proxy import LLM_PROXY

FACT_GENERATOR_SETTINGS = FactScoreSettings()


class AtomicFactGenerator:
    def __init__(self) -> None:
        # Examples (demonstrations) that is used in prompt generation
        self.demons: list[dict[str, list[str]]] = self.load_demons()

    async def run(self, text: str) -> list[str]:
        """
        Extracts atomic facts from a text.

        Args:
            text (str): The text to extract atomic facts from.

        Returns:
            list: A list of atomic facts and the associatated sentence extracted from the text.
        """
        paragraphs = re.split(r"(?<=\d\.)\s+", text)

        atoms = []
        for sent in paragraphs:
            atom = await self.get_sentence_af(sent)
            atoms.extend(atom)

        return atoms

    def load_demons(self) -> list[dict[str, list[str]]]:
        """
        Load examples (demonstrations) from a JSON file.
        This will be used in the prompt generation.

        Returns:
            list: A list of examples (demonstrations).
        """
        with open(FACT_GENERATOR_SETTINGS.path_to_example_demos) as file:
            demons: list[dict[str, list[str]]] = json.load(file)

        return demons

    def get_instructions(self) -> str:
        """
        Prepare instructions for the prompt generation.
        Instructions include the examples given in the atomic_facts_demons.json file.

        Returns:
            str: The instructions for the prompt generation.
        """

        instructions = (
            "Please breakdown the following sentence into independent facts:\n\n"
        )

        for demon in self.demons:
            sentence = demon["Sentence"]
            facts = demon["Independent Facts"]

            instructions += f"Sentence:\n{sentence}\n"

            instructions += "Independent Facts:\n"

            for fact in facts:
                instructions += f"- {fact}\n"

            instructions += "\n\n"

        return instructions

    async def get_sentence_af(self, sentence: str) -> list[str]:
        """
        Gets atomic facts for a sentence using the LLM Proxy.

        Args:
            sentence (str): The sentence to extract atomic facts from.

        Returns:
            list: A list of atomic facts extracted from the sentence.
        """
        atoms = None
        instructions = self.get_instructions()

        prompt = instructions + f"Sentence:\n{sentence}\nIndependent Facts:"

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
