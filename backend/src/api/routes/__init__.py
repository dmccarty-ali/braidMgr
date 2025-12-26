"""
API routes for braidMgr backend.

Exports:
    health: Health check and root endpoints
    auth: Authentication endpoints
    projects: Project management endpoints
    items: Item CRUD endpoints
    workstreams: Workstream management endpoints
    chat: AI chat endpoints with WebSocket support
    activity: Activity feed and audit log endpoints
"""

from src.api.routes import health
from src.api.routes import auth
from src.api.routes import projects
from src.api.routes import items
from src.api.routes import workstreams
from src.api.routes import chat
from src.api.routes import activity

__all__ = ["health", "auth", "projects", "items", "workstreams", "chat", "activity"]
