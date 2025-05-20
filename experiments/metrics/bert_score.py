"""Compute BERTScore for a given expected and actual response."""

from typing import cast
from bert_score import score


class BertScore:
    """Compute BERTScore for a given expected and actual response."""

    @staticmethod
    def compute_score(expected_response: str, actual_response: str) -> float:
        """Compute BERTScore for a given expected and actual response.
        Args:
            expected_response (str): The expected response.
            actual_response (str): The actual response.
        Returns:
            float: The BERTScore for the given expected and actual response.
        """
        (precision, recall, f1) = score(
            cands=[actual_response],
            refs=[expected_response],
            model_type="microsoft/deberta-xlarge-mnli",
            lang="en",
            rescale_with_baseline=True,
            # Reasoning: https://github.com/Tiiiger/bert_score/blob/master/journal/rescale_baseline.md
        )
        return cast(float, recall.mean().item())
