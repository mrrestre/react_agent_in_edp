"""Model for the search request object."""

from enum import StrEnum
from openai import BaseModel


class OauthTokenResponse(BaseModel):
    """Model for the OAuth token response."""

    access_token: str
    token_type: str
    expires_in: int


class ChatSlotCloudType(StrEnum):
    """Enum for the cloud type of the chat slot."""

    PUBLIC_CLOUD = "public_cloud"
    PRIVATE_CLOUD = "private_cloud"


class ChatRole(StrEnum):
    """Enum for the role of the chat entry."""

    SYSTEM = "system"
    USER = "user"


class ChatEntry(BaseModel):
    """Model for a chat entry."""

    role: ChatRole = ChatRole.USER
    content: str


class ChatSlotContainer(BaseModel):
    """Model for the chat slot container."""

    cloud_type: ChatSlotCloudType = ChatSlotCloudType.PRIVATE_CLOUD


class SearchRequestObject(BaseModel):
    """Model for the search request object."""

    prompt_introduction: str = (
        "You are a Support Engineer working in the context of Document Reporting and Compliance, cloud edition (DRCce).\nYou are given information and troubleshooting guides to help solve issues.\n"
    )
    chat_entries: list[ChatEntry]
    chat_slots: ChatSlotContainer = ChatSlotContainer(
        cloud_type=ChatSlotCloudType.PUBLIC_CLOUD
    )
    collection_id: str = "70386ab8-eeac-452c-b2e6-cac902ca451c"
    max_chunk_count_collection: int = (
        6  # How many chunks of own collection (vector docs) should be included?
    )
    max_chunk_count_sap_help: int = 1  # How many chunks of SAP Help should be included?


class ChunkSource(BaseModel):
    """Model for the chunk source."""

    chunk_id: str
    url: str
    chunk_title: str


class SearchResponseObject(BaseModel):
    """Model for the search response object."""

    correlation_id: str
    llm_response: str
    sources_all: list[ChunkSource]
    sources_markdown: str
    response_session_id: str
    prompt: str | None = None
    chat_id: str | None = None


class DocumentGroundingResponse(BaseModel):
    """Model for the document grounding response."""

    response: str
