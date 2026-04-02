import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuthContext } from '../context/AuthContext';

export const AdminRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, isAdmin, isLoading } = useAuthContext();

  if (isLoading) {
    return (
      <div className="h-screen w-screen flex items-center justify-center bg-[#0A0A0A]">
        <div className="w-8 h-8 rounded-full border-2 border-[#F97316] border-t-transparent animate-spin"></div>
      </div>
    );
  }

  if (!user || !isAdmin) {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
};
