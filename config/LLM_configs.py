from enum import Enum


class SupportedLLMs(Enum):
    GEMINI_15_FLASH = 1


GEMINI_15_FLASH = {
    "name": "gemini-1.5-flash",
    "key_name": "GOOGLE_API_KEY",
}
