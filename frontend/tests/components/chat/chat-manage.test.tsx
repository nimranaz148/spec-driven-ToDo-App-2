"""Frontend tests for chat task management components."""

import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import ChatFeed from '@/components/chat/chat-feed'
import { useChatStore } from '@/stores/chat-store'

// Mock the chat store
vi.mock('@/stores/chat-store')

const mockUseChatStore = vi.mocked(useChatStore)

describe('ChatFeed - Task Management', () => {
  const mockMessages = [
    {
      id: '1',
      role: 'user',
      content: 'What are my tasks?',
      timestamp: new Date(),
    },
    {
      id: '2',
      role: 'assistant',
      content: 'You have 2 tasks: Buy groceries (pending), Walk dog (completed)',
      timestamp: new Date(),
      tool_calls: [
        {
          tool: 'list_tasks',
          result: [
            { id: 1, title: 'Buy groceries', completed: false },
            { id: 2, title: 'Walk dog', completed: true },
          ],
        },
      ],
    },
    {
      id: '3',
      role: 'user',
      content: 'Mark task 1 as complete',
      timestamp: new Date(),
    },
    {
      id: '4',
      role: 'assistant',
      content: 'Task "Buy groceries" has been marked as completed!',
      timestamp: new Date(),
      tool_calls: [
        {
          tool: 'complete_task',
          task_id: 1,
          result: 'success',
        },
      ],
    },
  ]

  beforeEach(() => {
    mockUseChatStore.mockReturnValue({
      messages: mockMessages,
      isLoading: false,
      sendMessage: vi.fn(),
      clearMessages: vi.fn(),
    })
  })

  it('renders task completion status updates in chat bubbles', () => {
    render(<ChatFeed />)

    // Check that task list is displayed
    expect(screen.getByText(/You have 2 tasks/)).toBeInTheDocument()
    expect(screen.getByText(/Buy groceries \(pending\)/)).toBeInTheDocument()
    expect(screen.getByText(/Walk dog \(completed\)/)).toBeInTheDocument()

    // Check that completion confirmation is displayed
    expect(screen.getByText(/has been marked as completed/)).toBeInTheDocument()
  })

  it('displays tool call results with proper formatting', () => {
    render(<ChatFeed />)

    // Check for tool call indicators
    const toolCallElements = screen.getAllByTestId(/tool-call/)
    expect(toolCallElements).toHaveLength(2)

    // Check list_tasks tool call
    expect(screen.getByText('list_tasks')).toBeInTheDocument()
    
    // Check complete_task tool call
    expect(screen.getByText('complete_task')).toBeInTheDocument()
  })

  it('handles task status updates in real-time', async () => {
    const mockSendMessage = vi.fn()
    mockUseChatStore.mockReturnValue({
      messages: mockMessages.slice(0, 2), // Only initial messages
      isLoading: false,
      sendMessage: mockSendMessage,
      clearMessages: vi.fn(),
    })

    render(<ChatFeed />)

    // Simulate sending a completion message
    const input = screen.getByPlaceholderText(/Type your message/)
    const sendButton = screen.getByRole('button', { name: /send/i })

    fireEvent.change(input, { target: { value: 'Mark task 1 as complete' } })
    fireEvent.click(sendButton)

    expect(mockSendMessage).toHaveBeenCalledWith('Mark task 1 as complete')
  })

  it('shows loading state during task operations', () => {
    mockUseChatStore.mockReturnValue({
      messages: mockMessages,
      isLoading: true,
      sendMessage: vi.fn(),
      clearMessages: vi.fn(),
    })

    render(<ChatFeed />)

    expect(screen.getByTestId('loading-indicator')).toBeInTheDocument()
  })

  it('displays error states for failed task operations', () => {
    const errorMessages = [
      ...mockMessages,
      {
        id: '5',
        role: 'assistant',
        content: 'Sorry, I could not complete that task. Please try again.',
        timestamp: new Date(),
        error: true,
      },
    ]

    mockUseChatStore.mockReturnValue({
      messages: errorMessages,
      isLoading: false,
      sendMessage: vi.fn(),
      clearMessages: vi.fn(),
    })

    render(<ChatFeed />)

    expect(screen.getByText(/could not complete that task/)).toBeInTheDocument()
    expect(screen.getByTestId('error-message')).toBeInTheDocument()
  })
})
