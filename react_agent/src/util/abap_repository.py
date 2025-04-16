"""Class for indexing and accessing methods and class from a txt file"""

import os
import re
from typing import Dict

from react_agent.src.config.system_parameters import ABAPRepositorySettings
from react_agent.src.util.logger import LoggerSingleton
from react_agent.src.util.sap_system_proxy import SAPSystemProxy

SETTINGS = ABAPRepositorySettings()
LOGGER = LoggerSingleton.get_logger(SETTINGS.logger_name)


class ABAPClassRepository:
    """Class for indexing and accessing methods and class from a txt file"""

    def __init__(self, class_name: str = None):
        """Initialize an empty repository for storing ABAP classes and methods."""
        self.classes: Dict[str, Dict[str, str]] = {}

        # Index the local ABAP source file
        source_code = self._read_local_abap_source_file()
        self._index_source(source_code=source_code)

        # If an specific class was passed, get the content for that class only if not already indexed
        if class_name is not None and self.classes.get(class_name) is None:
            xco2_source_code = self._query_xco2_service(class_name=class_name)
            if xco2_source_code is not None:
                self._index_source(source_code=xco2_source_code)

    def _read_local_abap_source_file(self) -> str:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, "resources", "abap_source.txt")
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()

    def _add_method(
        self, class_name: str, method_name: str, method_content: str
    ) -> str:
        """Adds a method to the corresponding class."""
        class_name = class_name.lower()
        method_name = method_name.lower()

        if class_name not in self.classes:
            self.classes[class_name] = {}
        self.classes[class_name][method_name] = method_content

    def get_content_by_class(self, class_name: str) -> str:
        """Returns all methods for a given class as a string."""
        LOGGER.info("Getting content for class: %s", class_name)
        class_name = class_name.lower()
        methods = self.classes.get(class_name, {})

        if not methods:
            raise KeyError(
                f"No methods for this class indexed, indexed classes: {self.list_indexed_classes()}"
            )

        return "\n\n".join(methods.values())

    def get_content_by_method(self, method_name: str) -> str:
        """Search for a method across all classes and return the content of matching methods as a single string."""
        LOGGER.info("Getting content for method: %s", method_name)
        method_name = method_name.lower()
        results: list[tuple[str, str]] = []

        for class_name, methods in self.classes.items():
            if method_name in methods:
                results.append((class_name, methods[method_name]))

        # If no methods found, return a "Method not found" message
        if not results:
            raise KeyError(f"Method with name {method_name} not exists")

        # Otherwise, join the method contents into a single string and return
        return "\n".join(
            [
                f"Class: {t[0]}\nMethod Name: {method_name}\nMethod Implentation:\n{t[1]}"
                for t in results
            ]
        )

    def get_content_by_class_and_method(self, class_name: str, method_name: str) -> str:
        """Returns the content of a specific method in a class."""
        LOGGER.info(
            "Getting content for class: %s and method: %s", class_name, method_name
        )
        class_name = class_name.lower()
        method_name = method_name.lower()

        method_content = self.classes.get(class_name, {}).get(method_name, None)

        if method_content is None:
            raise KeyError(
                f"Method with name {method_name} does not exists in class {class_name}"
            )

        return f"Class: {class_name}\nMethod Name: {method_name}\nMethod Implementation:\n{method_content}"

    def list_indexed_classes(self) -> list[str]:
        """Returns a list of all stored class names."""
        class_names = list(self.classes.keys())

        return " ".join(class_names)

    def _index_source(self, source_code: str) -> None:
        """Indexes ABAP classes and methods from a source file."""
        LOGGER.info("Indexing source file")
        class_name_pattern = r"\bCLASS\s+([A-Za-z0-9_]{1,30})\s+IMPLEMENTATION"
        method_name_pattern = r"\bMETHOD\s+([A-Za-z0-9_]+)\s*\."

        current_class_name = None
        current_method_name = None
        method_content = ""

        if not source_code:
            raise ValueError("File contents is empty")

        # Split classes properly
        class_entries = re.split(r"\bENDCLASS\.", source_code, flags=re.IGNORECASE)

        for class_entry in class_entries:
            class_entry.strip(" \n")
            class_match = re.search(class_name_pattern, class_entry, re.IGNORECASE)
            if class_match:
                current_class_name = class_match.group(1)
            else:
                continue

            # Split method content using the method pattern
            method_entries = re.split(r"ENDMETHOD\.", class_entry, flags=re.IGNORECASE)

            for method_entry in method_entries:
                method_match = re.search(
                    method_name_pattern, method_entry, re.IGNORECASE
                )
                if method_match:
                    current_method_name = method_match.group(1)
                    method_content = method_entry.lstrip("\n")

                    if current_method_name and method_content:
                        self._add_method(
                            current_class_name,
                            current_method_name,
                            f"{method_content}\n ENDMETHOD.",
                        )
                else:
                    continue

    def _query_xco2_service(self, class_name: str) -> str:
        response = SAPSystemProxy().get_endpoint_https(f"classes('{class_name}')")
        return response.get("code")

    def __repr__(self):
        """Returns a string representation of stored classes and methods."""
        return "\n".join(
            f"{class_name}:\n  " + "\n  ".join(methods.keys())
            for class_name, methods in self.classes.items()
        )
