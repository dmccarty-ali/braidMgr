"""
Chat Service for Claude AI integration.

Provides project-aware AI chat with:
- System prompt enforcement for governance
- Usage logging for audit
- WebSocket streaming support
- Dev mode with CLI subprocess, production mode with API

Environment:
    CHAT_MODE: "api" (default) or "cli" for Claude CLI subprocess
    ANTHROPIC_API_KEY: Required for API mode
"""

import asyncio
import json
import os
import subprocess
import threading
from datetime import datetime
from typing import AsyncGenerator, Optional
from uuid import UUID

from src.config import get_config
from src.utils.logging import get_logger

logger = get_logger(__name__)


# =============================================================================
# System Prompt
# Enforces governance by restricting AI to project-related topics
# =============================================================================

SYSTEM_PROMPT = """You are Claude, an AI assistant embedded in braidMgr, a project management application for RAID logs (Risks, Actions, Issues, Decisions, Deliverables, Plan Items, and Budget tracking).

Your role is to help users with:
- Understanding their project status and items
- Analyzing risks, issues, and action items
- Providing project management guidance
- Answering questions about RAID log best practices
- Helping draft item descriptions or updates

Guidelines:
1. Stay focused on project management topics
2. If asked about unrelated topics (personal shopping, entertainment, etc.), politely redirect to project-related assistance
3. Be concise and actionable in your responses
4. When discussing specific items, reference their numbers (e.g., "Item #42")
5. Maintain confidentiality - don't reveal information about other organizations or projects

If the user asks something unrelated, respond with:
"I'm designed to help with project management tasks in braidMgr. Is there something about your project I can help with?"

Current project context will be provided when available.
"""


# =============================================================================
# Chat Message Types
# =============================================================================

class ChatMessage:
    """Represents a chat message."""

    def __init__(
        self,
        role: str,
        content: str,
        message_id: Optional[str] = None,
        timestamp: Optional[datetime] = None,
    ):
        self.role = role  # "user", "assistant", or "system"
        self.content = content
        self.id = message_id or f"msg-{datetime.utcnow().timestamp()}"
        self.timestamp = timestamp or datetime.utcnow()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
        }


# =============================================================================
# Chat Service
# =============================================================================

class ChatService:
    """
    Service for AI chat functionality.

    Supports two modes:
    - API mode (default): Uses Anthropic Python SDK
    - CLI mode: Spawns Claude CLI subprocess (for dev with subscription)
    """

    def __init__(self):
        self.config = get_config()
        self.mode = os.environ.get("CHAT_MODE", "api")
        self._cli_process: Optional[subprocess.Popen] = None
        self._conversation_history: list[dict] = []

        # Check for API key in API mode
        self.api_key = self.config.integrations.anthropic.api_key
        if not self.api_key:
            self.api_key = os.environ.get("ANTHROPIC_API_KEY", "")

        if self.mode == "api" and not self.api_key:
            logger.warning("No ANTHROPIC_API_KEY set - chat will use demo mode")

    async def send_message(
        self,
        user_message: str,
        project_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        project_context: Optional[str] = None,
    ) -> ChatMessage:
        """
        Send a message and get a response.

        Args:
            user_message: The user's message
            project_id: Current project ID for logging
            user_id: User ID for logging
            project_context: Optional project context to include

        Returns:
            ChatMessage with assistant response
        """
        # Log the request for audit
        logger.info(
            "Chat message received",
            extra={
                "user_id": str(user_id) if user_id else None,
                "project_id": str(project_id) if project_id else None,
                "message_length": len(user_message),
            },
        )

        # Build the conversation
        messages = self._conversation_history.copy()
        messages.append({"role": "user", "content": user_message})

        # Get response based on mode
        if self.mode == "cli":
            response_text = await self._send_cli(user_message)
        elif self.api_key:
            response_text = await self._send_api(messages, project_context)
        else:
            response_text = self._demo_response(user_message)

        # Update conversation history
        self._conversation_history.append({"role": "user", "content": user_message})
        self._conversation_history.append({"role": "assistant", "content": response_text})

        # Keep history bounded
        if len(self._conversation_history) > 20:
            self._conversation_history = self._conversation_history[-20:]

        return ChatMessage(role="assistant", content=response_text)

    async def stream_message(
        self,
        user_message: str,
        project_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        project_context: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Stream a response chunk by chunk.

        Yields:
            Response text chunks as they arrive
        """
        if self.mode == "cli":
            # CLI mode doesn't support streaming well, fall back to full response
            response = await self.send_message(
                user_message, project_id, user_id, project_context
            )
            yield response.content
            return

        if not self.api_key:
            yield self._demo_response(user_message)
            return

        # Stream from API
        async for chunk in self._stream_api(
            self._conversation_history + [{"role": "user", "content": user_message}],
            project_context,
        ):
            yield chunk

        # Note: conversation history is updated in _stream_api

    async def _send_api(
        self, messages: list[dict], project_context: Optional[str] = None
    ) -> str:
        """Send message via Anthropic API."""
        try:
            import anthropic

            client = anthropic.Anthropic(api_key=self.api_key)

            # Build system prompt with optional context
            system = SYSTEM_PROMPT
            if project_context:
                system += f"\n\nCurrent Project Context:\n{project_context}"

            response = client.messages.create(
                model=self.config.integrations.anthropic.model,
                max_tokens=1024,
                system=system,
                messages=messages,
            )

            return response.content[0].text

        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            return f"I apologize, but I encountered an error. Please try again. ({type(e).__name__})"

    async def _stream_api(
        self, messages: list[dict], project_context: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """Stream response from Anthropic API."""
        try:
            import anthropic

            client = anthropic.Anthropic(api_key=self.api_key)

            system = SYSTEM_PROMPT
            if project_context:
                system += f"\n\nCurrent Project Context:\n{project_context}"

            full_response = ""

            with client.messages.stream(
                model=self.config.integrations.anthropic.model,
                max_tokens=1024,
                system=system,
                messages=messages,
            ) as stream:
                for text in stream.text_stream:
                    full_response += text
                    yield text

            # Update conversation history after streaming completes
            if messages:
                self._conversation_history.append(messages[-1])  # user message
            self._conversation_history.append(
                {"role": "assistant", "content": full_response}
            )

        except Exception as e:
            logger.error(f"Anthropic API stream error: {e}")
            yield f"I apologize, but I encountered an error. ({type(e).__name__})"

    async def _send_cli(self, user_message: str) -> str:
        """
        Send message via Claude CLI subprocess.

        This spawns the 'claude' CLI and sends a message, capturing the response.
        Used for dev mode to leverage user's Claude subscription.
        """
        try:
            # Run claude CLI with the message
            # Using --print flag for non-interactive mode
            result = await asyncio.create_subprocess_exec(
                "claude",
                "--print",
                "-p", user_message,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await result.communicate()

            if result.returncode != 0:
                logger.error(f"Claude CLI error: {stderr.decode()}")
                return "I'm having trouble connecting to Claude. Please check the CLI setup."

            return stdout.decode().strip()

        except FileNotFoundError:
            logger.error("Claude CLI not found in PATH")
            return "Claude CLI is not installed or not in PATH. Please install it first."
        except Exception as e:
            logger.error(f"Claude CLI error: {e}")
            return f"Error running Claude CLI: {type(e).__name__}"

    def _demo_response(self, user_message: str) -> str:
        """
        Generate a demo response when no API key is configured.

        Used for development/testing without API costs.
        """
        lower_msg = user_message.lower()

        if any(word in lower_msg for word in ["hello", "hi", "hey"]):
            return (
                "Hello! I'm the braidMgr assistant. I can help you with your project's "
                "RAID items - Risks, Actions, Issues, Decisions, and more. What would you like to know?"
            )

        if any(word in lower_msg for word in ["risk", "risks"]):
            return (
                "Risks in braidMgr are potential issues that could impact your project. "
                "I can help you analyze risk severity, suggest mitigation strategies, "
                "or review your current risk register. What would you like to explore?"
            )

        if any(word in lower_msg for word in ["action", "actions", "task"]):
            return (
                "Action items track work that needs to be done. I can help you "
                "prioritize actions, check on overdue items, or draft new action descriptions. "
                "What do you need help with?"
            )

        if any(word in lower_msg for word in ["issue", "issues", "problem"]):
            return (
                "Issues are problems that have occurred and need resolution. "
                "I can help analyze issue patterns, suggest resolutions, "
                "or help escalate critical issues. How can I assist?"
            )

        if any(word in lower_msg for word in ["status", "summary", "overview"]):
            return (
                "To give you a project status summary, I'd need to access your current "
                "project data. In the meantime, you can check the Dashboard view for "
                "item counts and the Active Items view for items needing attention."
            )

        # Default response for demo mode
        return (
            "[Demo Mode - No API key configured]\n\n"
            "I can help with project management topics like:\n"
            "- Analyzing risks and issues\n"
            "- Managing action items\n"
            "- Understanding project status\n"
            "- RAID log best practices\n\n"
            "To enable full AI responses, configure ANTHROPIC_API_KEY in your environment."
        )

    def clear_history(self):
        """Clear conversation history."""
        self._conversation_history = []

    def get_history(self) -> list[dict]:
        """Get conversation history."""
        return self._conversation_history.copy()


# =============================================================================
# Singleton Instance
# =============================================================================

_chat_service: Optional[ChatService] = None


def get_chat_service() -> ChatService:
    """Get the chat service singleton."""
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService()
    return _chat_service
