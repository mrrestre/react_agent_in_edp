from abc import ABC, abstractmethod

from typing import Type

from pydantic import BaseModel


class IAgentTool(ABC):
    name: str
    description: str
    args_schema: Type[BaseModel]

    @staticmethod
    @abstractmethod
    def method(*args) -> str:
        pass
