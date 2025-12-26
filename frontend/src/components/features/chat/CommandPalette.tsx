// =============================================================================
// CommandPalette Component
// Cmd+K interface for quick chat access and actions
// =============================================================================

import { useEffect, useRef, useState, type KeyboardEvent } from "react"
import { useNavigate, useParams } from "react-router-dom"
import { useChatContext } from "./ChatContext"
import { ChatMessage } from "./ChatMessage"

// =============================================================================
// Quick Actions
// =============================================================================

interface QuickAction {
  id: string
  label: string
  description: string
  icon: React.ReactNode
  action: () => void
  keywords: string[]
}

// =============================================================================
// Component
// =============================================================================

export function CommandPalette() {
  const navigate = useNavigate()
  const { projectId } = useParams<{ projectId: string }>()
  const {
    messages,
    isLoading,
    isCommandOpen,
    sendMessage,
    openCommand,
    closeCommand,
    openDrawer,
  } = useChatContext()

  const [query, setQuery] = useState("")
  const [mode, setMode] = useState<"search" | "chat">("search")
  const inputRef = useRef<HTMLInputElement>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Define quick actions
  const quickActions: QuickAction[] = projectId
    ? [
        {
          id: "dashboard",
          label: "Go to Dashboard",
          description: "View project summary",
          icon: (
            <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
            </svg>
          ),
          action: () => navigate(`/projects/${projectId}/dashboard`),
          keywords: ["dashboard", "home", "summary", "overview"],
        },
        {
          id: "items",
          label: "Go to All Items",
          description: "View and filter all items",
          icon: (
            <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 10h16M4 14h16M4 18h16" />
            </svg>
          ),
          action: () => navigate(`/projects/${projectId}/items`),
          keywords: ["items", "list", "all", "table"],
        },
        {
          id: "active",
          label: "Go to Active Items",
          description: "View items needing attention",
          icon: (
            <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          ),
          action: () => navigate(`/projects/${projectId}/active`),
          keywords: ["active", "urgent", "attention", "alerts"],
        },
        {
          id: "timeline",
          label: "Go to Timeline",
          description: "Gantt chart view",
          icon: (
            <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          ),
          action: () => navigate(`/projects/${projectId}/timeline`),
          keywords: ["timeline", "gantt", "schedule", "dates"],
        },
        {
          id: "chat",
          label: "Open Chat",
          description: "Ask Claude a question",
          icon: (
            <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
          ),
          action: () => {
            closeCommand()
            openDrawer()
          },
          keywords: ["chat", "ask", "claude", "ai", "help"],
        },
      ]
    : []

  // Filter actions based on query
  const filteredActions = quickActions.filter((action) => {
    if (!query.trim()) return true
    const lowerQuery = query.toLowerCase()
    return (
      action.label.toLowerCase().includes(lowerQuery) ||
      action.description.toLowerCase().includes(lowerQuery) ||
      action.keywords.some((kw) => kw.includes(lowerQuery))
    )
  })

  // Handle keyboard shortcut to open
  useEffect(() => {
    const handleKeyDown = (e: globalThis.KeyboardEvent) => {
      // Cmd+K or Ctrl+K to open
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault()
        if (isCommandOpen) {
          closeCommand()
        } else {
          openCommand()
          setMode("search")
          setQuery("")
        }
      }

      // Escape to close
      if (e.key === "Escape" && isCommandOpen) {
        closeCommand()
      }
    }

    document.addEventListener("keydown", handleKeyDown)
    return () => document.removeEventListener("keydown", handleKeyDown)
  }, [isCommandOpen, openCommand, closeCommand])

  // Focus input when opened
  useEffect(() => {
    if (isCommandOpen && inputRef.current) {
      inputRef.current.focus()
    }
  }, [isCommandOpen])

  // Scroll to bottom when in chat mode
  useEffect(() => {
    if (mode === "chat") {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
    }
  }, [messages, mode])

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && query.trim()) {
      if (mode === "search") {
        // If query starts with >, switch to chat mode
        if (query.startsWith(">")) {
          setMode("chat")
          const message = query.slice(1).trim()
          if (message) {
            sendMessage(message)
            setQuery("")
          } else {
            setQuery("")
          }
        } else if (filteredActions.length > 0 && filteredActions[0]) {
          // Execute first matching action
          filteredActions[0].action()
          closeCommand()
        } else {
          // No matching action, switch to chat mode
          setMode("chat")
          sendMessage(query)
          setQuery("")
        }
      } else {
        // Chat mode - send message
        sendMessage(query)
        setQuery("")
      }
    }
  }

  if (!isCommandOpen) return null

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 z-50 bg-black/50"
        onClick={closeCommand}
      />

      {/* Command palette */}
      <div className="fixed inset-x-0 top-[20%] z-50 mx-auto w-full max-w-xl px-4">
        <div className="overflow-hidden rounded-xl border bg-background shadow-2xl">
          {/* Input area */}
          <div className="flex items-center border-b px-4">
            {mode === "chat" ? (
              <button
                onClick={() => setMode("search")}
                className="mr-2 text-muted-foreground hover:text-foreground"
                title="Back to search"
              >
                <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
              </button>
            ) : (
              <svg
                className="mr-2 h-4 w-4 shrink-0 text-muted-foreground"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                />
              </svg>
            )}
            <input
              ref={inputRef}
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={
                mode === "chat"
                  ? "Ask Claude..."
                  : "Search or type > to chat..."
              }
              className="flex-1 bg-transparent py-4 text-sm outline-none placeholder:text-muted-foreground"
            />
            {isLoading && (
              <svg
                className="ml-2 h-4 w-4 animate-spin text-muted-foreground"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                />
              </svg>
            )}
          </div>

          {/* Content area */}
          {mode === "search" ? (
            // Quick actions list
            <div className="max-h-80 overflow-y-auto p-2">
              {filteredActions.length === 0 ? (
                <div className="px-4 py-8 text-center text-sm text-muted-foreground">
                  No results found. Press Enter to ask Claude.
                </div>
              ) : (
                <div className="space-y-1">
                  {filteredActions.map((action) => (
                    <button
                      key={action.id}
                      onClick={() => {
                        action.action()
                        closeCommand()
                      }}
                      className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-left text-sm hover:bg-muted"
                    >
                      <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-muted text-muted-foreground">
                        {action.icon}
                      </span>
                      <div className="flex-1 overflow-hidden">
                        <div className="font-medium">{action.label}</div>
                        <div className="truncate text-xs text-muted-foreground">
                          {action.description}
                        </div>
                      </div>
                    </button>
                  ))}
                </div>
              )}

              {/* Hint */}
              <div className="mt-2 border-t px-4 py-2 text-xs text-muted-foreground">
                Type <kbd className="rounded bg-muted px-1 font-mono">&gt;</kbd> to start chatting
              </div>
            </div>
          ) : (
            // Chat mode
            <div className="flex flex-col">
              <div className="max-h-80 overflow-y-auto p-4">
                {messages.length === 0 ? (
                  <div className="py-4 text-center text-sm text-muted-foreground">
                    Ask me anything about your project!
                  </div>
                ) : (
                  <div className="space-y-3">
                    {messages.slice(-6).map((message) => (
                      <ChatMessage key={message.id} message={message} />
                    ))}
                    <div ref={messagesEndRef} />
                  </div>
                )}
              </div>

              {/* Mode hint */}
              <div className="border-t px-4 py-2 text-xs text-muted-foreground">
                Press Enter to send. Click arrow or Esc to go back.
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  )
}
