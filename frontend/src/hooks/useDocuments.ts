import { useState, useCallback } from 'react';
import api from '../api/axiosInstance';
import  type { Document, AppError } from '../types';

export function useDocuments() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<AppError | null>(null);

  const fetchDocuments = useCallback(async (page = 1, limit = 20) => {
    setIsLoading(true);
    try {
      const { data } = await api.get(`/documents?page=${page}&limit=${limit}`);
      setDocuments(data.items);
    } catch (err: any) {
      setError(err.response?.data || { message: 'Failed to fetch documents' });
    } finally {
      setIsLoading(false);
    }
  }, []);

  const uploadFile = async (file: File) => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const { data } = await api.post('/documents/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      return data;
    } catch (err: any) {
      throw err.response?.data || { message: 'Upload failed' };
    }
  };

  const uploadText = async (text: string, filename: string) => {
    try {
      const { data } = await api.post('/documents/text', { text, filename });
      return data;
    } catch (err: any) {
      throw err.response?.data || { message: 'Text add failed' };
    }
  };

  const deleteDocument = async (id: string) => {
    try {
      await api.delete(`/documents/${id}`);
      setDocuments(prev => prev.filter(d => d.id !== id));
    } catch (err: any) {
      throw err.response?.data || { message: 'Delete failed' };
    }
  };

  return { documents, isLoading, error, fetchDocuments, uploadFile, uploadText, deleteDocument };
}
