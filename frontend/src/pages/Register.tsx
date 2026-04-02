import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuthContext } from '../context/AuthContext';
import { GraduationCap } from 'lucide-react';

export const Register = () => {
  const { register } = useAuthContext();
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    try {
      await register({ username, email, password });
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.message || 'Registration failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex flex-col justify-center items-center p-4">
      <div className="w-full max-w-sm bg-surface p-8 rounded-xl border border-border shadow-2xl">
        <div className="flex justify-center mb-6">
          <div className="w-12 h-12 bg-primary/20 rounded-xl flex items-center justify-center text-primary">
            <GraduationCap size={28} />
          </div>
        </div>
        <h2 className="text-2xl font-bold text-center mb-2">Create Account</h2>
        <p className="text-text-secondary text-center mb-8 text-sm">Join EduChat Pro</p>
        
        {error && <div className="mb-4 p-3 bg-error/10 border border-error/20 text-error rounded-lg text-sm">{error}</div>}
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-text-secondary mb-1">Username</label>
            <input
              type="text"
              required
              minLength={3}
              className="w-full bg-background border border-border rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-primary transition-colors"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-text-secondary mb-1">Email</label>
            <input
              type="email"
              required
              className="w-full bg-background border border-border rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-primary transition-colors"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-text-secondary mb-1">Password</label>
            <input
              type="password"
              required
              minLength={8}
              className="w-full bg-background border border-border rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-primary transition-colors"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>
          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-primary hover:bg-primary-hover text-white font-medium py-2.5 rounded-lg transition-colors mt-2 disabled:opacity-50"
          >
            {isLoading ? 'Creating...' : 'Sign Up'}
          </button>
        </form>
        
        <p className="mt-6 text-center text-sm text-text-secondary">
          Already have an account? <Link to="/login" className="text-primary hover:underline">Sign in</Link>
        </p>
      </div>
    </div>
  );
};
