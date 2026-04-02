import React, { useEffect, useState } from 'react';
import { useDocuments } from '../hooks/useDocuments';
import { useUsers } from '../hooks/useUsers';
import { ArrowLeft, Trash2, Upload, FileText, Settings, Users, Database, Loader2 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export const Admin = () => {
  const [activeTab, setActiveTab] = useState<'kb' | 'users'>('kb');
  const navigate = useNavigate();

  return (
    <div className="h-screen overflow-y-auto bg-background text-text-primary flex flex-col">
      <div className="border-b border-border bg-surface/50 backdrop-blur-md sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-4 h-16 flex items-center gap-4">
          <button onClick={() => navigate('/')} className="p-2.5 bg-background border border-border hover:border-primary/50 text-text-secondary hover:text-white rounded-xl transition-all shadow-sm">
            <ArrowLeft size={18} />
          </button>
          <h1 className="text-lg font-bold flex items-center gap-2.5 tracking-tight"><div className="bg-primary/20 text-primary p-1.5 rounded-lg"><Settings size={18} /></div> Admin Panel</h1>
        </div>
      </div>

      <div className="flex-1 max-w-6xl w-full mx-auto p-4 md:p-8 flex flex-col lg:flex-row gap-8">
        <div className="w-full lg:w-64 shrink-0 flex flex-row lg:flex-col gap-2 overflow-x-auto pb-2 lg:pb-0 hide-scrollbar">
          <button 
            onClick={() => setActiveTab('kb')}
            className={`flex items-center gap-3 px-4 py-3.5 rounded-xl font-medium transition-all text-sm whitespace-nowrap ${activeTab === 'kb' ? 'bg-primary text-white shadow-lg shadow-primary/20' : 'hover:bg-surface text-text-secondary hover:text-white'}`}
          >
            <Database size={18} /> Knowledge Base
          </button>
          <button 
            onClick={() => setActiveTab('users')}
            className={`flex items-center gap-3 px-4 py-3.5 rounded-xl font-medium transition-all text-sm whitespace-nowrap ${activeTab === 'users' ? 'bg-primary text-white shadow-lg shadow-primary/20' : 'hover:bg-surface text-text-secondary hover:text-white'}`}
          >
            <Users size={18} /> User Management
          </button>
        </div>

        <div className="flex-1 min-w-0 pb-12">
          {activeTab === 'kb' && <KnowledgeBaseTab />}
          {activeTab === 'users' && <UsersTab />}
        </div>
      </div>
    </div>
  );
};

const KnowledgeBaseTab = () => {
  const { documents, fetchDocuments, uploadFile, uploadText, deleteDocument } = useDocuments();
  const [textInput, setTextInput] = useState('');
  const [filename, setFilename] = useState('');
  const [isUploading, setIsUploading] = useState(false);

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  useEffect(() => {
    const hasProcessing = documents.some(d => d.status === 'processing');
    if (!hasProcessing) return;
    const interval = setInterval(() => {
      fetchDocuments();
    }, 3000);
    return () => clearInterval(interval);
  }, [documents, fetchDocuments]);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setIsUploading(true);
    try {
      await uploadFile(file);
      await fetchDocuments();
    } catch (err: any) {
      alert(err.message || 'Upload failed');
    } finally {
      setIsUploading(false);
      e.target.value = '';
    }
  };

  const handleTextUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!textInput.trim() || !filename.trim()) return;
    setIsUploading(true);
    try {
      await uploadText(textInput, filename + '.txt');
      setTextInput('');
      setFilename('');
      await fetchDocuments();
    } catch (err: any) {
      alert(err.message || 'Failed to save text');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      <div className="bg-surface rounded-2xl border border-border p-6 md:p-8 shadow-sm">
        <h2 className="text-[17px] font-bold mb-6 flex items-center gap-2"><Upload size={18} className="text-primary"/> Upload Knowledge Hub</h2>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="border-2 border-dashed border-border/70 rounded-2xl p-8 flex flex-col items-center justify-center text-center hover:border-primary/50 hover:bg-background/30 transition-all relative min-h-[220px]">
            <input 
              type="file" 
              accept=".pdf,.docx,.txt" 
              onChange={handleFileUpload} 
              disabled={isUploading}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer disabled:cursor-not-allowed" 
            />
            <div className={`w-14 h-14 rounded-2xl flex items-center justify-center mb-5 shadow-sm transition-colors ${isUploading ? 'bg-primary/20 text-primary animate-pulse' : 'bg-background border border-border text-text-secondary'}`}>
              <Upload size={24} />
            </div>
            <p className="font-medium text-text-primary">Click or drag file to upload</p>
            <p className="text-xs text-text-muted mt-1.5 font-medium">PDF, DOCX, TXT (up to 10MB)</p>
            {isUploading && <p className="text-primary text-sm mt-4 flex items-center gap-2 font-medium bg-primary/10 px-3 py-1.5 rounded-lg"><Loader2 size={14} className="animate-spin" /> Uploading block...</p>}
          </div>

          <form onSubmit={handleTextUpload} className="flex flex-col gap-3.5 h-full">
            <input
              type="text"
              placeholder="Title for this snippet (e.g., 'Physics Timetable')"
              value={filename}
              onChange={(e) => setFilename(e.target.value)}
              className="w-full bg-background border border-border rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary shadow-sm transition-colors"
              required
            />
            <textarea
              placeholder="Paste raw text knowledge here..."
              value={textInput}
              onChange={(e) => setTextInput(e.target.value)}
              className="w-full bg-background border border-border rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary shadow-sm transition-colors flex-1 min-h-[120px] resize-none"
              required
            />
            <button 
              type="submit" 
              disabled={isUploading || !textInput.trim()}
              className="w-full bg-primary hover:bg-primary-hover text-white font-medium py-3 rounded-xl transition-colors disabled:opacity-50 disabled:bg-surface disabled:text-text-muted shadow-lg shadow-primary/20"
            >
              Inject Text into Cortex
            </button>
          </form>
        </div>
      </div>

      <div className="bg-surface rounded-2xl border border-border overflow-hidden shadow-sm">
        <div className="px-6 py-5 border-b border-border flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 bg-background/20">
          <h2 className="font-bold flex items-center gap-2"><Database size={18} className="text-primary"/> Indexed Context Blocks</h2>
          <div className="text-xs font-semibold bg-primary/10 text-primary px-3 py-1.5 rounded-lg border border-primary/20">{documents.length} ITEMS</div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm whitespace-nowrap">
            <thead>
              <tr className="text-text-muted border-b border-border/50 bg-background/30">
                <th className="px-6 py-4 font-semibold text-xs tracking-wider uppercase">Filename</th>
                <th className="px-6 py-4 font-semibold text-xs tracking-wider uppercase">Chunks</th>
                <th className="px-6 py-4 font-semibold text-xs tracking-wider uppercase">Status</th>
                <th className="px-6 py-4 font-semibold text-xs tracking-wider uppercase text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/50">
              {documents.length === 0 ? (
                <tr>
                  <td colSpan={4} className="px-6 py-12 text-center text-text-muted">No documents ingested into the cortex yet.</td>
                </tr>
              ) : documents.map((doc) => (
                <tr key={doc.id} className="hover:bg-background/40 transition-colors group">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3 font-medium">
                      <div className="w-8 h-8 rounded-lg bg-background border border-border flex items-center justify-center text-text-secondary group-hover:text-primary transition-colors">
                        <FileText size={14} />
                      </div>
                      <span className="truncate max-w-[200px]">{doc.filename}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-text-secondary font-medium">{doc.chunk_count ?? '-'} block(s)</td>
                  <td className="px-6 py-4">
                    {doc.status === 'processing' && (
                      <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[11px] font-bold uppercase tracking-wider bg-primary/10 text-primary border border-primary/20">
                        <Loader2 size={12} className="animate-spin" /> Ingesting
                      </span>
                    )}
                    {doc.status === 'ready' && (
                      <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[11px] font-bold uppercase tracking-wider bg-success/10 text-success border border-success/20">
                        <div className="w-1.5 h-1.5 rounded-full bg-success"></div> Ready
                      </span>
                    )}
                    {doc.status === 'failed' && (
                      <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[11px] font-bold uppercase tracking-wider bg-error/10 text-error border border-error/20">
                        <div className="w-1.5 h-1.5 rounded-full bg-error"></div> Failed
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <button 
                      onClick={() => { if(confirm('Purge document from DB and Vector Store?')) deleteDocument(doc.id); }}
                      className="text-text-muted hover:text-error hover:bg-error/10 p-2 rounded-lg transition-all"
                      title="Delete document"
                    >
                      <Trash2 size={16} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

const UsersTab = () => {
  const { users, fetchUsers, deleteUser } = useUsers();

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  return (
    <div className="bg-surface rounded-2xl border border-border overflow-hidden shadow-sm animate-in fade-in duration-300">
      <div className="px-6 py-5 border-b border-border bg-background/20 flex items-center justify-between">
        <h2 className="font-bold flex items-center gap-2"><Users size={18} className="text-primary"/> Personnel Authorization</h2>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm whitespace-nowrap">
          <thead>
            <tr className="text-text-muted border-b border-border/50 bg-background/30">
              <th className="px-6 py-4 font-semibold text-xs tracking-wider uppercase">Username</th>
              <th className="px-6 py-4 font-semibold text-xs tracking-wider uppercase">Email</th>
              <th className="px-6 py-4 font-semibold text-xs tracking-wider uppercase">Clearance</th>
              <th className="px-6 py-4 font-semibold text-xs tracking-wider uppercase">Status</th>
              <th className="px-6 py-4 font-semibold text-xs tracking-wider uppercase text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border/50">
            {users.map((u) => (
              <tr key={u.id} className="hover:bg-background/40 transition-colors">
                <td className="px-6 py-4 font-medium">{u.username}</td>
                <td className="px-6 py-4 text-text-secondary">{u.email}</td>
                <td className="px-6 py-4">
                  <span className={`inline-flex px-2.5 py-1.5 rounded-lg text-[11px] uppercase tracking-wider font-bold ${u.role === 'admin' ? 'bg-primary/20 text-primary border border-primary/30' : 'bg-background border border-border text-text-secondary'}`}>
                    {u.role}
                  </span>
                </td>
                <td className="px-6 py-4">
                  {u.is_deleted ? (
                    <span className="text-error text-xs font-semibold bg-error/10 px-2.5 py-1 rounded-lg border border-error/20">Terminated</span>
                  ) : (
                    <span className="text-success text-xs font-semibold bg-success/10 px-2.5 py-1 rounded-lg border border-success/20">Active</span>
                  )}
                </td>
                <td className="px-6 py-4 text-right">
                  <button 
                    onClick={() => { if(confirm('Soft delete user?')) deleteUser(u.id); }}
                    disabled={u.role === 'admin' || u.is_deleted}
                    className="text-text-muted hover:text-error hover:bg-error/10 p-2 rounded-lg transition-all disabled:opacity-30 disabled:hover:bg-transparent disabled:hover:text-text-muted"
                  >
                    <Trash2 size={16} />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
