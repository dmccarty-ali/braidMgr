// =============================================================================
// ChatMessage Component
// Displays a single chat message with appropriate styling
// =============================================================================

import { memo } from "react"
import type { ChatMessage as ChatMessageType } from "@/hooks/useChat"
import { cn } from "@/lib/utils"

// =============================================================================
// Props
// =============================================================================

interface ChatMessageProps {
  message: ChatMessageType
}

// =============================================================================
// Component
// =============================================================================

export const ChatMessage = memo(function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user"
  const isSystem = message.role === "system"

  return (
    <div
      className={cn(
        "flex w-full",
        isUser ? "justify-end" : "justify-start"
      )}
    >
      <div
        className={cn(
          "max-w-[85%] rounded-lg px-4 py-2 text-sm",
          isUser
            ? "bg-primary text-primary-foreground"
            : isSystem
            ? "bg-muted text-muted-foreground italic"
            : "bg-muted text-foreground"
        )}
      >
        {/* Message content with basic markdown-like formatting */}
        <div className="whitespace-pre-wrap break-words">
          {message.content}
          {message.isStreaming && (
            <span className="inline-block w-2 h-4 ml-1 bg-current animate-pulse" />
          )}
        </div>

        {/* Timestamp */}
        <div
          className={cn(
            "text-[10px] mt-1 opacity-60",
            isUser ? "text-right" : "text-left"
          )}
        >
          {message.timestamp.toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          })}
        </div>
      </div>
    </div>
  )
})
