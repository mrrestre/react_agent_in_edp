"""Utility functions for summarizing ABAP code"""

from langchain.prompts import PromptTemplate

from react_agent.src.config.system_parameters import CodeSummarizerSettings
from react_agent.src.util.llm_proxy import LLM_PROXY

SETTINGS = CodeSummarizerSettings()


class CodeSummarizer:
    """Class for summarizing ABAP code."""

    @staticmethod
    def summarize_code(code: str) -> str:
        """Summarize ABAP code into a description"""
        prompt_template = PromptTemplate.from_template(SETTINGS.prompt_template)
        prompt = prompt_template.format(source_code=code)
        return LLM_PROXY.invoke(input=prompt)
