"""Help script for loading the local troubleshooting guides into the memory database"""

import os
import json

from react_agent.src.util.memory_manager import MemoryManager

from react_agent.src.config.system_parameters import TroubleshootingSearchSettings

TOOL_SETTINGS = TroubleshootingSearchSettings()

MEMORY_MANAGER = MemoryManager(
    memory_store_type="Postgres",
    namespace=TOOL_SETTINGS.namespace,
    embedding_fields=["text"],
)


def load_memories() -> bool:
    """Load memories from reference troubleshooting json file if not already loaded"""
    memory_added = False
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "resources", "troubleshooting.json")

    with open(file_path, encoding="utf8") as f:
        json_file = json.load(f)

    for article in json_file.get("articles"):
        if not MEMORY_MANAGER.is_memory_present(article.get("title")):
            memory_content = {"text": article.get("text")}
            MEMORY_MANAGER.add_memory(
                memory_title=article.get("title"), memory_content=memory_content
            )
            memory_added = True

    return memory_added


print(f"Loaded new memories: {load_memories()}")
