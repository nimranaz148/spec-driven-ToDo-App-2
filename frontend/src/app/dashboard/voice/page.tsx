'use client';

import { useState, useRef, useCallback, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  Mic,
  MicOff,
  Volume2,
  VolumeX,
  Loader2,
  Brain,
  ChevronDown,
  ChevronRight,
  CheckCircle2,
  Wrench,
  MessageSquarePlus,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useAuthStore } from '@/stores/auth-store';
import { api, StreamEvent } from '@/lib/api';

interface VoiceMessage {
  id: string;
  type: 'user' | 'assistant';
  text: string;
  timestamp: Date;
  isStreaming?: boolean;
}

/** Clean text for speech - remove markdown, emojis, tables */
function cleanTextForSpeech(text: string): string {
  return text
    .replace(/\|[^\n]*\|/g, '') // Remove table rows
    .replace(/\|-+\|/g, '')     // Remove table separators
    .replace(/\*\*([^*]+)\*\*/g, '$1') // Bold
    .replace(/\*([^*]+)\*/g, '$1')     // Italic
    .replace(/#{1,6}\s*/g, '')         // Headers
    .replace(/[\u{1F300}-\u{1F9FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]/gu, '') // Emojis
    .replace(/[✓✅⏳🔴🟡🟢📋➕🎉⚠️❌🤖💪🎯📝]/g, '') // Common emojis
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1') // Links
    .replace(/```[^`]*```/g, '')  // Code blocks
    .replace(/`([^`]+)`/g, '$1') // Inline code
    .replace(/\n+/g, '. ')
    .replace(/\s+/g, ' ')
    .trim();
}

export default function VoicePage() {
  const { user } = useAuthStore();
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [messages, setMessages] = useState<VoiceMessage[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [conversationId, setConversationId] = useState<number | null>(null);
  const [isSpeechSupported] = useState(() => {
    if (typeof window !== 'undefined') {
      return !!(window.SpeechRecognition || window.webkitSpeechRecognition);
    }
    return true;
  });
  
  const messageIdRef = useRef(0);
  const recognitionRef = useRef<any>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const speakText = useCallback((text: string) => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const cleaned = cleanTextForSpeech(text);
      const utterance = new SpeechSynthesisUtterance(cleaned);
      utterance.rate = 1.0;
      utterance.onstart = () => setIsSpeaking(true);
      utterance.onend = () => setIsSpeaking(false);
      window.speechSynthesis.speak(utterance);
    }
  }, []);

  const stopSpeaking = () => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
    }
  };

  const startListening = () => {
    if (!isSpeechSupported) return;

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();

    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    recognition.onstart = () => {
      setIsListening(true);
      setTranscript('');
    };

    recognition.onresult = (event: any) => {
      const current = event.resultIndex;
      const transcriptText = event.results[current][0].transcript;
      setTranscript(transcriptText);
    };

    recognition.onend = () => {
      setIsListening(false);
      if (transcript) {
        handleVoiceInput(transcript);
      }
    };

    recognition.onerror = (event: any) => {
      console.error('Speech recognition error:', event.error);
      setIsListening(false);
      if (event.error === 'no-speech') {
        speakText("I didn't hear anything. Please try again.");
      }
    };

    recognitionRef.current = recognition;
    recognition.start();
  };

  const stopListening = () => {
    recognitionRef.current?.stop();
    setIsListening(false);
  };

  const handleVoiceInput = useCallback(async (text: string) => {
    if (!text.trim() || !user) return;

    // Add user message
    messageIdRef.current += 1;
    const userMsgId = `user-${messageIdRef.current}`;
    setMessages((prev) => [...prev, {
      id: userMsgId,
      type: 'user',
      text: text.trim(),
      timestamp: new Date(),
    }]);

    // Add streaming assistant message
    messageIdRef.current += 1;
    const assistantMsgId = `assistant-${messageIdRef.current}`;
    setMessages((prev) => [...prev, {
      id: assistantMsgId,
      type: 'assistant',
      text: '',
      timestamp: new Date(),
      isStreaming: true,
    }]);

    setIsProcessing(true);
    speakText("Let me help you with that.");

    try {
      let fullContent = '';
      
      for await (const event of api.streamChatMessage(user.id, text.trim(), conversationId)) {
        switch (event.type) {
          case 'start':
            setConversationId(event.conversation_id);
            break;
          case 'token':
            fullContent += event.content;
            setMessages((prev) => prev.map((m) =>
              m.id === assistantMsgId ? { ...m, text: fullContent } : m
            ));
            break;
          case 'done':
            setMessages((prev) => prev.map((m) =>
              m.id === assistantMsgId ? { ...m, isStreaming: false } : m
            ));
            // Speak the final response
            if (fullContent) {
              speakText(fullContent);
            }
            break;
          case 'error':
            throw new Error(event.message);
        }
      }
    } catch (error) {
      console.error('Voice chat error:', error);
      const errorText = 'Sorry, I encountered an error. Please try again.';
      setMessages((prev) => prev.map((m) =>
        m.id === assistantMsgId ? { ...m, text: errorText, isStreaming: false } : m
      ));
      speakText(errorText);
    } finally {
      setIsProcessing(false);
    }
  }, [speakText, user, conversationId]);

  const startNewConversation = () => {
    setConversationId(null);
    setMessages([]);
    setTranscript('');
    speakText("Starting a new conversation. How can I help you?");
  };

  return (
    <div className="h-[calc(100vh-10rem)] flex flex-col max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-4 flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3 mb-1">
            <Mic className="h-7 w-7 text-primary" />
            <h1 className="text-2xl font-bold">Voice Assistant</h1>
          </div>
          <p className="text-muted-foreground text-sm">
            Manage tasks hands-free with voice commands
          </p>
        </div>
        <Button variant="outline" size="sm" onClick={startNewConversation}>
          <MessageSquarePlus className="h-4 w-4 mr-2" />
          New Chat
        </Button>
      </div>

      {/* Chat Messages */}
      <Card className="flex-1 border-border/50 mb-4 overflow-hidden">
        <ScrollArea className="h-full p-4">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center p-8">
              <Mic className="h-12 w-12 text-muted-foreground/50 mb-4" />
              <p className="text-muted-foreground">
                Tap the microphone and speak to get started
              </p>
              <div className="mt-4 text-sm text-muted-foreground/70">
                <p>Try saying:</p>
                <ul className="mt-2 space-y-1">
                  <li>"Show my tasks"</li>
                  <li>"Add a task to buy groceries"</li>
                  <li>"Mark task 1 as done"</li>
                </ul>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {messages.map((msg) => (
                <div
                  key={msg.id}
                  className={cn(
                    'flex',
                    msg.type === 'user' ? 'justify-end' : 'justify-start'
                  )}
                >
                  <div
                    className={cn(
                      'max-w-[85%] rounded-2xl px-4 py-3',
                      msg.type === 'user'
                        ? 'bg-primary text-primary-foreground rounded-tr-md'
                        : 'bg-muted/80 rounded-tl-md'
                    )}
                  >
                    {msg.type === 'assistant' ? (
                      <div className="text-sm prose prose-sm dark:prose-invert max-w-none">
                        <ReactMarkdown remarkPlugins={[remarkGfm]} components={{
                          p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                          table: ({ children }) => (
                            <div className="my-2 overflow-x-auto rounded border border-border">
                              <table className="w-full text-xs">{children}</table>
                            </div>
                          ),
                          thead: ({ children }) => <thead className="bg-muted/50">{children}</thead>,
                          th: ({ children }) => <th className="px-2 py-1 text-left font-semibold border-b">{children}</th>,
                          td: ({ children }) => <td className="px-2 py-1">{children}</td>,
                        }}>
                          {msg.text || (msg.isStreaming ? '...' : '')}
                        </ReactMarkdown>
                        {msg.isStreaming && (
                          <span className="inline-block w-1.5 h-4 ml-1 bg-current animate-pulse rounded" />
                        )}
                      </div>
                    ) : (
                      <p className="text-sm">{msg.text}</p>
                    )}
                  </div>
                </div>
              ))}
              <div ref={scrollRef} />
            </div>
          )}
        </ScrollArea>
      </Card>

      {/* Voice Controls */}
      <Card className="border-border/50">
        <CardContent className="p-4">
          <div className="flex items-center justify-center gap-4">
            {/* Mic Button */}
            <button
              onClick={isListening ? stopListening : startListening}
              disabled={isProcessing || !isSpeechSupported}
              className={cn(
                'w-16 h-16 rounded-full flex items-center justify-center transition-all',
                isListening
                  ? 'bg-destructive text-destructive-foreground animate-pulse'
                  : 'bg-primary text-primary-foreground hover:scale-105',
                (isProcessing || !isSpeechSupported) && 'opacity-50 cursor-not-allowed'
              )}
            >
              {isProcessing ? (
                <Loader2 className="h-7 w-7 animate-spin" />
              ) : isListening ? (
                <MicOff className="h-7 w-7" />
              ) : (
                <Mic className="h-7 w-7" />
              )}
            </button>

            {/* Speaker Button */}
            <button
              onClick={stopSpeaking}
              disabled={!isSpeaking}
              className={cn(
                'w-12 h-12 rounded-full flex items-center justify-center transition-all',
                isSpeaking
                  ? 'bg-primary/20 text-primary'
                  : 'bg-muted text-muted-foreground',
                !isSpeaking && 'opacity-50'
              )}
            >
              {isSpeaking ? <Volume2 className="h-5 w-5" /> : <VolumeX className="h-5 w-5" />}
            </button>
          </div>

          {/* Transcript */}
          {transcript && (
            <p className="mt-3 text-center text-sm text-muted-foreground italic">
              "{transcript}"
            </p>
          )}

          {/* Status */}
          <p className="mt-2 text-center text-xs text-muted-foreground">
            {!isSpeechSupported
              ? 'Speech not supported - use Chrome or Edge'
              : isProcessing
              ? 'Processing...'
              : isListening
              ? 'Listening...'
              : 'Tap microphone to speak'}
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
