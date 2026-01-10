'use client';

/**
 * ChatKit-style UI Components
 */

import React, { useState, useRef, useEffect, memo } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { cn } from '@/lib/utils';
import {
  Bot,
  User,
  Loader2,
  CheckCircle2,
  AlertCircle,
  Brain,
  ChevronDown,
  ChevronRight,
  Wrench,
  Clock,
  Zap,
  Send,
  Sparkles,
  AlertTriangle,
  X,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import type { ThinkingStep, ToolCall, ConfirmationRequest } from '@/lib/types';

// ============================================================================
// Types
// ============================================================================

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  isStreaming?: boolean;
  isOptimistic?: boolean;
  thinkingSteps?: ThinkingStep[];
  toolCalls?: ToolCall[];
  processingTimeMs?: number;
}

export interface ChatKitProps {
  messages: ChatMessage[];
  isLoading?: boolean;
  isTyping?: boolean;
  error?: string | null;
  pendingConfirmation?: ConfirmationRequest | null;
  userAvatar?: string;
  assistantName?: string;
  assistantAvatar?: string;
  onSendMessage: (message: string) => void;
  onConfirm?: () => void;
  onCancel?: () => void;
  placeholder?: string;
  suggestedPrompts?: string[];
  className?: string;
}

// ============================================================================
// Sub-components
// ============================================================================

const ThinkingIcon = ({ type }: { type: ThinkingStep['type'] }) => {
  const icons = {
    analyzing: <Brain className="h-3 w-3 text-blue-500" />,
    planning: <Clock className="h-3 w-3 text-purple-500" />,
    tool_call: <Wrench className="h-3 w-3 text-orange-500" />,
    processing: <Zap className="h-3 w-3 text-yellow-500" />,
    clarifying: <AlertTriangle className="h-3 w-3 text-amber-500" />,
  };
  return icons[type] || <Brain className="h-3 w-3" />;
};

const ThinkingStepsPanel = ({
  steps,
  processingTimeMs,
  isExpanded,
  onToggle
}: {
  steps: ThinkingStep[];
  processingTimeMs?: number;
  isExpanded: boolean;
  onToggle: () => void;
}) => {
  if (!steps.length) return null;

  return (
    <div className="mt-3 rounded-lg bg-gradient-to-r from-blue-500/5 to-purple-500/5 border border-blue-500/10">
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between p-2 text-xs hover:bg-white/5 transition-colors rounded-lg"
      >
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1">
            <Brain className="h-3.5 w-3.5 text-blue-500" />
            <span className="font-medium text-foreground/80">Agent Reasoning</span>
          </div>
          <span className="text-muted-foreground">({steps.length} steps)</span>
        </div>
        <div className="flex items-center gap-2">
          {processingTimeMs && (
            <span className="text-muted-foreground/60 text-[10px]">
              {processingTimeMs}ms
            </span>
          )}
          {isExpanded ? (
            <ChevronDown className="h-3.5 w-3.5 text-muted-foreground" />
          ) : (
            <ChevronRight className="h-3.5 w-3.5 text-muted-foreground" />
          )}
        </div>
      </button>

      {isExpanded && (
        <div className="px-3 pb-3 space-y-2">
          {steps.map((step, idx) => (
            <div
              key={idx}
              className="flex items-start gap-2 text-xs animate-in fade-in slide-in-from-top-1"
              style={{ animationDelay: `${idx * 50}ms` }}
            >
              <div className="mt-0.5 p-1 rounded bg-background/50">
                <ThinkingIcon type={step.type} />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-foreground/70 leading-relaxed">{step.content}</p>
                {step.timestamp !== undefined && (
                  <span className="text-muted-foreground/50 text-[10px]">
                    +{step.timestamp.toFixed(2)}s
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

const ToolCallsPanel = ({ toolCalls }: { toolCalls: ToolCall[] }) => {
  if (!toolCalls.length) return null;

  return (
    <div className="mt-3 rounded-lg bg-gradient-to-r from-green-500/5 to-emerald-500/5 border border-green-500/10 p-3">
      <div className="flex items-center gap-2 mb-2">
        <Wrench className="h-3.5 w-3.5 text-green-500" />
        <span className="text-xs font-medium text-foreground/80">Actions Executed</span>
      </div>
      <div className="space-y-1.5">
        {toolCalls.map((tc, idx) => (
          <div
            key={idx}
            className="flex items-center gap-2 text-xs bg-background/30 rounded px-2 py-1.5"
          >
            {tc.result.success ? (
              <CheckCircle2 className="h-3.5 w-3.5 text-green-500 shrink-0" />
            ) : (
              <AlertCircle className="h-3.5 w-3.5 text-red-500 shrink-0" />
            )}
            <code className="font-mono text-foreground/80">{tc.tool}</code>
            {tc.result.id && (
              <span className="text-primary font-medium">#{tc.result.id}</span>
            )}
            {tc.duration_ms && (
              <span className="text-muted-foreground/50 ml-auto">
                {tc.duration_ms}ms
              </span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

const MessageBubble = ({
  message,
  userAvatar,
  assistantName,
  assistantAvatar,
}: {
  message: ChatMessage;
  userAvatar?: string;
  assistantName?: string;
  assistantAvatar?: string;
}) => {
  const [isThinkingExpanded, setIsThinkingExpanded] = useState(false);
  const isUser = message.role === 'user';

  return (
    <div
      className={cn(
        'flex gap-3 animate-in fade-in slide-in-from-bottom-2',
        isUser && 'flex-row-reverse'
      )}
    >
      <Avatar className={cn('h-8 w-8 shrink-0 ring-2 ring-background shadow-md', isUser ? 'ring-primary/20' : 'ring-blue-500/20')}>
        {isUser ? (
          <>
            <AvatarImage src={userAvatar} />
            <AvatarFallback className="bg-primary/10 text-primary">
              <User className="h-4 w-4" />
            </AvatarFallback>
          </>
        ) : (
          <>
            <AvatarImage src={assistantAvatar} />
            <AvatarFallback className="bg-gradient-to-br from-blue-500 to-purple-600 text-white">
              <Bot className="h-4 w-4" />
            </AvatarFallback>
          </>
        )}
      </Avatar>

      <div className={cn('flex-1 max-w-[85%]', isUser && 'flex flex-col items-end')}>
        {!isUser && assistantName && (
          <span className="text-xs font-medium text-muted-foreground mb-1 ml-1">
            {assistantName}
          </span>
        )}

        <div
          className={cn(
            'rounded-2xl px-4 py-3 shadow-sm',
            isUser
              ? 'bg-primary text-primary-foreground rounded-tr-md'
              : 'bg-muted/80 backdrop-blur-sm rounded-tl-md',
            message.isOptimistic && 'opacity-70',
            message.isStreaming && 'animate-pulse'
          )}
        >
          {isUser ? (
            <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
          ) : (
            <MarkdownContent content={message.content} />
          )}
          {message.isStreaming && (
            <span className="inline-block w-1.5 h-4 ml-1 bg-current animate-pulse rounded" />
          )}
        </div>

        {/* Thinking Steps */}
        {!isUser && message.thinkingSteps && message.thinkingSteps.length > 0 && (
          <ThinkingStepsPanel
            steps={message.thinkingSteps}
            processingTimeMs={message.processingTimeMs}
            isExpanded={isThinkingExpanded}
            onToggle={() => setIsThinkingExpanded(!isThinkingExpanded)}
          />
        )}

        {/* Tool Calls */}
        {!isUser && message.toolCalls && message.toolCalls.length > 0 && (
          <ToolCallsPanel toolCalls={message.toolCalls} />
        )}

        <span
          className={cn(
            'text-[10px] text-muted-foreground/60 mt-1',
            isUser ? 'mr-1' : 'ml-1'
          )}
        >
          {message.timestamp.toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit',
          })}
        </span>
      </div>
    </div>
  );
};

const TypingIndicator = ({ assistantName }: { assistantName?: string }) => (
  <div className="flex gap-3 animate-in fade-in">
    <Avatar className="h-8 w-8 shrink-0 ring-2 ring-background ring-blue-500/20 shadow-md">
      <AvatarFallback className="bg-gradient-to-br from-blue-500 to-purple-600 text-white">
        <Bot className="h-4 w-4" />
      </AvatarFallback>
    </Avatar>
    <div className="flex flex-col">
      {assistantName && (
        <span className="text-xs font-medium text-muted-foreground mb-1 ml-1">
          {assistantName}
        </span>
      )}
      <div className="bg-muted/80 backdrop-blur-sm rounded-2xl rounded-tl-md px-4 py-3 shadow-sm">
        <div className="flex items-center gap-1.5">
          <div className="flex gap-1">
            <span className="w-2 h-2 bg-foreground/40 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
            <span className="w-2 h-2 bg-foreground/40 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
            <span className="w-2 h-2 bg-foreground/40 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
          </div>
          <span className="text-xs text-muted-foreground ml-2">Thinking...</span>
        </div>
      </div>
    </div>
  </div>
);

const ConfirmationBanner = ({
  confirmation,
  isLoading,
  onConfirm,
  onCancel,
}: {
  confirmation: ConfirmationRequest;
  isLoading?: boolean;
  onConfirm?: () => void;
  onCancel?: () => void;
}) => (
  <div className="mx-4 mb-4 rounded-xl bg-gradient-to-r from-amber-500/10 to-orange-500/10 border border-amber-500/20 p-4 animate-in slide-in-from-bottom-2">
    <div className="flex items-start gap-3">
      <div className="p-2 rounded-full bg-amber-500/20">
        <AlertTriangle className="h-5 w-5 text-amber-500" />
      </div>
      <div className="flex-1">
        <h4 className="text-sm font-semibold text-foreground mb-1">
          Confirmation Required
        </h4>
        <p className="text-sm text-muted-foreground mb-3">
          {confirmation.message}
        </p>

        {confirmation.affected_items.length > 0 && (
          <div className="mb-3 p-2 rounded-lg bg-background/50 text-xs">
            <p className="font-medium text-muted-foreground mb-1">Affected items:</p>
            <ul className="space-y-0.5 text-muted-foreground/80">
              {confirmation.affected_items.slice(0, 5).map((item) => (
                <li key={item.id} className="flex items-center gap-1">
                  <span className="text-primary">#{item.id}</span>
                  <span className="truncate">{item.title}</span>
                </li>
              ))}
              {confirmation.affected_items.length > 5 && (
                <li className="text-muted-foreground/60 italic">
                  ...and {confirmation.affected_items.length - 5} more
                </li>
              )}
            </ul>
          </div>
        )}

        <div className="flex items-center gap-2">
          <Button
            size="sm"
            variant="destructive"
            onClick={onConfirm}
            disabled={isLoading}
            className="gap-1.5"
          >
            {isLoading && <Loader2 className="h-3.5 w-3.5 animate-spin" />}
            Yes, proceed
          </Button>
          <Button
            size="sm"
            variant="outline"
            onClick={onCancel}
            disabled={isLoading}
            className="gap-1.5"
          >
            <X className="h-3.5 w-3.5" />
            Cancel
          </Button>
        </div>
      </div>
    </div>
  </div>
);

const EmptyState = ({
  suggestedPrompts,
  onSelectPrompt,
}: {
  suggestedPrompts?: string[];
  onSelectPrompt: (prompt: string) => void;
}) => (
  <div className="flex-1 flex flex-col items-center justify-center p-8 text-center">
    <div className="w-20 h-20 rounded-full bg-gradient-to-br from-blue-500/20 to-purple-500/20 flex items-center justify-center mb-6 animate-pulse">
      <Sparkles className="h-10 w-10 text-primary" />
    </div>
    <h3 className="text-xl font-semibold mb-2">How can I help you today?</h3>
    <p className="text-muted-foreground mb-8 max-w-md">
      I can help you manage your tasks through natural conversation.
      Try creating, listing, completing, or deleting tasks.
    </p>

    {suggestedPrompts && suggestedPrompts.length > 0 && (
      <div className="flex flex-wrap gap-2 justify-center max-w-lg">
        {suggestedPrompts.map((prompt) => (
          <button
            key={prompt}
            onClick={() => onSelectPrompt(prompt)}
            className="px-4 py-2 text-sm rounded-full bg-muted/80 hover:bg-muted text-foreground/80 hover:text-foreground transition-all hover:scale-105 hover:shadow-md"
          >
            {prompt}
          </button>
        ))}
      </div>
    )}
  </div>
);

// ============================================================================
// Main Component
// ============================================================================

export function ChatKitUI({
  messages,
  isLoading = false,
  isTyping = false,
  error,
  pendingConfirmation,
  userAvatar,
  assistantName = 'AI Assistant',
  assistantAvatar,
  onSendMessage,
  onConfirm,
  onCancel,
  placeholder = 'Type a message...',
  suggestedPrompts,
  className,
}: ChatKitProps) {
  const [input, setInput] = useState('');
  const scrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isTyping]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    onSendMessage(input.trim());
    setInput('');
  };

  const handlePromptSelect = (prompt: string) => {
    onSendMessage(prompt);
    setInput('');
  };

  return (
    <div className={cn('flex flex-col h-full bg-background', className)}>
      {/* Messages Area */}
      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto p-4 space-y-6 scroll-smooth max-h-[calc(100vh-16rem)]"
      >
        {messages.length === 0 ? (
          <EmptyState
            suggestedPrompts={suggestedPrompts}
            onSelectPrompt={handlePromptSelect}
          />
        ) : (
          <>
            {messages.map((message) => (
              <MessageBubble
                key={message.id}
                message={message}
                userAvatar={userAvatar}
                assistantName={assistantName}
                assistantAvatar={assistantAvatar}
              />
            ))}
            {isTyping && <TypingIndicator assistantName={assistantName} />}
          </>
        )}
      </div>

      {/* Error Banner */}
      {error && (
        <div className="mx-4 mb-2 p-3 rounded-lg bg-destructive/10 border border-destructive/20 text-destructive text-sm flex items-center gap-2">
          <AlertCircle className="h-4 w-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Confirmation Banner */}
      {pendingConfirmation && (
        <ConfirmationBanner
          confirmation={pendingConfirmation}
          isLoading={isLoading}
          onConfirm={onConfirm}
          onCancel={onCancel}
        />
      )}

      {/* Input Area */}
      <div className="border-t border-border/50 p-4 bg-background/80 backdrop-blur-sm">
        <form onSubmit={handleSubmit} className="flex gap-2">
          <div className="flex-1 relative">
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={placeholder}
              disabled={isLoading || !!pendingConfirmation}
              className={cn(
                'w-full h-11 px-4 rounded-xl',
                'bg-muted/50 border border-border/50',
                'text-sm placeholder:text-muted-foreground/60',
                'focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary/50',
                'disabled:opacity-50 disabled:cursor-not-allowed',
                'transition-all'
              )}
            />
          </div>
          <Button
            type="submit"
            size="icon"
            disabled={!input.trim() || isLoading || !!pendingConfirmation}
            className="h-11 w-11 rounded-xl shrink-0 bg-primary hover:bg-primary/90 transition-all hover:scale-105"
          >
            {isLoading ? (
              <Loader2 className="h-5 w-5 animate-spin" />
            ) : (
              <Send className="h-5 w-5" />
            )}
          </Button>
        </form>
      </div>
    </div>
  );
}

/** Markdown renderer for assistant messages */
const MarkdownContent = memo(function MarkdownContent({ content }: { content: string }) {
  return (
    <div className="text-sm prose prose-sm dark:prose-invert max-w-none prose-p:leading-relaxed">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
          strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
          ul: ({ children }) => <ul className="list-disc list-inside my-2 space-y-1">{children}</ul>,
          ol: ({ children }) => <ol className="list-decimal list-inside my-2 space-y-1">{children}</ol>,
          li: ({ children }) => <li className="leading-relaxed">{children}</li>,
          table: ({ children }) => (
            <div className="my-3 overflow-x-auto rounded-lg border border-border">
              <table className="w-full text-xs border-collapse">{children}</table>
            </div>
          ),
          thead: ({ children }) => <thead className="bg-muted/50">{children}</thead>,
          tbody: ({ children }) => <tbody className="divide-y divide-border">{children}</tbody>,
          tr: ({ children }) => <tr className="hover:bg-muted/30">{children}</tr>,
          th: ({ children }) => <th className="px-3 py-2 text-left font-semibold border-b border-border">{children}</th>,
          td: ({ children }) => <td className="px-3 py-2 text-muted-foreground">{children}</td>,
          code: ({ children }) => <code className="bg-muted px-1 py-0.5 rounded text-xs">{children}</code>,
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
});

export default ChatKitUI;
