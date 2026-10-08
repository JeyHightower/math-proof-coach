'use client';

import { useState, useEffect} from 'react';
import { Header } from './components/Header';
import { MessageList } from './components/MessageList';
import { MessageInput } from './components/MessageInput';
import { Message, SessionState } from '@/types/chat';


const API_URL = (process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000').replace(/\/$/, '');


export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [session, setSession] = useState<SessionState>({
    sessionId:'',
    status: 'idle',
  });


  useEffect(() => {
    setSession((prev) => ({
      ...prev,
      sessionId: crypto.randomUUID(),
    }))
  }, []);


  const handleResetSession = () => {
    setMessages([]);
    setSession({
      sessionId: crypto.randomUUID(),
      status:'idle',
    });
  };

  
  const handleSendMessage = async (content: string) => {
    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content,
      createdAt: new Date(),
    }
    
    setMessages((prev) => [...prev, userMessage]);
    setSession((prev) => ({...prev, status: 'loading', error: undefined}));

    try {
      const response = await fetch(`${API_URL}/api/chat`, {
        method: "POST",
        headers: {
          'Content-Type': "application/json",
        },
        body: JSON.stringify({
          session_id: session.sessionId,
          message: content,
        }),
      });

      if (!response.ok){
        throw new Error(`Server error: ${response.status}`);
      }

      const data = await response.json();

      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: data.response || data.message || "No response returned from coach.",
        createdAt: new Date(),
      }

      setMessages((prev) => [...prev, assistantMessage]);
      setSession((prev) => ({...prev, status: 'idle'}));
    } catch (err: unknown){
      console.error("Chat error:", err);
      const errorMessage = 
        err instanceof Error ? err.message : "Failed to connect to the server.";
      
      setSession((prev) => ({
        ...prev,
        status: 'error',
        error: `${errorMessage} The server may be waking up (free hosting can take about a minute). Please try again.`,
      }))
    }

  };

  return (
    <main className="flex flex-col h-screen bg-zinc-950 text-zinc-100 overflow-hidden">
      <Header
        sessionId={session.sessionId}
        onResetSession={handleResetSession}
      />

      {session.status === 'error' && (
        <div className="bg-red-900/40 border-b border-red-800/60 px-4 py-2 text-center text-red-200 text-xs flex items-center justify-center space-x-2">
          <span>⚠️ {session.error}</span>
          <button
            onClick={() => setSession((prev) => ({ ...prev, status: 'idle' }))}
            className="underline hover:text-white font-medium ml-2 cursor-pointer"
          >
            Dismiss
          </button>
        </div>
      )}

      <MessageList messages={messages} status={session.status} />

      <MessageInput
        onSendMessage={handleSendMessage}
        disabled={session.status === 'loading'}
      />
    </main>
  );
}

