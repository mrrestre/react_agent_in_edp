from typing import Type

from pydantic import BaseModel, Field

from langchain.tools.base import BaseTool


class EmailInputModel(BaseModel):
    to: str = Field(..., description="to whom the email is ment to")
    subject: str = Field(..., description="email subject")
    content: str = Field(..., description="email content")


class EmailWriter(BaseTool):
    name: str = "write_email"
    description: str = "Send emails to specified recipients"
    args_schema: Type[BaseModel] = EmailInputModel

    def _run(
        self,
        to: str,
        subject: str,
        content: str,
    ) -> str:
        """Write and send an email."""
        return f"Email sent to {to} with subject '{subject}' and content '{content}'"
