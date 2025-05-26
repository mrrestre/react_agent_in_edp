"""Evaluate the helpfulness of a generated answer using an LLM."""

from typing import Optional
from langchain_core.prompts import PromptTemplate

from experiments.models.experiment_models import LLMJudgeOutcome
from react_agent.src.util.llm_proxy import LLM_PROXY, TokenConsumption

PROMPT_TEMPLATE = """## Role
You are a strict and fair evaluator of answer quality. Your job is to assess whether a generated answer adequately addresses a given question. Be conservative in your judgments — an answer must be clearly complete and correct to be rated as fully helpful.

## Task
Given a question and a generated answer, classify the answer into one of three categories:

- 2 = Fully Helpful: The answer directly, accurately, and completely addresses the question. No major information is missing.
- 1 = Partially Helpful: The answer is somewhat relevant and may include some correct information, but is incomplete, vague, or partially incorrect.
- 0 = Not Helpful: The answer is irrelevant, incorrect, off-topic, or otherwise fails to help the user meaningfully.

You must focus on the **quality of the response relative to the question** — not on how plausible it sounds.

## Input
Question: {question}
Generated Answer: {answer}

## Examples

Example 1  
Question: What is the capital of France?  
Answer: The capital of France is Paris.  
→ Classification: 2

Example 2  
Question: What is the capital of France?  
Answer: France is a country in Western Europe with a rich history.  
→ Classification: 1  
(Reason: Vaguely related, but doesn’t answer the specific question)

Example 3  
Question: What is the capital of France?  
Answer: The capital of France is Madrid.  
→ Classification: 0  
(Reason: Incorrect information)

Example 4  
Question: How does photosynthesis work?  
Answer: It’s something plants do to grow.  
→ Classification: 1  
(Reason: Too vague and incomplete, but somewhat relevant)

Example 5  
Question: How does photosynthesis work?  
Answer: Photosynthesis is the process by which green plants use sunlight to synthesize food from carbon dioxide and water.  
→ Classification: 2

Example 6  
Question: How does photosynthesis work?  
Answer: The stock market fluctuates based on investor behavior.  
→ Classification: 0  
(Reason: Completely unrelated)

## Output Format
Respond with a single value: `2`, `1`, or `0` corresponding to the classification.
"""


class LLMAsJudgeEvaluator:
    """Class to evaluate the helpfulness of a generated answer using an LLM."""

    def __init__(self, model: Optional[str] = None):
        if model is None:
            self.model = LLM_PROXY.get_used_model()
        else:
            self.model = model

        self._token_consuption: TokenConsumption
        self._llm_call_count: int = 0

        self.prompt_template = PromptTemplate.from_template(PROMPT_TEMPLATE)

    def evaluate(self, question: str, generated_answer: str) -> LLMJudgeOutcome:
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

        self._token_consuption = LLM_PROXY.get_token_usage()
        self._llm_call_count = LLM_PROXY.get_call_count()

        # Reset the model in the LLMProxy if it was changed
        if model_changed:
            LLM_PROXY.set_new_model(current_model)

        response = response.strip() if isinstance(response, str) else response

        # Parse the response
        if response == 2 or response == "2":
            return LLMJudgeOutcome.FULLY_HELPFUL
        elif response == 1 or response == "1":
            return LLMJudgeOutcome.PARTIALLY_HELPFUL
        elif response == 0 or response == "0":
            return LLMJudgeOutcome.NOT_HELPFUL
        else:
            raise ValueError(
                f"Unexpected response: {response}, datatype {type(response)}"
            )

    def get_token_consumption(self) -> TokenConsumption:
        """Get the token consumption statistics."""
        return self._token_consuption

    def get_llm_call_count(self) -> int:
        """Get the number of LLM calls made."""
        return self._llm_call_count
