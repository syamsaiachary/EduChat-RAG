export interface User {
  id: string;
  username: string;
  email: string;
  role: 'user' | 'admin';
  is_deleted: boolean;
  created_at: string;
}

export interface ChatSession {
  id: string;
  user_id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface Message {
  id?: string;
  session_id?: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: any[];
  created_at?: string;
  streaming?: boolean;
}

export interface Document {
  id: string;
  filename: string;
  file_type: string;
  file_size_bytes?: number;
  chunk_count?: number;
  status: 'processing' | 'ready' | 'failed';
  uploaded_by: string;
  created_at: string;
}

export interface AppError {
  error: boolean;
  code: string;
  message: string;
  status_code: number;
}
