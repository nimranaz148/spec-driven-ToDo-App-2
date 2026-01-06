"""Error handling components for chat UI."""

import React from 'react'
import { AlertCircle, RefreshCw, Wifi, WifiOff } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'

interface ChatErrorProps {
  error: string | null
  onRetry?: () => void
  onClear?: () => void
}

export function ChatError({ error, onRetry, onClear }: ChatErrorProps) {
  if (!error) return null

  const getErrorType = (errorMessage: string) => {
    if (errorMessage.includes('network') || errorMessage.includes('fetch')) {
      return 'network'
    }
    if (errorMessage.includes('rate limit') || errorMessage.includes('429')) {
      return 'rate_limit'
    }
    if (errorMessage.includes('authentication') || errorMessage.includes('401')) {
      return 'auth'
    }
    return 'general'
  }

  const errorType = getErrorType(error.toLowerCase())

  const getErrorIcon = () => {
    switch (errorType) {
      case 'network':
        return <WifiOff className="h-4 w-4" />
      case 'rate_limit':
        return <AlertCircle className="h-4 w-4" />
      default:
        return <AlertCircle className="h-4 w-4" />
    }
  }

  const getErrorMessage = () => {
    switch (errorType) {
      case 'network':
        return 'Connection lost. Please check your internet connection and try again.'
      case 'rate_limit':
        return 'You\'re sending messages too quickly. Please wait a moment before trying again.'
      case 'auth':
        return 'Your session has expired. Please refresh the page and log in again.'
      default:
        return error
    }
  }

  const getRetryText = () => {
    switch (errorType) {
      case 'network':
        return 'Retry Connection'
      case 'rate_limit':
        return 'Try Again'
      default:
        return 'Retry'
    }
  }

  return (
    <Alert variant="destructive" className="mb-4">
      <div className="flex items-start gap-3">
        {getErrorIcon()}
        <div className="flex-1">
          <AlertDescription className="text-sm">
            {getErrorMessage()}
          </AlertDescription>
          <div className="flex gap-2 mt-3">
            {onRetry && (
              <Button
                variant="outline"
                size="sm"
                onClick={onRetry}
                className="h-8 px-3 text-xs"
              >
                <RefreshCw className="h-3 w-3 mr-1" />
                {getRetryText()}
              </Button>
            )}
            {onClear && (
              <Button
                variant="ghost"
                size="sm"
                onClick={onClear}
                className="h-8 px-3 text-xs"
              >
                Dismiss
              </Button>
            )}
          </div>
        </div>
      </div>
    </Alert>
  )
}

interface ConnectionStatusProps {
  isConnected: boolean
  isReconnecting?: boolean
}

export function ConnectionStatus({ isConnected, isReconnecting }: ConnectionStatusProps) {
  if (isConnected && !isReconnecting) return null

  return (
    <div className="flex items-center gap-2 px-3 py-2 bg-muted/50 border-b text-sm text-muted-foreground">
      {isReconnecting ? (
        <>
          <RefreshCw className="h-3 w-3 animate-spin" />
          Reconnecting...
        </>
      ) : (
        <>
          <WifiOff className="h-3 w-3" />
          Connection lost
        </>
      )}
    </div>
  )
}

interface RetryGuidanceProps {
  errorType: 'network' | 'rate_limit' | 'server' | 'auth'
  onRetry?: () => void
}

export function RetryGuidance({ errorType, onRetry }: RetryGuidanceProps) {
  const getGuidance = () => {
    switch (errorType) {
      case 'network':
        return {
          title: 'Connection Issues',
          message: 'Check your internet connection and try again.',
          action: 'Retry Connection'
        }
      case 'rate_limit':
        return {
          title: 'Slow Down',
          message: 'You\'re sending messages too quickly. Wait a moment before continuing.',
          action: 'Try Again'
        }
      case 'server':
        return {
          title: 'Server Error',
          message: 'Something went wrong on our end. Please try again in a moment.',
          action: 'Retry'
        }
      case 'auth':
        return {
          title: 'Session Expired',
          message: 'Please refresh the page and log in again.',
          action: 'Refresh Page'
        }
    }
  }

  const guidance = getGuidance()

  const handleAction = () => {
    if (errorType === 'auth') {
      window.location.reload()
    } else if (onRetry) {
      onRetry()
    }
  }

  return (
    <div className="flex flex-col items-center gap-4 py-8 text-center">
      <div className="p-3 rounded-full bg-muted">
        <AlertCircle className="h-6 w-6 text-muted-foreground" />
      </div>
      <div>
        <h3 className="font-medium text-sm">{guidance.title}</h3>
        <p className="text-xs text-muted-foreground mt-1">{guidance.message}</p>
      </div>
      <Button
        variant="outline"
        size="sm"
        onClick={handleAction}
        className="h-8 px-4 text-xs"
      >
        <RefreshCw className="h-3 w-3 mr-1" />
        {guidance.action}
      </Button>
    </div>
  )
}

// Hook for handling chat errors with retry logic
export function useChatErrorHandler() {
  const [retryCount, setRetryCount] = React.useState(0)
  const [lastError, setLastError] = React.useState<string | null>(null)

  const handleError = React.useCallback((error: string) => {
    setLastError(error)
    setRetryCount(prev => prev + 1)
  }, [])

  const clearError = React.useCallback(() => {
    setLastError(null)
    setRetryCount(0)
  }, [])

  const shouldShowRetry = retryCount < 3 // Max 3 retries

  return {
    error: lastError,
    retryCount,
    shouldShowRetry,
    handleError,
    clearError
  }
}
