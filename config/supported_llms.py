from enum import Enum


class SupportedLLMs(Enum):
    GPT_4o = "gpt-4o"

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_
