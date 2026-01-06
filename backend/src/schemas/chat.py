"""Pydantic schemas for chat endpoints."""
from typing import Optional, List, Any
from pydantic import BaseModel, Field
from enum import Enum


class ThinkingStepType(str, Enum):
    """Types of thinking steps for agent transparency."""
    ANALYZING = "analyzing"
    PLANNING = "planning"
    TOOL_CALL = "tool_call"
    PROCESSING = "processing"
    CLARIFYING = "clarifying"


class ThinkingStep(BaseModel):
    """Schema for agent thinking/reasoning step."""

    type: ThinkingStepType = Field(..., description="Type of thinking step")
    content: str = Field(..., description="Description of what agent is doing")
    timestamp: Optional[float] = Field(None, description="Timestamp in seconds since request start")


class ToolCall(BaseModel):
    """Schema for tool call information."""

    tool: str = Field(..., description="Name of the tool that was called")
    parameters: dict[str, Any] = Field(..., description="Parameters passed to the tool")
    result: dict[str, Any] = Field(..., description="Result returned by the tool")
    duration_ms: Optional[int] = Field(None, description="Execution time in milliseconds")


class ConfirmationRequest(BaseModel):
    """Schema for confirmation required response."""

    action: str = Field(..., description="Action requiring confirmation (e.g., 'delete_all', 'complete_all')")
    message: str = Field(..., description="Human-readable confirmation message")
    affected_items: List[dict[str, Any]] = Field(default_factory=list, description="Items that will be affected")
    confirm_token: str = Field(..., description="Token to send back to confirm action")


class ChatRequest(BaseModel):
    """Schema for chat message request."""

    conversation_id: Optional[int] = Field(None, description="Existing conversation ID (optional)")
    message: str = Field(..., min_length=1, max_length=4000, description="User message content")
    confirm_token: Optional[str] = Field(None, description="Confirmation token for bulk operations")


class ChatResponse(BaseModel):
    """Schema for chat response."""

    conversation_id: int = Field(..., description="Conversation ID for this exchange")
    response: str = Field(..., description="Assistant's response message")
    tool_calls: List[ToolCall] = Field(default_factory=list, description="Tools called during processing")
    thinking_steps: List[ThinkingStep] = Field(default_factory=list, description="Agent reasoning steps")
    confirmation_required: Optional[ConfirmationRequest] = Field(None, description="Confirmation needed for bulk ops")
    processing_time_ms: Optional[int] = Field(None, description="Total processing time")

    class Config:
        from_attributes = True


class ChatMessage(BaseModel):
    """Schema for a single chat message."""

    id: Optional[int] = Field(None, description="Message ID")
    role: str = Field(..., description="Message role (user or assistant)")
    content: str = Field(..., min_length=1, max_length=4000, description="Message content")
    tool_calls: Optional[List[ToolCall]] = Field(None, description="Tool calls for this message")
    thinking_steps: Optional[List[ThinkingStep]] = Field(None, description="Thinking steps for this message")
    created_at: Optional[str] = Field(None, description="Creation timestamp")

    class Config:
        from_attributes = True
