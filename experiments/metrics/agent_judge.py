"""Agent Judge Evaluator for assessing agent responses."""

from experiments.models.experiment_models import LLMJudgeOutcome
from react_agent.src.agents.react_agent import ReActAgent
from react_agent.src.config.system_parameters import TriageSettings
from react_agent.src.util.tools_fabric import ToolsFabric

JUDGE_SYS_PROMPT_TEMPLATE = """## Role
You are a strict and fair evaluator of answer quality. Your job is to assess whether a generated answer adequately addresses a given question. Be conservative in your judgments — an answer must be clearly complete and correct to be rated as fully helpful.

## Task
Given a question and a generated answer, classify the answer into one of three categories:

- 2 = Fully Helpful: The answer directly, accurately, and completely addresses the question. No major information is missing.
- 1 = Partially Helpful: The answer is somewhat relevant and may include some correct information, but is incomplete, vague, or partially incorrect.
- 0 = Not Helpful: The answer is irrelevant, incorrect, off-topic, or otherwise fails to help the user meaningfully.

You must focus on the **quality of the response relative to the question** — not on how plausible it sounds.

## Instructions
{react_instructions}

## Tools
You have access to the following tools to gather facts, retrieve relevant data, and answer technical or compliance-related queries:
{tools}

## Rules
{rules}

## Tool Rankings
{tool_rankings}

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
Answer: It's something plants do to grow.  
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
Respond with a single number: 2, 1, or 0 corresponding to the classification.
"""

USER_MESSAGE_TEMPLATE = """## Input
Question: {question}
Generated Answer: {answer}"""


class AgentJudgeEvaluator:
    """Class to evaluate the helpfulness of an agent's response using a ReActAgent."""

    def __init__(self):
        """Initialize the Agent Judge Evaluator with a ReActAgent."""
        fabric = ToolsFabric()
        tools = fabric.get_tools_for_category(
            use_mcp=False, configuration=TriageSettings().Categories.ALL
        )
        self.agent = ReActAgent(
            tool_list=tools, custom_judge_prompt=JUDGE_SYS_PROMPT_TEMPLATE
        )

    def evaluate(self, question: str, agent_response: str) -> str:
        """Evaluate the agent's response to a question using the ReActAgent."""
        user_message = USER_MESSAGE_TEMPLATE.format(
            question=question, answer=agent_response
        )
        self.agent.run_agent_with_input(user_message=user_message)

        agent_response = self.agent.run_data.final_output

        response = (
            response.strip() if isinstance(agent_response, str) else agent_response
        )

        # Parse the response
        if response == 2 or response == "2":
            return LLMJudgeOutcome.FULLY_HELPFUL
        if response == 1 or response == "1":
            return LLMJudgeOutcome.PARTIALLY_HELPFUL
        if response == 0 or response == "0":
            return LLMJudgeOutcome.NOT_HELPFUL

        raise ValueError(f"Unexpected response: {response}, datatype {type(response)}")
