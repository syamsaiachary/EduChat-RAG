import { useState, useCallback } from 'react';
import api from '../api/axiosInstance';
import type { Message, AppError } from '../types';

export function useChat(sessionId: string | null) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<AppError | null>(null);

  const fetchMessages = useCallback(async () => {
    if (!sessionId) return;
    setIsLoading(true);
    try {
      const { data } = await api.get(`/sessions/${sessionId}/messages`);
      setMessages(data);
    } catch (err: any) {
      setError(err.response?.data || { message: 'Failed to fetch messages' });
    } finally {
      setIsLoading(false);
    }
  }, [sessionId]);

  const sendMessage = async (content: string) => {
    if (!sessionId) return;
    
    // Optimistic UI update
    setMessages(prev => [...prev, { role: 'user', content }]);
    
    // Placeholder for assistant
    const placeholderId = 'temp-' + Date.now();
    setMessages(prev => [...prev, { id: placeholderId, role: 'assistant', content: '', streaming: true }]);

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/sessions/${sessionId}/messages/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        // We ensure cookies are sent with the fetch request so it can be authenticated
        credentials: 'include',
        body: JSON.stringify({ content }),
      });

      if (!response.body) throw new Error('No response body');

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n\n');
        
        for (const line of lines) {
          if (!line.startsWith('data: ')) continue;
          
          const jsonStr = line.slice(6).trim();
          if (!jsonStr) continue;
          
          try {
            const data = JSON.parse(jsonStr);
            if (data.token) {
              setMessages(prev => prev.map(m => 
                m.id === placeholderId ? { ...m, content: m.content + data.token } : m
              ));
            }
            if (data.done) {
              setMessages(prev => prev.map(m => 
                m.id === placeholderId ? { ...m, streaming: false, sources: data.sources } : m
              ));
            }
            if (data.error) {
               setMessages(prev => prev.map(m => 
                m.id === placeholderId ? { ...m, streaming: false, content: m.content + "\n[Error: " + data.error + "]" } : m
              ));
            }
          } catch (e) {
            console.error('Failed to parse SSE JSON', e);
          }
        }
      }
    } catch (err: any) {
      setMessages(prev => prev.map(m => 
        m.id === placeholderId ? { ...m, streaming: false, content: 'Failed to send message.' } : m
      ));
    }
  };

  return { messages, isLoading, error, fetchMessages, sendMessage };
}
