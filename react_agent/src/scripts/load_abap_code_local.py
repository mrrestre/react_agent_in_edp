"""Help script for loading the local abap classes into the memory database"""

import os

from react_agent.src.config.system_parameters import CodebaseSearcherSettings
from react_agent.src.util.abap_repository import ABAPClassRepository
from react_agent.src.util.code_summarizer import CodeSummarizer
from react_agent.src.util.memory_manager import MemoryManager

CODE_SEARCHER_SETTINGS = CodebaseSearcherSettings()

MEMORY_MANAGER = MemoryManager(
    memory_store_type="Postgres",
    namespace=CODE_SEARCHER_SETTINGS.namespace,
    embedding_fields=["description"],
)


def load_abap_code() -> bool:
    """Load memories from reference ABAP Source if not already loaded"""
    memory_added = False
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "resources", "abap_source.txt")

    with open(file_path, "r", encoding="utf-8") as file:
        file_content = file.read()

    repository = ABAPClassRepository(source_code=file_content)

    for class_name in repository.list_indexed_classes():
        for method_name in repository.classes[class_name].keys():
            if not MEMORY_MANAGER.is_memory_present(f"{class_name}.{method_name}"):
                # Summarize the code of the method and add it to the memory
                memory_content = {
                    "description": CodeSummarizer.summarize_code(
                        repository.get_content_by_class_and_method(
                            class_name=class_name, method_name=method_name
                        )
                    ),
                    "code": repository.get_content_by_class_and_method(
                        class_name=class_name, method_name=method_name
                    ),
                }
                MEMORY_MANAGER.add_memory(
                    memory_title=f"{class_name}.{method_name}",
                    memory_content=memory_content,
                )
                memory_added = True

    return memory_added


print(f"Loaded new memories: {load_abap_code()}")
