import React, { useState, useEffect, useRef } from 'react';
import { useAuthContext } from '../context/AuthContext';
import { useSessions } from '../hooks/useSessions';
import { useChat } from '../hooks/useChat';
import { GraduationCap, LogOut, Settings, Plus, Send, Trash2, FileText } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

export const Chat = () => {
  const { user, isAdmin, logout } = useAuthContext();
  const { sessions, fetchSessions, createSession, deleteSession } = useSessions();
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const { messages, fetchMessages, sendMessage } = useChat(activeSessionId);
  
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchSessions();
  }, [fetchSessions]);

  useEffect(() => {
    if (sessions.length > 0 && !activeSessionId) {
      setActiveSessionId(sessions[0].id);
    }
  }, [sessions, activeSessionId]);

  useEffect(() => {
    if (activeSessionId) {
      fetchMessages();
    }
  }, [activeSessionId, fetchMessages]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleNewChat = async () => {
    const session = await createSession('New Chat');
    setActiveSessionId(session.id);
  };

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || !activeSessionId) return;
    const text = input.trim();
    setInput('');
    await sendMessage(text);
    fetchSessions();
  };

  const SourcesDisplay = ({ sources }: { sources: any[] }) => {
    if (!sources || sources.length === 0) return null;
    return (
      <div className="mt-3 bg-background/50 rounded-lg p-3 border border-border text-xs text-text-secondary">
        <div className="flex items-center gap-1.5 mb-2 font-medium text-text-primary">
          <FileText size={14} className="text-primary" /> Sources used:
        </div>
        <ul className="space-y-1 list-disc list-inside">
          {sources.map((s, idx) => (
            <li key={idx}>
              {s.filename} <span className="text-text-muted">(chunk {s.chunk_index})</span>
            </li>
          ))}
        </ul>
      </div>
    );
  };

  return (
    <div className="flex h-screen bg-background overflow-hidden relative">
      <div className="w-64 bg-sidebar border-r border-border flex-col shrink-0 z-10 hidden md:flex">
        <div className="p-4 flex items-center gap-3">
          <div className="w-8 h-8 bg-primary/20 rounded-lg flex items-center justify-center text-primary">
            <GraduationCap size={20} />
          </div>
          <span className="font-bold tracking-tight text-white">EduChat</span>
        </div>
        
        <div className="px-4 py-2">
          <button 
            onClick={handleNewChat}
            className="w-full flex items-center justify-center gap-2 bg-primary hover:bg-primary-hover text-white font-medium py-2.5 rounded-lg transition-colors shadow-lg shadow-primary/20"
          >
            <Plus size={18} /> New Chat
          </button>
        </div>

        <div className="flex-1 overflow-y-auto mt-4 px-2 space-y-0.5">
          {sessions.map(s => (
            <div 
              key={s.id}
              onClick={() => setActiveSessionId(s.id)}
              className={`group flex items-center justify-between px-3 py-2.5 rounded-lg cursor-pointer transition-colors ${activeSessionId === s.id ? 'bg-surface border-l-2 border-primary text-text-primary' : 'hover:bg-surface/50 text-text-secondary'}`}
            >
              <div className="truncate flex-1 font-medium text-[13px]">
                {s.title}
              </div>
              <button 
                onClick={async (e) => { 
                  e.stopPropagation(); 
                  await deleteSession(s.id); 
                  if (activeSessionId === s.id) setActiveSessionId(null);
                }}
                className="opacity-0 group-hover:opacity-100 p-1 hover:text-error transition-all hover:bg-error/10 rounded"
              >
                <Trash2 size={13} />
              </button>
            </div>
          ))}
        </div>

        <div className="p-4 border-t border-border mt-auto">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-8 h-8 rounded-full bg-surface border border-border flex items-center justify-center text-sm font-bold text-primary">
              {user?.username.charAt(0).toUpperCase()}
            </div>
            <div className="truncate flex-1">
              <div className="text-sm font-medium text-text-primary truncate">{user?.username}</div>
              <div className="text-xs text-text-muted truncate">{user?.email}</div>
            </div>
          </div>
          
          {isAdmin && (
            <button 
              onClick={() => navigate('/admin')}
              className="w-full mb-1 flex flex-row items-center gap-2 text-[13px] font-medium text-text-secondary hover:text-white hover:bg-surface py-2 px-3 rounded-lg transition-colors"
            >
              <Settings size={15} /> Admin Panel
            </button>
          )}
          
          <button 
            onClick={logout}
            className="w-full flex flex-row items-center gap-2 text-[13px] font-medium text-text-secondary hover:text-error hover:bg-error/10 py-2 px-3 rounded-lg transition-colors"
          >
            <LogOut size={15} /> Logout
          </button>
        </div>
      </div>

      <div className="flex-1 flex flex-col min-w-0 bg-background relative z-0">
        {!activeSessionId ? (
          <div className="flex-1 flex flex-col items-center justify-center text-text-muted animate-in fade-in duration-500">
            <GraduationCap size={64} className="mb-4 opacity-50 text-primary" />
            <h2 className="text-xl font-medium text-text-secondary">Ask anything about your college.</h2>
            <p className="text-sm mt-2">Create a new chat to begin.</p>
          </div>
        ) : (
          <>
            <div className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8 space-y-6">
              {messages.map((m, idx) => (
                <div key={m.id || idx} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  {m.role === 'assistant' && (
                    <div className="w-8 h-8 shrink-0 bg-surface border border-border rounded-lg flex items-center justify-center text-primary mr-4 mt-1">
                      <GraduationCap size={16} />
                    </div>
                  )}
                  <div className={`max-w-[90%] sm:max-w-[75%] rounded-[20px] p-5 ${m.role === 'user' ? 'bg-primary text-white rounded-tr-md shadow-md shadow-primary/20' : 'bg-surface border border-border text-text-primary rounded-tl-md shadow-sm'}`}>
                    {m.role === 'user' ? (
                      <div className="whitespace-pre-wrap leading-relaxed text-[15px]">{m.content}</div>
                    ) : (
                      <div className="markdown-body text-[15px] leading-relaxed">
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>{m.content}</ReactMarkdown>
                      </div>
                    )}
                    
                    {m.streaming && (
                      <div className="flex gap-1.5 mt-3 mb-1">
                         <div className="w-1.5 h-1.5 bg-primary/80 rounded-full animate-bounce"></div>
                         <div className="w-1.5 h-1.5 bg-primary/80 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                         <div className="w-1.5 h-1.5 bg-primary/80 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                      </div>
                    )}
                    
                    {!m.streaming && m.sources && m.sources.length > 0 && <SourcesDisplay sources={m.sources} />}
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} className="h-36 shrink-0" />
            </div>

            <div className="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-background via-background to-transparent pt-12">
              <div className="max-w-4xl mx-auto relative">
                <form onSubmit={handleSend} className="relative flex items-center">
                  <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Ask a question..."
                    className="w-full bg-surface border border-border rounded-[20px] pl-5 pr-14 py-4 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary shadow-xl transition-all text-[15px] placeholder-text-muted"
                  />
                  <button 
                    type="submit"
                    disabled={!input.trim()}
                    className="absolute right-3 p-2 bg-primary hover:bg-primary-hover text-white rounded-xl transition-colors disabled:opacity-50 disabled:bg-surface disabled:text-text-muted"
                  >
                    <Send size={18} className="translate-x-[1px] translate-y-[1px]" />
                  </button>
                </form>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
};
