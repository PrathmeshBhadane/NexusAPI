"use client";

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { authService } from '@/lib/api';
import Link from 'next/link';

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [status, setStatus] = useState({ type: '', message: '' });
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setStatus({ type: '', message: '' });
    
    try {
      const res = await authService.login({ email, password });
      setStatus({ type: 'success', message: 'Login successful! Redirecting...' });
      
      // Persist the token
      if (typeof window !== 'undefined') {
        localStorage.setItem('auth_token', res.access_token);
      }
      
      // Redirect to master dashboard
      setTimeout(() => router.push('/'), 1000);
    } catch (err: any) {
      setStatus({ type: 'error', message: err.message });
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="glass-card w-full max-w-md animate-in zoom-in-95 duration-500 mt-[-10vh]">
        
        {/* Header */}
        <div className="text-center space-y-2 mb-8 relative z-10">
          <div className="mx-auto w-12 h-12 rounded-xl bg-purple-500/20 text-purple-400 flex items-center justify-center border border-purple-500/30 mb-4 shadow-[0_0_15px_rgba(168,85,247,0.3)]">
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
            </svg>
          </div>
          <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-purple-200">
            Welcome Back
          </h1>
          <p className="text-blue-100/60 font-medium">Sign in to access the AI Gateway</p>
        </div>

        {/* Form */}
        <form onSubmit={handleLogin} className="space-y-5 relative z-10">
          <div>
            <label className="block text-sm font-medium text-blue-100/80 mb-1.5 ml-1" htmlFor="email">Email Address</label>
            <input 
              id="email" type="email" required
              className="glass-input focus:border-purple-500/50 focus:shadow-[0_0_15px_rgba(168,85,247,0.2)]"
              placeholder="you@example.com"
              value={email} onChange={e => setEmail(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-blue-100/80 mb-1.5 ml-1" htmlFor="password">Password</label>
            <input 
              id="password" type="password" required
              className="glass-input focus:border-purple-500/50 focus:shadow-[0_0_15px_rgba(168,85,247,0.2)]"
              placeholder="••••••••"
              value={password} onChange={e => setPassword(e.target.value)}
            />
          </div>

          {status.message && (
            <div className={`p-3 rounded-xl text-sm border font-medium ${status.type === 'error' ? 'bg-red-500/10 border-red-500/30 text-red-400' : 'bg-green-500/10 border-green-500/30 text-green-400'}`}>
              {status.message}
            </div>
          )}

          <button type="submit" disabled={loading} className="glass-button w-full !mt-8 text-purple-200 bg-purple-500/15 border-purple-500/30 hover:bg-purple-500/30 hover:border-purple-500/60 shadow-[0_0_20px_rgba(168,85,247,0.15)] hover:shadow-[0_0_30px_rgba(168,85,247,0.3)] disabled:opacity-50">
            {loading ? 'Authenticating...' : 'Sign In to Gateway'}
          </button>
        </form>

        {/* Footer Link */}
        <p className="mt-8 text-center text-sm text-blue-100/60 relative z-10 font-medium">
          Don't have an account?{' '}
          <Link href="/auth/register" className="text-purple-400 hover:text-purple-300 transition-colors hover:underline">
            Register for access
          </Link>
        </p>
      </div>
    </div>
  );
}
