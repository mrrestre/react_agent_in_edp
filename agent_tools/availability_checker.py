from typing import Type
from agent_tools.i_agent_tool import IAgentTool
from pydantic import BaseModel


class DayRequest(BaseModel):
    day: str


class AvailabilityChecker(IAgentTool):
    name: str = "check_calendar_availability"
    description: str = "Check available time slots for a given day"
    args_schema: Type[BaseModel] = DayRequest

    @staticmethod
    def method(day: str) -> str:
        """Check calendar availability for a given day."""
        # Placeholder response - in real app would check actual calendar
        return f"Available times on {day}: 9:00 AM, 2:00 PM, 4:00 PM"
