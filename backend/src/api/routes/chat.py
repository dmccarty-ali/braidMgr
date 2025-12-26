"""
Chat API routes.

Provides AI chat endpoints with WebSocket streaming support.

Endpoints:
    POST /chat/message - Send a message and get a response
    WS /chat/ws - WebSocket for streaming chat
    DELETE /chat/history - Clear conversation history
"""

import json
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from pydantic import BaseModel

from src.api.dependencies.auth import get_optional_user
from src.domain.auth import CurrentUser
from src.services.chat_service import ChatService, get_chat_service, ChatMessage
from src.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/chat", tags=["Chat"])


# =============================================================================
# Request/Response Schemas
# =============================================================================


class ChatMessageRequest(BaseModel):
    """Request body for sending a chat message."""

    message: str
    project_id: Optional[str] = None


class ChatMessageResponse(BaseModel):
    """Response containing assistant's reply."""

    id: str
    content: str
    role: str = "assistant"


class ChatHistoryResponse(BaseModel):
    """Response containing conversation history."""

    messages: list[dict]


# =============================================================================
# REST Endpoints
# =============================================================================


@router.post(
    "/message",
    response_model=ChatMessageResponse,
    summary="Send chat message",
    description="Send a message to Claude and get a response.",
)
async def send_message(
    body: ChatMessageRequest,
    current_user: Optional[CurrentUser] = Depends(get_optional_user),
    chat_service: ChatService = Depends(get_chat_service),
) -> ChatMessageResponse:
    """Send a message and get a response."""
    if not body.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty",
        )

    # Parse project_id if provided
    project_id = None
    if body.project_id:
        try:
            project_id = UUID(body.project_id)
        except ValueError:
            pass

    # Get user ID if authenticated
    user_id = current_user.id if current_user else None

    # Send message and get response
    response = await chat_service.send_message(
        user_message=body.message,
        project_id=project_id,
        user_id=user_id,
    )

    return ChatMessageResponse(
        id=response.id,
        content=response.content,
        role=response.role,
    )


@router.get(
    "/history",
    response_model=ChatHistoryResponse,
    summary="Get chat history",
    description="Retrieve the current conversation history.",
)
async def get_history(
    chat_service: ChatService = Depends(get_chat_service),
) -> ChatHistoryResponse:
    """Get conversation history."""
    return ChatHistoryResponse(messages=chat_service.get_history())


@router.delete(
    "/history",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Clear chat history",
    description="Clear the current conversation history.",
)
async def clear_history(
    chat_service: ChatService = Depends(get_chat_service),
):
    """Clear conversation history."""
    chat_service.clear_history()
    return None


# =============================================================================
# WebSocket Endpoint
# =============================================================================


@router.websocket("/ws")
async def chat_websocket(
    websocket: WebSocket,
    chat_service: ChatService = Depends(get_chat_service),
):
    """
    WebSocket endpoint for streaming chat.

    Message format (client -> server):
        {"type": "message", "content": "user message"}

    Message format (server -> client):
        {"type": "stream", "content": "chunk"}  - Streaming chunk
        {"type": "message", "id": "...", "content": "full response"}  - Complete message
        {"type": "error", "message": "error description"}  - Error
    """
    await websocket.accept()
    logger.info("Chat WebSocket connection established")

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format",
                })
                continue

            if message.get("type") != "message":
                await websocket.send_json({
                    "type": "error",
                    "message": "Unknown message type",
                })
                continue

            user_message = message.get("content", "").strip()
            if not user_message:
                await websocket.send_json({
                    "type": "error",
                    "message": "Message cannot be empty",
                })
                continue

            # Stream the response
            full_response = ""
            try:
                async for chunk in chat_service.stream_message(user_message):
                    full_response += chunk
                    await websocket.send_json({
                        "type": "stream",
                        "content": chunk,
                    })

                # Send complete message signal
                await websocket.send_json({
                    "type": "message",
                    "id": f"msg-{hash(full_response) % 1000000}",
                    "content": full_response,
                })

            except Exception as e:
                logger.error(f"Chat stream error: {e}")
                await websocket.send_json({
                    "type": "error",
                    "message": str(e),
                })

    except WebSocketDisconnect:
        logger.info("Chat WebSocket disconnected")
    except Exception as e:
        logger.error(f"Chat WebSocket error: {e}")
        try:
            await websocket.close(code=1011)
        except Exception:
            pass
