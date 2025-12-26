// =============================================================================
// Chat Context
// Provides shared chat state between drawer and command palette
// =============================================================================

import {
  createContext,
  useContext,
  useState,
  useCallback,
  type ReactNode,
} from "react"
import { useChat, type ChatMessage } from "@/hooks/useChat"

// =============================================================================
// Types
// =============================================================================

interface ChatContextValue {
  // State
  messages: ChatMessage[]
  isLoading: boolean
  isConnected: boolean
  error: string | null

  // UI state
  isDrawerOpen: boolean
  isCommandOpen: boolean

  // Actions
  sendMessage: (content: string) => void
  clearMessages: () => void
  connect: () => void
  disconnect: () => void

  // UI actions
  openDrawer: () => void
  closeDrawer: () => void
  toggleDrawer: () => void
  openCommand: () => void
  closeCommand: () => void
}

// =============================================================================
// Context
// =============================================================================

const ChatContext = createContext<ChatContextValue | null>(null)

// =============================================================================
// Provider
// =============================================================================

interface ChatProviderProps {
  children: ReactNode
}

export function ChatProvider({ children }: ChatProviderProps) {
  const chat = useChat()
  const [isDrawerOpen, setIsDrawerOpen] = useState(false)
  const [isCommandOpen, setIsCommandOpen] = useState(false)

  // Connect when opening chat UI
  const openDrawer = useCallback(() => {
    setIsDrawerOpen(true)
    if (!chat.isConnected) {
      chat.connect()
    }
  }, [chat])

  const closeDrawer = useCallback(() => {
    setIsDrawerOpen(false)
  }, [])

  const toggleDrawer = useCallback(() => {
    if (isDrawerOpen) {
      closeDrawer()
    } else {
      openDrawer()
    }
  }, [isDrawerOpen, openDrawer, closeDrawer])

  const openCommand = useCallback(() => {
    setIsCommandOpen(true)
    if (!chat.isConnected) {
      chat.connect()
    }
  }, [chat])

  const closeCommand = useCallback(() => {
    setIsCommandOpen(false)
  }, [])

  const value: ChatContextValue = {
    ...chat,
    isDrawerOpen,
    isCommandOpen,
    openDrawer,
    closeDrawer,
    toggleDrawer,
    openCommand,
    closeCommand,
  }

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>
}

// =============================================================================
// Hook
// =============================================================================

export function useChatContext() {
  const context = useContext(ChatContext)
  if (!context) {
    throw new Error("useChatContext must be used within a ChatProvider")
  }
  return context
}
