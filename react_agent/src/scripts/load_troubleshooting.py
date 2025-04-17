import os
import json

from react_agent.src.util.memory_manager import MemoryManager


def load_memories(
    mem_manager: MemoryManager,
) -> None:
    """Load memories from reference troubleshooting json file if not already loaded"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "resources", "troubleshooting.json")

    with open(file_path, encoding="utf8") as f:
        json_file = json.load(f)

    for article in json_file.get("articles"):
        if not mem_manager.is_memory_present(article.get("title")):
            memory_content = {"text": article.get("text")}
            mem_manager.add_memory(
                memory_title=article.get("title"), memory_content=memory_content
            )
