"use client";

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { authService } from '@/lib/api';
import Link from 'next/link';

export default function RegisterPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [status, setStatus] = useState({ type: '', message: '' });
  const [loading, setLoading] = useState(false);

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setStatus({ type: '', message: '' });
    
    try {
      const res = await authService.register({ email, username, password });
      setStatus({ type: 'success', message: 'Registration successful! Logging you in...' });
      
      // Persist the token generated from registration
      if (typeof window !== 'undefined' && res.access_token) {
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
      <div className="glass-card w-full max-w-md animate-in zoom-in-95 duration-500">
        
        {/* Header */}
        <div className="text-center space-y-2 mb-8 relative z-10">
          <div className="mx-auto w-12 h-12 rounded-xl bg-orange-500/20 text-orange-400 flex items-center justify-center border border-orange-500/30 mb-4 shadow-[0_0_15px_rgba(249,115,22,0.3)]">
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
            </svg>
          </div>
          <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-orange-200">
            Create Account
          </h1>
          <p className="text-blue-100/60 font-medium">Join the next-generation AI platform</p>
        </div>

        {/* Form */}
        <form onSubmit={handleRegister} className="space-y-5 relative z-10">
          <div>
            <label className="block text-sm font-medium text-blue-100/80 mb-1.5 ml-1" htmlFor="email">Email Address</label>
            <input 
              id="email" type="email" required
              className="glass-input focus:border-orange-500/50 focus:shadow-[0_0_15px_rgba(249,115,22,0.2)]"
              placeholder="you@example.com"
              value={email} onChange={e => setEmail(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-blue-100/80 mb-1.5 ml-1" htmlFor="username">Username</label>
            <input 
              id="username" type="text" required
              className="glass-input focus:border-orange-500/50 focus:shadow-[0_0_15px_rgba(249,115,22,0.2)]"
              placeholder="DeveloperNinja"
              value={username} onChange={e => setUsername(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-blue-100/80 mb-1.5 ml-1" htmlFor="password">Password</label>
            <input 
              id="password" type="password" required minLength={8}
              className="glass-input focus:border-orange-500/50 focus:shadow-[0_0_15px_rgba(249,115,22,0.2)]"
              placeholder="••••••••"
              value={password} onChange={e => setPassword(e.target.value)}
            />
          </div>

          {status.message && (
            <div className={`p-3 rounded-xl text-sm border font-medium ${status.type === 'error' ? 'bg-red-500/10 border-red-500/30 text-red-400' : 'bg-green-500/10 border-green-500/30 text-green-400'}`}>
              {status.message}
            </div>
          )}

          <button type="submit" disabled={loading} className="glass-button w-full !mt-8 text-orange-200 bg-orange-500/15 border-orange-500/30 hover:bg-orange-500/30 hover:border-orange-500/60 shadow-[0_0_20px_rgba(249,115,22,0.15)] hover:shadow-[0_0_30px_rgba(249,115,22,0.3)] disabled:opacity-50">
            {loading ? 'Creating Account...' : 'Register Access Node'}
          </button>
        </form>

        {/* Footer Link */}
        <p className="mt-8 text-center text-sm text-blue-100/60 relative z-10 font-medium">
          Already have an account?{' '}
          <Link href="/auth/login" className="text-orange-400 hover:text-orange-300 transition-colors hover:underline">
            Sign In here
          </Link>
        </p>
      </div>
    </div>
  );
}
