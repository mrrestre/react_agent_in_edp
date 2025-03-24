from pydantic import BaseModel, Field
from typing import List, Type

from agent_tools.i_agent_tool import IAgentTool


class MeetingDetails(BaseModel):
    attendees: List[str] = Field(..., description="List of attendees")
    subject: str = Field(..., description="Subject of the meeting")
    duration_minutes: int = Field(..., description="Duration of the meeting in minutes")
    preferred_day: str = Field(..., description="Preferred day for the meeting")


class MeetingScheduler(IAgentTool):
    name: str = "schedule_meeting"
    description: str = "Schedule calendar meetings"
    args_schema: Type[BaseModel] = MeetingDetails

    @staticmethod
    def method(
        attendees: list[str],
        subject: str,
        duration_minutes: int,
        preferred_day: str,
    ) -> str:
        """Schedule a calendar meeting."""
        # Placeholder response - in real app would check calendar and schedule
        return f"Meeting '{subject}' scheduled for {preferred_day} with {len(attendees)} attendees for {duration_minutes} minutes"
