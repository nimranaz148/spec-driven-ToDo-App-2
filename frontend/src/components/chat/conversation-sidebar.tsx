'use client';

import React, { useState } from 'react';
import { Plus, MessageSquare, Trash2, Edit2, MoreVertical, ChevronLeft, ChevronRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { cn } from '@/lib/utils';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Input } from '@/components/ui/input';

interface Conversation {
  id: number;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

interface ConversationSidebarProps {
  conversations: Conversation[];
  activeConversationId: number | null;
  onSelectConversation: (id: number) => void;
  onCreateConversation: () => void;
  onDeleteConversation: (id: number) => void;
  onRenameConversation: (id: number, title: string) => void;
  isLoading?: boolean;
}

export default function ConversationSidebar({
  conversations,
  activeConversationId,
  onSelectConversation,
  onCreateConversation,
  onDeleteConversation,
  onRenameConversation,
  isLoading = false,
}: ConversationSidebarProps) {
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editTitle, setEditTitle] = useState('');
  const [isCollapsed, setIsCollapsed] = useState(false);

  const handleStartEdit = (conversation: Conversation) => {
    setEditingId(conversation.id);
    setEditTitle(conversation.title);
  };

  const handleSaveEdit = () => {
    if (editingId && editTitle.trim()) {
      onRenameConversation(editingId, editTitle.trim());
    }
    setEditingId(null);
    setEditTitle('');
  };

  const handleCancelEdit = () => {
    setEditingId(null);
    setEditTitle('');
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60);

    if (diffInHours < 24) {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } else if (diffInHours < 24 * 7) {
      return date.toLocaleDateString([], { weekday: 'short' });
    } else {
      return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
    }
  };

  return (
    <div className={cn(
      "border-r border-border bg-muted/30 flex flex-col h-full transition-all duration-300",
      isCollapsed ? "w-12" : "w-64"
    )}>
      {/* Toggle Button */}
      <div className="p-2 border-b border-border">
        <Button
          onClick={() => setIsCollapsed(!isCollapsed)}
          size="sm"
          variant="ghost"
          className="w-full h-8 p-0"
        >
          {isCollapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
        </Button>
      </div>

      {!isCollapsed && (
        <>
          {/* Header */}
          <div className="p-3 border-b border-border">
            <div className="flex items-center justify-between mb-2">
              <h2 className="font-semibold text-base">Conversations</h2>
              <Button
                onClick={onCreateConversation}
                size="sm"
                className="h-7 w-7 p-0"
                disabled={isLoading}
              >
                <Plus className="h-3 w-3" />
              </Button>
            </div>
            <Button
              onClick={onCreateConversation}
              variant="outline"
              className="w-full justify-start gap-2 h-8 text-sm"
              disabled={isLoading}
            >
              <Plus className="h-3 w-3" />
              New Chat
            </Button>
          </div>

          {/* Conversations List */}
          <ScrollArea className="flex-1">
            <div className="p-1 space-y-1">
              {conversations.length === 0 ? (
                <div className="text-center py-6 text-muted-foreground">
                  <MessageSquare className="h-6 w-6 mx-auto mb-2 opacity-50" />
                  <p className="text-xs">No conversations yet</p>
                  <p className="text-xs opacity-75">Start a new chat</p>
                </div>
              ) : (
                conversations.map((conversation) => (
                  <div
                    key={conversation.id}
                    className={cn(
                      'group relative rounded-md p-2 cursor-pointer transition-colors hover:bg-muted/50',
                      activeConversationId === conversation.id && 'bg-muted border border-border'
                    )}
                    onClick={() => onSelectConversation(conversation.id)}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0">
                        {editingId === conversation.id ? (
                          <Input
                            value={editTitle}
                            onChange={(e) => setEditTitle(e.target.value)}
                            onBlur={handleSaveEdit}
                            onKeyDown={(e) => {
                              if (e.key === 'Enter') handleSaveEdit();
                              if (e.key === 'Escape') handleCancelEdit();
                            }}
                            className="h-5 text-xs font-medium"
                            autoFocus
                            onClick={(e) => e.stopPropagation()}
                          />
                        ) : (
                          <h3 className="font-medium text-xs truncate">
                            {conversation.title}
                          </h3>
                        )}
                        <div className="flex items-center gap-1 mt-1">
                          <span className="text-xs text-muted-foreground">
                            {formatDate(conversation.updated_at)}
                          </span>
                          {conversation.message_count > 0 && (
                            <span className="text-xs text-muted-foreground">
                              • {conversation.message_count}
                            </span>
                          )}
                        </div>
                      </div>

                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-5 w-5 p-0 opacity-0 group-hover:opacity-100 transition-opacity"
                            onClick={(e) => e.stopPropagation()}
                          >
                            <MoreVertical className="h-3 w-3" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end" className="w-32">
                          <DropdownMenuItem
                            onClick={(e) => {
                              e.stopPropagation();
                              handleStartEdit(conversation);
                            }}
                          >
                            <Edit2 className="h-3 w-3 mr-2" />
                            Rename
                          </DropdownMenuItem>
                          <DropdownMenuItem
                            onClick={(e) => {
                              e.stopPropagation();
                              onDeleteConversation(conversation.id);
                            }}
                            className="text-destructive focus:text-destructive"
                          >
                            <Trash2 className="h-3 w-3 mr-2" />
                            Delete
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </div>
                  </div>
                ))
              )}
            </div>
          </ScrollArea>
        </>
      )}

      {/* Collapsed state - show only active conversation indicator */}
      {isCollapsed && (
        <div className="flex-1 flex flex-col items-center py-2">
          <Button
            onClick={onCreateConversation}
            size="sm"
            variant="ghost"
            className="h-8 w-8 p-0 mb-2"
            disabled={isLoading}
          >
            <Plus className="h-4 w-4" />
          </Button>
          {conversations.map((conversation) => (
            <Button
              key={conversation.id}
              onClick={() => onSelectConversation(conversation.id)}
              size="sm"
              variant="ghost"
              className={cn(
                "h-8 w-8 p-0 mb-1",
                activeConversationId === conversation.id && 'bg-muted'
              )}
            >
              <MessageSquare className="h-4 w-4" />
            </Button>
          ))}
        </div>
      )}
    </div>
  );
}
