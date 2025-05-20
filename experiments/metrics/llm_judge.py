from enum import StrEnum
from typing import Optional
from langchain_core.prompts import PromptTemplate

from react_agent.src.util.llm_proxy import LLM_PROXY

PROMPT_TEMPLATE = """## Role
You are a helpful and fair evaluator.

## Task
Given a question and a generated answer, determine whether the answer is helpful in answering the question.

## Input
Question: {question}
Generated Answer: {answer}

## Output
Respond with only the value 1 for "Helpful" or the value 0 for "Not Helpful"."""


class TrialOutcome(StrEnum):
    """Enum for trial outcomes."""

    HELPFUL = "Helpful"
    NOT_HELPFUL = "Not Helpful"


class LLMAsJudgeEvaluator:
    """Class to evaluate the helpfulness of a generated answer using an LLM."""

    def __init__(self, model: Optional[str] = None):
        if model is None:
            self.model = LLM_PROXY.get_used_model()
        else:
            self.model = model

        self.prompt_template = PromptTemplate.from_template(PROMPT_TEMPLATE)

    def evaluate(self, question: str, generated_answer: str) -> TrialOutcome:
        """Evaluate the helpfulness of a generated answer using an LLM.
        Args:
            question (str): The question to evaluate.
            generated_answer (str): The generated answer to evaluate.
        Returns:
            str: The evaluation result, either "Helpful" or "Not Helpful".
        """
        # Save the model configured in the LLMProxy
        current_model = LLM_PROXY.get_used_model()
        model_changed = False

        # Set the model in the LLMProxy if differs from the current one
        if self.model != current_model:
            LLM_PROXY.set_new_model(self.model)
            model_changed = True

        # Prepare the prompt
        prompt = self.prompt_template.format(
            question=question,
            answer=generated_answer,
        )

        # Invoke the LLM
        response = LLM_PROXY.invoke(prompt)

        # Reset the model in the LLMProxy if it was changed
        if model_changed:
            LLM_PROXY.set_new_model(current_model)

        # Parse the response
        if response == 1 or response == "1":
            return TrialOutcome.HELPFUL
        elif response == 0 or response == "0":
            return TrialOutcome.NOT_HELPFUL
        else:
            raise ValueError(f"Unexpected response: {response}")
