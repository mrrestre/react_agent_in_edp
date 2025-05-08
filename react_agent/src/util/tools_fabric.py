"""Fabric class for instanciating or fetching agent tools based on configuration"""

import os
from typing import Optional, Union

from dotenv import load_dotenv
from react_agent.src.agent_tools.documentation_retriever import DocumentationRetriever
from react_agent.src.agent_tools.sap_help_searcher import SapHelpSearcher
from react_agent.src.agent_tools.troubleshooting_searcher import TroubleshootingSearcher
from react_agent.src.agent_tools.codebase_searcher import CodebaseSearcher
from react_agent.src.agent_tools.source_code_retriever import SourceCodeRetriever

from react_agent.src.config.system_parameters import (
    TriageSettings,
    ToolsFabricSettings,
    QAToolsServerSettings,
    CodingToolsServerSettings,
)
from react_agent.src.util.logger import LoggerSingleton

TRIAGE_SETTINGS = TriageSettings()
TOOLS_FABRIC_SETTINGS = ToolsFabricSettings()
LOGGER = LoggerSingleton.get_logger(TOOLS_FABRIC_SETTINGS.logger_name)

_ = load_dotenv()

SMITHERY_API_KEY: str = os.getenv("SMITHERY_API_KEY")


class ToolsFabric:
    """Fabric class for instanciating or fetching agent tools based on configuration"""

    @staticmethod
    def get_tools_for_category(
        use_mcp: bool,
        configuration: TriageSettings.Categories,
        include_web_search: Optional[bool] = False,
    ) -> Union[dict, list]:
        """Fabric method for instanciating or fetching agent tools based on configuration"""
        LOGGER.info(
            "Getting tools for configuration: %s using mcp: %s", configuration, use_mcp
        )
        if use_mcp:
            multi_server_client_config = {}

            if include_web_search:
                multi_server_client_config["DuckDuckGo"] = {
                    "url": TOOLS_FABRIC_SETTINGS.duckduckgo_url.format(
                        config_b64=TOOLS_FABRIC_SETTINGS.duckduckgo_config,
                        smithery_api_key=SMITHERY_API_KEY,
                    ),
                    "transport": TOOLS_FABRIC_SETTINGS.duckduckgo_protocol,
                }

            if configuration == TRIAGE_SETTINGS.Categories.KNOWLEDGE_QA:
                qa_server_settings = QAToolsServerSettings()

                multi_server_client_config["QuestionAnsweringTools"] = {
                    "url": f"http://{qa_server_settings.host}:{qa_server_settings.port}/{qa_server_settings.transport}",
                    "transport": qa_server_settings.transport,
                }

            if configuration == TRIAGE_SETTINGS.Categories.CONFIG_RCA:
                rca_server_settings = CodingToolsServerSettings()

                multi_server_client_config["CodingTools"] = {
                    "url": f"http://{rca_server_settings.host}:{rca_server_settings.port}/{rca_server_settings.transport}",
                    "transport": rca_server_settings.transport,
                }
            return multi_server_client_config
        else:
            tool_list = []

            if configuration == TRIAGE_SETTINGS.Categories.KNOWLEDGE_QA:
                tool_list.append(DocumentationRetriever())
                tool_list.append(TroubleshootingSearcher())
                tool_list.append(SapHelpSearcher())
            if configuration == TRIAGE_SETTINGS.Categories.CONFIG_RCA:
                tool_list.append(CodebaseSearcher())
                tool_list.append(SourceCodeRetriever())

            return tool_list
