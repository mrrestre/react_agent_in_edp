from typing import Type

from pydantic import BaseModel, Field

from langchain.tools.base import BaseTool


class DateRequest(BaseModel):
    year: str = Field(..., description="year for the request")
    month: str = Field(..., description="month for the request")
    day: str = Field(..., description="day for the request")


class AvailabilityChecker(BaseTool):
    name: str = "check_calendar_availability"
    description: str = "Check available time slots for a given day"
    args_schema: Type[BaseModel] = DateRequest

    def _run(
        self,
        year: str,
        month: str,
        day: str,
    ) -> str:
        """Check calendar availability for a given day."""
        # Placeholder response - in real app would check actual calendar
        return f"Available times on {day}/{month}/{year}: 9:00 AM, 2:00 PM, 4:00 PM"

    async def _arun(
        self,
        year: str,
        month: str,
        day: str,
    ) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("check_calendar_availability does not support async")
