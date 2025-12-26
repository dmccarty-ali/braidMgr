// =============================================================================
// Chat State Hook
// Manages chat messages and connection to Claude backend
// =============================================================================

import { useState, useCallback, useRef, useEffect } from "react"

// =============================================================================
// Types
// =============================================================================

export interface ChatMessage {
  id: string
  role: "user" | "assistant" | "system"
  content: string
  timestamp: Date
  // For streaming responses
  isStreaming?: boolean
}

export interface ChatState {
  messages: ChatMessage[]
  isConnected: boolean
  isLoading: boolean
  error: string | null
}

// =============================================================================
// Hook
// =============================================================================

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // WebSocket ref for real-time communication with backend
  const wsRef = useRef<WebSocket | null>(null)
  const [isConnected, setIsConnected] = useState(false)

  // Generate unique ID for messages
  const generateId = () => `msg-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`

  // Connect to backend WebSocket
  const connect = useCallback(() => {
    // Determine WebSocket URL based on current location
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:"
    const host = window.location.host
    const wsUrl = `${protocol}//${host}/api/chat/ws`

    try {
      const ws = new WebSocket(wsUrl)

      ws.onopen = () => {
        setIsConnected(true)
        setError(null)
        console.log("Chat WebSocket connected")
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)

          if (data.type === "message") {
            // Complete message received
            setMessages((prev) => {
              // Check if we're updating a streaming message
              const streamingIdx = prev.findIndex(
                (m) => m.role === "assistant" && m.isStreaming
              )
              if (streamingIdx >= 0 && prev[streamingIdx]) {
                const updated = [...prev]
                const existing = prev[streamingIdx]!
                updated[streamingIdx] = {
                  ...existing,
                  content: data.content,
                  isStreaming: false,
                }
                return updated
              }
              // New message
              return [
                ...prev,
                {
                  id: data.id || generateId(),
                  role: "assistant",
                  content: data.content,
                  timestamp: new Date(),
                  isStreaming: false,
                },
              ]
            })
            setIsLoading(false)
          } else if (data.type === "stream") {
            // Streaming chunk
            setMessages((prev) => {
              const streamingIdx = prev.findIndex(
                (m) => m.role === "assistant" && m.isStreaming
              )
              if (streamingIdx >= 0 && prev[streamingIdx]) {
                const updated = [...prev]
                const existing = prev[streamingIdx]!
                updated[streamingIdx] = {
                  ...existing,
                  content: existing.content + data.content,
                }
                return updated
              }
              // Start new streaming message
              return [
                ...prev,
                {
                  id: generateId(),
                  role: "assistant",
                  content: data.content,
                  timestamp: new Date(),
                  isStreaming: true,
                },
              ]
            })
          } else if (data.type === "error") {
            setError(data.message)
            setIsLoading(false)
          }
        } catch {
          console.error("Failed to parse WebSocket message")
        }
      }

      ws.onerror = () => {
        setError("Connection error")
        setIsConnected(false)
      }

      ws.onclose = () => {
        setIsConnected(false)
        console.log("Chat WebSocket disconnected")
      }

      wsRef.current = ws
    } catch (err) {
      setError("Failed to connect")
      setIsConnected(false)
    }
  }, [])

  // Disconnect WebSocket
  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }
  }, [])

  // Send a message
  const sendMessage = useCallback(
    async (content: string) => {
      if (!content.trim()) return

      // Add user message immediately
      const userMessage: ChatMessage = {
        id: generateId(),
        role: "user",
        content: content.trim(),
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, userMessage])
      setIsLoading(true)
      setError(null)

      // If WebSocket is connected, use it
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(
          JSON.stringify({
            type: "message",
            content: content.trim(),
          })
        )
        return
      }

      // Fallback to REST API
      try {
        const response = await fetch(`/api/chat/message`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ message: content.trim() }),
        })

        if (!response.ok) {
          throw new Error("Failed to send message")
        }

        const data = await response.json()
        setMessages((prev) => [
          ...prev,
          {
            id: data.id || generateId(),
            role: "assistant",
            content: data.content,
            timestamp: new Date(),
          },
        ])
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to send message")
      } finally {
        setIsLoading(false)
      }
    },
    []
  )

  // Clear chat history
  const clearMessages = useCallback(() => {
    setMessages([])
    setError(null)
  }, [])

  // Auto-connect on mount (optional - can be triggered manually)
  useEffect(() => {
    // Don't auto-connect; let the UI trigger it when chat is opened
    return () => {
      disconnect()
    }
  }, [disconnect])

  return {
    messages,
    isLoading,
    isConnected,
    error,
    sendMessage,
    clearMessages,
    connect,
    disconnect,
  }
}
