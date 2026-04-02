import { useState, useCallback } from 'react';
import api from '../api/axiosInstance';
import type { ChatSession, AppError } from '../types';

export function useSessions() {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<AppError | null>(null);

  const fetchSessions = useCallback(async (page = 1, limit = 20) => {
    setIsLoading(true);
    setError(null);
    try {
      const { data } = await api.get(`/sessions?page=${page}&limit=${limit}`);
      setSessions(data.items);
    } catch (err: any) {
      setError(err.response?.data || { message: 'Failed to fetch sessions' });
    } finally {
      setIsLoading(false);
    }
  }, []);

  const createSession = async (title: string) => {
    try {
      const { data } = await api.post('/sessions', { title });
      setSessions(prev => [data, ...prev]);
      return data;
    } catch (err: any) {
      setError(err.response?.data || { message: 'Failed to create session' });
      throw err;
    }
  };

  const deleteSession = async (id: string) => {
    try {
      await api.delete(`/sessions/${id}`);
      setSessions(prev => prev.filter(s => s.id !== id));
    } catch (err: any) {
      setError(err.response?.data || { message: 'Failed to delete session' });
      throw err;
    }
  };

  return { sessions, isLoading, error, fetchSessions, createSession, deleteSession };
}
