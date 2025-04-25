from pydantic_settings import BaseSettings


class FactScoreSettings(BaseSettings):
    path_to_example_demos: str = "./ressources/atomic_facts_demons.json"
