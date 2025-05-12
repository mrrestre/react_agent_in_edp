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

    cloud_type: ChatSlotCloudType


class SearchRequestObject(BaseModel):
    """Model for the search request object."""

    prompt_introduction: str
    chat_entries: list[ChatEntry]
    chat_slots: ChatSlotContainer
    collection_id: str
    max_chunk_count_collection: (
        int  # How many chunks of own collection (vector docs) should be included?
    )
    max_chunk_count_sap_help: int  # How many chunks of SAP Help should be included?


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
