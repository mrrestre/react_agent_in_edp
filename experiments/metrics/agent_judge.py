"""Agent Judge Evaluator for assessing agent responses."""

from pydantic import BaseModel, Field
from langchain_core.messages import AIMessage

from experiments.models.experiment_models import AgentJudgeOutcome
from react_agent.src.agents.react_agent import ReActAgent
from react_agent.src.config.system_parameters import TriageSettings
from react_agent.src.util.tools_fabric import ToolsFabric

from react_agent.src.util.llm_proxy import LLM_PROXY, TokenConsumption

JUDGE_USER_MESSAGE_TEMPLATE = """## Input
Question: {question}
Expert Answer: {expert_answer}
Generated Answer: {generated_answer}"""


class JudgementResponseFormat(BaseModel):
    """Always without execptions use this tool to structure your response to the user."""

    answer: AgentJudgeOutcome = Field(
        description="The judgement of the agent's response"
    )
    reasoning: str = Field(description="The reasoning behind the judgement")


class AgentJudgeEvaluator:
    """Class to evaluate the helpfulness of an agent's response using a ReActAgent."""

    def __init__(self, model: str = None):
        """Initialize the Agent Judge Evaluator with a ReActAgent."""
        self.default_llm_proxy_model = LLM_PROXY.get_used_model()

        self._token_consumption: TokenConsumption
        self._llm_call_count: int = 0
        self.llm_model_changed: bool = False

        self.set_llm_proxy_model(model)

        fabric = ToolsFabric()
        tools = fabric.get_tools_for_category(
            use_mcp=False, configuration=TriageSettings().Categories.ALL
        )
        tools.append(JudgementResponseFormat)
        self.agent = ReActAgent(tool_list=tools, is_judge_agent=True)

    def evaluate(
        self, question: str, expert_answer: str, generated_answer: str
    ) -> JudgementResponseFormat:
        """Evaluate the agent's response to a question using the ReActAgent."""

        user_message = JUDGE_USER_MESSAGE_TEMPLATE.format(
            question=question,
            expert_answer=expert_answer,
            generated_answer=generated_answer,
        )
        execution_trail = self.agent.run_agent_with_input(user_message=user_message)

        run_data = self.agent.run_data
        self._token_consumption = run_data.tokens_consumed
        self._llm_call_count = run_data.llm_call_count

        # Last is agent final response, secont to last is tool call (formater) and third to last is ai message containing the tool call
        ai_message_tool_call = execution_trail["messages"][-3]

        if isinstance(ai_message_tool_call, AIMessage):
            return JudgementResponseFormat.model_validate(
                ai_message_tool_call.tool_calls[0]["args"]
            )

        raise ValueError(
            f"Unexpected response: {ai_message_tool_call["content"]}, datatype {type(ai_message_tool_call["content"])}"
        )

    def set_llm_proxy_model(self, model: str) -> None:
        """Set the model used by the agent."""
        # Set the model in the LLMProxy if differs from the current one
        if model != self.default_llm_proxy_model:
            LLM_PROXY.set_new_model(model)
            self.llm_model_changed = True

    def get_token_consumption(self) -> TokenConsumption:
        """Get the token consumption statistics."""
        return self._token_consumption

    def get_llm_call_count(self) -> int:
        """Get the number of LLM calls made."""
        return self._llm_call_count

    def reset_llm_proxy_model(self) -> None:
        """Reset the model used by the agent to the original one."""
        if self.llm_model_changed:
            LLM_PROXY.set_new_model(self.default_llm_proxy_model)

    def __del__(self):
        """Reset the LLM model when the evaluator is deleted."""
        self.reset_llm_proxy_model()
