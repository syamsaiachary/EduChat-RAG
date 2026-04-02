import { useState, useCallback } from 'react';
import api from '../api/axiosInstance';
import type { User, AppError } from '../types';

export function useUsers() {
  const [users, setUsers] = useState<User[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<AppError | null>(null);

  const fetchUsers = useCallback(async (page = 1, limit = 20) => {
    setIsLoading(true);
    try {
      const { data } = await api.get(`/users?page=${page}&limit=${limit}`);
      setUsers(data.items);
    } catch (err: any) {
      setError(err.response?.data || { message: 'Failed to fetch users' });
    } finally {
      setIsLoading(false);
    }
  }, []);

  const deleteUser = async (id: string) => {
    try {
      await api.delete(`/users/${id}`);
      setUsers(prev => prev.map(u => u.id === id ? { ...u, is_deleted: true } : u));
    } catch (err: any) {
      throw err.response?.data || { message: 'Failed to delete user' };
    }
  };

  return { users, isLoading, error, fetchUsers, deleteUser };
}
