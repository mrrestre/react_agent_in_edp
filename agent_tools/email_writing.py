from typing import Type

from pydantic import BaseModel

from agent_tools.i_agent_tool import IAgentTool


class EmailInputModel(BaseModel):
    to: str
    subject: str
    content: str


class EmailWriter(IAgentTool):
    name: str = "write_email"
    description: str = "Send emails to specified recipients"
    args_schema: Type[BaseModel] = EmailInputModel

    @staticmethod
    def method(to: str, subject: str, content: str) -> str:
        """Write and send an email."""
        return f"Email sent to {to} with subject '{subject}' and content '{content}'"
