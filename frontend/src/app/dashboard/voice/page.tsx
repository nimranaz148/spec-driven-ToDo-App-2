'use client';

import { useState, useRef, useCallback } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  Mic,
  MicOff,
  Volume2,
  VolumeX,
  Loader2,
  Sparkles,
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface VoiceMessage {
  id: string;
  type: 'user' | 'assistant';
  text: string;
  timestamp: Date;
}

export default function VoicePage() {
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [messages, setMessages] = useState<VoiceMessage[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  // Check if speech recognition is supported during initial render
  const [isSpeechSupported] = useState(() => {
    if (typeof window !== 'undefined') {
      return !!(window.SpeechRecognition || window.webkitSpeechRecognition);
    }
    return true; // SSR default
  });
  const messageIdRef = useRef(0);

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const recognitionRef = useRef<any>(null);

  const startListening = () => {
    if (!isSpeechSupported) return;

    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();

    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    recognition.onstart = () => {
      setIsListening(true);
      setTranscript('');
    };

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
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

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    recognition.onerror = (event: any) => {
      console.error('Speech recognition error:', event.error);
      setIsListening(false);
    };

    recognitionRef.current = recognition;
    recognition.start();
  };

  const stopListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
    setIsListening(false);
  };

  const speakText = useCallback((text: string) => {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.onstart = () => setIsSpeaking(true);
      utterance.onend = () => setIsSpeaking(false);
      window.speechSynthesis.speak(utterance);
    }
  }, []);

  const handleVoiceInput = useCallback((text: string) => {
    if (!text.trim()) return;

    messageIdRef.current += 1;
    const userMessage: VoiceMessage = {
      id: `user-${messageIdRef.current}`,
      type: 'user',
      text: text.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsProcessing(true);

    // Simulate AI response
    setTimeout(() => {
      messageIdRef.current += 1;
      const aiResponse = `I heard: ${text}. This is a placeholder response. In a full implementation, I would process your voice command and help you manage your tasks.`;

      const aiMessage: VoiceMessage = {
        id: `assistant-${messageIdRef.current}`,
        type: 'assistant',
        text: aiResponse,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, aiMessage]);
      setIsProcessing(false);

      // Speak the response
      speakText(aiResponse);
    }, 1500);
  }, [speakText]);

  const stopSpeaking = () => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
    }
  };

  const exampleCommands = [
    'Show my high priority tasks',
    'What tasks are due today?',
    'Add a new task called meeting prep',
    'Mark my first task as complete',
  ];

  return (
    <div className="h-[calc(100vh-10rem)] flex flex-col max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-2">
          <Mic className="h-8 w-8 text-primary" />
          <h1 className="text-2xl sm:text-3xl font-bold">Voice Assistant</h1>
        </div>
        <p className="text-muted-foreground">
          Manage your tasks hands-free with voice commands
        </p>
      </div>

      {/* Main Content */}
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Voice Control */}
        <Card className="border-border/50 flex flex-col">
          <CardContent className="flex-1 flex flex-col items-center justify-center p-8">
            {!isSpeechSupported ? (
              <div className="text-center">
                <MicOff className="h-16 w-16 mx-auto mb-4 text-muted-foreground" />
                <h3 className="text-lg font-semibold mb-2">
                  Speech Recognition Not Supported
                </h3>
                <p className="text-muted-foreground text-sm">
                  Your browser does not support speech recognition. Please try Chrome
                  or Edge.
                </p>
              </div>
            ) : (
              <>
                {/* Mic Button */}
                <button
                  onClick={isListening ? stopListening : startListening}
                  disabled={isProcessing}
                  className={cn(
                    'w-32 h-32 rounded-full flex items-center justify-center transition-all duration-300',
                    isListening
                      ? 'bg-destructive text-destructive-foreground animate-pulse-gold'
                      : 'bg-primary text-primary-foreground hover:scale-105 gold-glow',
                    isProcessing && 'opacity-50 cursor-not-allowed'
                  )}
                >
                  {isProcessing ? (
                    <Loader2 className="h-12 w-12 animate-spin" />
                  ) : isListening ? (
                    <MicOff className="h-12 w-12" />
                  ) : (
                    <Mic className="h-12 w-12" />
                  )}
                </button>

                {/* Status */}
                <p className="mt-6 text-center">
                  {isProcessing ? (
                    <span className="text-muted-foreground">Processing...</span>
                  ) : isListening ? (
                    <span className="text-primary font-medium">Listening...</span>
                  ) : (
                    <span className="text-muted-foreground">
                      Tap to start speaking
                    </span>
                  )}
                </p>

                {/* Transcript */}
                {transcript && (
                  <div className="mt-4 p-4 rounded-lg bg-muted max-w-full">
                    <p className="text-sm text-center">&ldquo;{transcript}&rdquo;</p>
                  </div>
                )}

                {/* Speaking Indicator */}
                {isSpeaking && (
                  <div className="mt-4 flex items-center gap-2">
                    <Volume2 className="h-4 w-4 text-primary animate-pulse" />
                    <span className="text-sm text-muted-foreground">Speaking...</span>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={stopSpeaking}
                      className="ml-2"
                    >
                      <VolumeX className="h-4 w-4" />
                    </Button>
                  </div>
                )}

                {/* Example Commands */}
                {messages.length === 0 && !isListening && (
                  <div className="mt-8 text-center">
                    <p className="text-sm text-muted-foreground mb-3">
                      Try saying:
                    </p>
                    <div className="space-y-2">
                      {exampleCommands.map((cmd) => (
                        <p
                          key={cmd}
                          className="text-sm text-primary/80 bg-primary/5 px-3 py-1 rounded-full inline-block mx-1"
                        >
                          &ldquo;{cmd}&rdquo;
                        </p>
                      ))}
                    </div>
                  </div>
                )}
              </>
            )}
          </CardContent>
        </Card>

        {/* Conversation History */}
        <Card className="border-border/50 flex flex-col">
          <div className="p-4 border-b border-border">
            <h3 className="font-semibold">Conversation History</h3>
          </div>
          <ScrollArea className="flex-1 p-4">
            {messages.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-center p-8">
                <Sparkles className="h-12 w-12 text-primary/30 mb-4" />
                <p className="text-muted-foreground text-sm">
                  Your voice conversation history will appear here
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={cn(
                      'p-3 rounded-lg',
                      message.type === 'user'
                        ? 'bg-primary/10 ml-8'
                        : 'bg-muted mr-8'
                    )}
                  >
                    <p className="text-xs font-medium mb-1 text-muted-foreground">
                      {message.type === 'user' ? 'You' : 'Assistant'}
                    </p>
                    <p className="text-sm">{message.text}</p>
                    <p className="text-xs text-muted-foreground mt-1">
                      {message.timestamp.toLocaleTimeString([], {
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </ScrollArea>
        </Card>
      </div>
    </div>
  );
}

// Add TypeScript declarations for Web Speech API
declare global {
  interface Window {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    SpeechRecognition: any;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    webkitSpeechRecognition: any;
  }
}
