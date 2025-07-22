"""This script loads ABAP class definitions into a memory database for further processing."""

import os
import json

from react_agent.src.config.system_parameters import CodebaseSearcherSettings

from react_agent.src.agent_tools.source_code_retriever import SourceCodeRetriever

from react_agent.src.util.abap_repository import ABAPClassRepository
from react_agent.src.util.memory_manager import MemoryManager
from react_agent.src.util.code_summarizer import CodeSummarizer

FILE_TO_LOAD = "class_subset.json"  # Options: "class_subset.json", "all_clases.json"
notebook_dir = os.path.abspath("")

file_path = os.path.abspath(os.path.join(notebook_dir, "./", "resources", FILE_TO_LOAD))

with open(file_path, encoding="utf8") as f:
    json_file = json.load(f)

classes: list[tuple] = []

for my_class in json_file["classes"]:
    classes.append((my_class["name"].lower(), my_class["description"]))


CODE_SEARCHER_SETTINGS = CodebaseSearcherSettings()

MEMORY_MANAGER = MemoryManager(
    memory_store_type="Postgres",
    namespace=CODE_SEARCHER_SETTINGS.namespace,
    embedding_fields=["description"],
)

code_lookup = SourceCodeRetriever()

for my_class in classes:
    print("Class name: ", my_class[0])
    class_name = my_class[0]
    class_description = my_class[1]

    class_code = code_lookup._run(class_name=class_name)

    print("\t- Started indexing")
    repository = ABAPClassRepository(source_code=class_code)
    if len(repository.classes) == 0:
        print(f"\t- No methods found for class: {class_name}")
        continue

    print(
        f"\t- Finished indexing, number of methods: {len(repository.classes.get(class_name).keys())}"
    )

    for method_name in repository.classes[class_name].keys():
        if not MEMORY_MANAGER.is_memory_present(f"{class_name}.{method_name}"):
            print(f"\t- Summarizing and adding method: {method_name}")
            # Summarize the code of the method and add it to the memory
            memory_content = {
                "description": CodeSummarizer.summarize_code(
                    f"Class description: {class_description}\n"
                    + repository.get_content_by_class_and_method(
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
        else:
            print(f"\t- Skipping method: {method_name}")
            continue
