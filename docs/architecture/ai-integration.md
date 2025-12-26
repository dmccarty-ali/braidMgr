# AI Integration

*Parent: [ARCHITECTURE.md](../ARCHITECTURE.md)*
*Last updated: 2025-12-26*

Claude API integration for natural language project queries.

**Key Concepts**:
- System prompt enforcement for governance (restricts to project topics)
- WebSocket streaming for real-time responses
- REST fallback for compatibility
- Usage logging for audit
- Demo mode when no API key configured

---

## Current Implementation

### Chat Service

Located at `backend/src/services/chat_service.py`:

```python
class ChatService:
    """
    Service for AI chat functionality.

    Supports two modes:
    - API mode (default): Uses Anthropic Python SDK
    - CLI mode: Spawns Claude CLI subprocess (for dev with subscription)
    """

    async def send_message(self, user_message: str, ...) -> ChatMessage:
        """Send message and get response."""

    async def stream_message(self, user_message: str, ...) -> AsyncGenerator[str, None]:
        """Stream response chunk by chunk."""
```

### System Prompt (Governance)

The system prompt restricts Claude to project management topics:

```python
SYSTEM_PROMPT = """You are Claude, an AI assistant embedded in braidMgr...

Your role is to help users with:
- Understanding their project status and items
- Analyzing risks, issues, and action items
- Providing project management guidance
- Answering questions about RAID log best practices

Guidelines:
1. Stay focused on project management topics
2. If asked about unrelated topics (personal shopping, entertainment, etc.),
   politely redirect to project-related assistance
...
"""
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chat/message` | POST | Send message, get response |
| `/api/chat/ws` | WebSocket | Streaming chat connection |
| `/api/chat/history` | GET | Get conversation history |
| `/api/chat/history` | DELETE | Clear conversation |

### WebSocket Protocol

```typescript
// Client -> Server
{ "type": "message", "content": "user message" }

// Server -> Client (streaming)
{ "type": "stream", "content": "chunk" }

// Server -> Client (complete)
{ "type": "message", "id": "...", "content": "full response" }

// Server -> Client (error)
{ "type": "error", "message": "error description" }
```

---

## Frontend Components

Located at `frontend/src/components/features/chat/`:

| Component | Description |
|-----------|-------------|
| ChatContext | Shared state provider for drawer and command palette |
| ChatDrawer | Floating button (bottom-right) + slide-out panel |
| CommandPalette | Cmd+K interface with search and chat modes |
| ChatMessage | Message bubble with timestamp |
| ChatInput | Textarea with send button |

### Usage

```tsx
// App.tsx - wrapped in ProjectLayout
<ChatProvider>
  <AppLayout>...</AppLayout>
  <ChatDrawer />
  <CommandPalette />
</ChatProvider>
```

---

## Configuration

### Environment Variables

| Variable | Description |
|----------|-------------|
| `CHAT_MODE` | `cli` (local dev) or `api` (cloud/production) |
| `ANTHROPIC_API_KEY` | Required for `api` mode only |

### Local Development vs Cloud

| Environment | CHAT_MODE | How It Works |
|-------------|-----------|--------------|
| **Local dev** | `cli` | Uses `claude` CLI - leverages your Claude subscription |
| **Cloud/Production** | `api` | Uses Anthropic API with `ANTHROPIC_API_KEY` |
| **Docker** | `api` | CLI not available in container; use API or demo mode |

### Setup for Local Development

Copy the example environment file:

```bash
cd backend
cp .env.example .env
source .env
```

The `.env.example` file includes `CHAT_MODE=cli` for local development.

Or set inline when starting the backend:

```bash
CHAT_MODE=cli uvicorn src.api.main:app --reload
```

### Config in `config.yaml`

```yaml
integrations:
  anthropic:
    api_key: ${ANTHROPIC_API_KEY:-}
    model: claude-3-5-sonnet-20241022
```

---

## Demo Mode

When no API key is configured, the chat service returns canned responses:

```python
def _demo_response(self, user_message: str) -> str:
    """Generate demo response when no API key configured."""
    if "risk" in user_message.lower():
        return "Risks in braidMgr are potential issues..."
    # ... other demo responses
    return "[Demo Mode - No API key configured]..."
```

---

## Context Building

```python
async def build_project_context(
    project_id: UUID,
    user_id: UUID
) -> ProjectContext:
    """Build AI context from project data."""
    # Get project (already permission-checked)
    project = await project_repo.get(project_id)

    # Get items (respects user's view permissions)
    items = await item_repo.get_by_project(project_id)

    # Calculate budget metrics
    budget = await budget_service.calculate(project_id)

    # Format for AI consumption
    summary = format_for_ai(project, items, budget)

    return ProjectContext(
        project=project,
        items=items,
        budget_metrics=budget,
        summary=summary
    )


def format_for_ai(
    project: Project,
    items: list[Item],
    budget: BudgetMetrics
) -> str:
    """Format project data for AI context."""
    sections = []

    # Summary counts
    counts = Counter(item.type for item in items)
    sections.append("ITEM COUNTS:")
    for item_type, count in counts.items():
        sections.append(f"  {item_type}: {count}")

    # Status summary
    open_items = [i for i in items if i.indicator != 'Completed']
    critical = [i for i in open_items if 'Late' in (i.indicator or '')]
    sections.append(f"\nOPEN ITEMS: {len(open_items)}")
    sections.append(f"CRITICAL (Late): {len(critical)}")

    # Budget summary
    if budget.total_budget:
        remaining = budget.total_budget - budget.actual_spend
        sections.append(f"\nBUDGET: ${budget.total_budget:,.0f}")
        sections.append(f"SPENT: ${budget.actual_spend:,.0f}")
        sections.append(f"REMAINING: ${remaining:,.0f}")

    # Active risks
    risks = [i for i in items if i.type == 'Risk' and i.indicator != 'Completed']
    if risks:
        sections.append("\nACTIVE RISKS:")
        for risk in risks[:5]:
            sections.append(f"  #{risk.item_num}: {risk.title}")

    # Overdue actions
    overdue = [i for i in items
               if i.type == 'Action Item'
               and 'Late' in (i.indicator or '')]
    if overdue:
        sections.append("\nOVERDUE ACTIONS:")
        for action in overdue[:5]:
            sections.append(f"  #{action.item_num}: {action.title}")

    return "\n".join(sections)
```

---

## RBAC Enforcement

AI only accesses data the user has permission to view:

```python
@router.post("/chat/sessions/{session_id}/messages")
async def send_chat_message(
    session_id: UUID,
    request: ChatMessageRequest,
    current_user: User = Depends(get_current_user)
):
    # Get session (validates ownership)
    session = await chat_repo.get_session(session_id, current_user.id)

    # Build context with user's permissions
    if session.project_id:
        # Verify user has access to project
        await check_permission(
            current_user.id,
            session.project_id,
            Permission.VIEW_ITEMS
        )
        context = await build_project_context(
            session.project_id,
            current_user.id
        )
    else:
        # Org-wide context - include all user's accessible projects
        context = await build_org_context(
            current_user.org_id,
            current_user.id
        )

    # Send to Claude
    response = await services.claude.send_message(
        messages=request.messages,
        context=context
    )

    return ChatMessageResponse(content=response)
```

---

## Scope Expansion

Default context is current project. Users can expand by asking:

| User Query | Scope |
|------------|-------|
| "What are the open risks?" | Current project |
| "Show me overdue items" | Current project |
| "Across all my projects, what's overdue?" | All accessible projects |
| "Compare budgets across projects" | All accessible projects |

```python
def detect_scope_expansion(message: str) -> bool:
    """Detect if user wants cross-project query."""
    patterns = [
        "across all",
        "all projects",
        "all my projects",
        "every project",
        "compare projects",
        "portfolio",
    ]
    message_lower = message.lower()
    return any(pattern in message_lower for pattern in patterns)
```

---

## Chat Session Storage

```python
# Store session and messages for continuity
@dataclass
class ChatSession:
    id: UUID
    user_id: UUID
    project_id: UUID | None  # None = org-wide
    title: str | None
    created_at: datetime
    updated_at: datetime

@dataclass
class ChatMessage:
    id: UUID
    session_id: UUID
    role: str  # user, assistant, system
    content: str
    context_refs: dict | None  # Referenced items
    token_count: int | None
    created_at: datetime
```

---

## Token Usage Tracking

```python
async def track_token_usage(
    session_id: UUID,
    input_tokens: int,
    output_tokens: int
):
    """Track API usage for cost monitoring."""
    await services.aurora.execute_returning(
        pool,
        """
        INSERT INTO token_usage (session_id, input_tokens, output_tokens, created_at)
        VALUES ($1, $2, $3, NOW())
        RETURNING id
        """,
        session_id, input_tokens, output_tokens
    )

# Monthly usage report
async def get_monthly_usage(org_id: UUID) -> TokenUsage:
    """Get token usage for billing."""
    ...
```
