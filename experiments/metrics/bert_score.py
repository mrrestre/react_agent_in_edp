"""Compute BERTScore for a given expected and actual response."""

from typing import cast
from bert_score import score
from pydantic import BaseModel


class BertScoreValues(BaseModel):
    """Values for BERTScore."""

    PRECISION: float
    RECALL: float
    F1: float


class BertScore:
    """Compute BERTScore for a given expected and actual response."""

    @staticmethod
    def compute_score(expected_response: str, actual_response: str) -> BertScoreValues:
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
            # rescale_with_baseline=True,
            # Reasoning: https://github.com/Tiiiger/bert_score/blob/master/journal/rescale_baseline.md
            # Rescaling to make score easier to interpret since "regular" BERT  tends to be around 0.85.
        )
        return BertScoreValues(
            PRECISION=cast(float, precision.mean().item()),
            RECALL=cast(float, recall.mean().item()),
            F1=cast(float, f1.mean().item()),
        )


# BERTScore (2019): BERTScore matches tokens via contextual embeddings and reports precision/recall/F1.
# It does correlate with semantic similarity (better than BLEU/ROUGE), but it is highly sensitive to length mismatch.
# In a short-ref/long-cand scenario, recall can be high (reference covered) but precision will be low (many extra words), so the F1 score drops.
# Thus BERTScore by itself underestimates semantic overlap when the candidate is much longer.
# One workaround is to examine recall only, or to compute F1 in a way that downweights precision but out-of-the-box it penalizes extra content.
