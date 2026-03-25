"use client";

import React, { useState, useEffect } from 'react';
import { keysService } from '@/lib/api';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

export default function Home() {
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isAuthLoading, setIsAuthLoading] = useState(true);

  // Portal States
  const [apiKeys, setApiKeys] = useState<any[]>([]);
  const [newKeyName, setNewKeyName] = useState('');
  const [newKeyService, setNewKeyService] = useState('all');
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [generatedKey, setGeneratedKey] = useState<{key: string, name: string, service: string} | null>(null);

  const SCOPE_OPTIONS = [
    { value: 'all', label: 'Unlimited (All Services)' },
    { value: 'ai', label: 'AI Content Generator Only' },
    { value: 'ml', label: 'Machine Learning Jobs Only' },
    { value: 'data', label: 'Data Processing Engine Only' },
  ];
  const [loadingKeys, setLoadingKeys] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('auth_token');
      if (token) {
        setIsAuthenticated(true);
        fetchSettings();
      }
      setIsAuthLoading(false);
    }
  }, []);

  const fetchSettings = async () => {
    setLoadingKeys(true);
    try {
      const keys = await keysService.list();
      setApiKeys(keys || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingKeys(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    setIsAuthenticated(false);
    router.refresh();
  };

  const handleCreateKey = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newKeyName.trim()) return;
    setErrorMsg('');
    try {
      // Create utilizing our new scoping infrastructure
      const res = await keysService.create(newKeyName, newKeyService);
      setGeneratedKey({ key: res.key, name: res.name, service: res.service });
      setNewKeyName('');
      setNewKeyService('all');
      fetchSettings();
    } catch (err: any) {
      setErrorMsg(err.message);
    }
  };

  const handleRevokeKey = async (keyId: string) => {
    try {
      await keysService.revoke(keyId);
      fetchSettings();
    } catch (err: any) {
      alert("Failed to revoke: " + err.message);
    }
  };

  if (isAuthLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-8 h-8 rounded-full border-4 border-neon-blue border-t-transparent animate-spin"></div>
      </div>
    );
  }

  return (
    <main className="min-h-screen p-8 sm:p-20 font-sans relative">
      
      {/* Top Navbar / Logout */}
      {isAuthenticated && (
        <div className="absolute top-8 right-8 animate-in fade-in duration-500">
          <button 
            onClick={handleLogout}
            className="px-4 py-2 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 hover:bg-red-500/20 transition-all font-medium text-sm flex items-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" /></svg>
            Sign Out
          </button>
        </div>
      )}

      <div className="max-w-6xl mx-auto space-y-16">
        
        {/* Header Section */}
        <header className="flex flex-col items-center text-center space-y-6 animate-in slide-in-from-bottom-8 duration-700">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass border-neon-blue/30 text-neon-blue text-sm font-semibold tracking-wide shadow-[0_0_15px_rgba(58,134,255,0.2)]">
            <span className="w-2 h-2 rounded-full bg-neon-blue animate-pulse" />
            Developer Hub
          </div>
          <h1 className="text-5xl md:text-7xl font-bold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-white via-blue-100 to-space-blue-light drop-shadow-lg">
            AI Platform APIs
          </h1>
          <p className="max-w-2xl text-lg text-blue-200/70 font-medium">
            Generate secure API keys scoped specifically to the microservices you need for your projects.
          </p>
        </header>

        {!isAuthenticated ? (
          /* Unauthenticated View */
          <div className="flex flex-col items-center justify-center space-y-8 animate-in zoom-in-95 duration-500 mt-12">
            <div className="glass-card max-w-lg w-full text-center p-10 border border-neon-blue/40 shadow-[0_0_40px_rgba(58,134,255,0.15)]">
               <h2 className="text-2xl font-bold text-white mb-2">Student Access Required</h2>
               <p className="text-blue-100/60 mb-8 leading-relaxed">
                 You must register or log in to generate scoped API keys and view endpoint documentation.
               </p>
               <div className="flex flex-col sm:flex-row gap-4 w-full justify-center">
                 <Link href="/auth/register" className="glass-button flex-1 py-3 text-white border-white/20 hover:border-white/50 text-center justify-center">
                   Register For Keys
                 </Link>
                 <Link href="/auth/login" className="glass-button flex-1 py-3 bg-neon-blue/20 border-neon-blue/50 hover:bg-neon-blue/30 text-neon-blue text-center justify-center shadow-[0_0_15px_rgba(58,134,255,0.3)]">
                   Log In to Dashboard
                 </Link>
               </div>
            </div>
          </div>
        ) : (
          /* Authenticated Developer View */
          <div className="space-y-12 animate-in slide-in-from-bottom-12 duration-1000 delay-150">
            
            {/* API Keys Management Block */}
            <div className="glass-card flex flex-col gap-6 border border-white/10 shadow-lg" style={{ position: 'relative' }}>
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4" style={{ position: 'relative', zIndex: 9999 }}>
                <div>
                  <h2 className="text-2xl font-bold text-white mb-1">My API Keys</h2>
                  <p className="text-sm text-blue-100/60 font-medium">Generate heavily restricted service keys or universal keys.</p>
                </div>
                
                <div className="relative flex-shrink-0" style={{ zIndex: 9999 }}>
                  <label className="block text-xs font-semibold text-blue-200/50 mb-1 ml-1 uppercase tracking-wider text-right">Target Scope</label>
                  <button 
                    type="button"
                    onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                    className="glass-input focus:border-neon-blue/80 bg-[#0a0f24] text-white min-w-[240px] w-full flex items-center justify-between text-left transition-all duration-300 rounded-xl"
                  >
                    <span className="truncate pr-2">{SCOPE_OPTIONS.find(o => o.value === newKeyService)?.label}</span>
                    <svg className={`w-4 h-4 flex-shrink-0 transition-transform duration-500 text-neon-blue ${isDropdownOpen ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" /></svg>
                  </button>
                  
                  {isDropdownOpen && (
                    <>
                      {/* Invisible backdrop to catch outside clicks */}
                      <div className="fixed inset-0" style={{ zIndex: 9998 }} onClick={() => setIsDropdownOpen(false)} />
                      
                      {/* Floating Menu */}
                      <div 
                        className="absolute top-full right-0 w-full md:w-[280px] mt-2 backdrop-blur-3xl border border-neon-blue/60 rounded-xl overflow-hidden shadow-[0_15px_50px_rgba(0,0,0,0.8)]"
                        style={{ zIndex: 9999, backgroundColor: 'rgba(10, 15, 36, 0.98)' }}
                      >
                        {SCOPE_OPTIONS.map((option) => (
                          <button
                            key={option.value}
                            type="button"
                            onClick={() => {
                              setNewKeyService(option.value);
                              setIsDropdownOpen(false);
                            }}
                            className={`w-full text-left px-5 py-3 text-sm transition-all duration-200 ${
                              newKeyService === option.value 
                                ? 'bg-neon-blue/15 text-white font-bold border-l-2 border-neon-blue' 
                                : 'text-blue-100/70 hover:bg-white/5 hover:text-white border-l-2 border-transparent'
                            }`}
                          >
                            {option.label}
                          </button>
                        ))}
                      </div>
                    </>
                  )}
                </div>
              </div>

              {/* Secure Generated Key Banner */}
              {generatedKey && (
                <div className="bg-green-500/20 border-2 border-green-500/50 p-6 md:p-8 rounded-2xl space-y-4 relative overflow-hidden shadow-[0_0_40px_rgba(34,197,94,0.15)] animate-in slide-in-from-top-4 fade-in duration-500">
                  <div className="absolute top-0 left-0 w-2 h-full bg-green-500 shadow-[0_0_20px_rgba(34,197,94,1)]"></div>
                  <h3 className="text-green-400 font-extrabold text-2xl mb-1">Make sure you copy your API key now!</h3>
                  <p className="text-green-100/90 text-base">You won't be able to see it again. It has access rights strictly targeting: <span className="font-bold text-white capitalize bg-green-500/30 px-3 py-1 rounded ml-2 shadow-inner">{generatedKey.service}</span></p>
                  <div className="bg-black/60 font-mono text-green-300 p-6 rounded-xl mt-4 flex items-center justify-between border border-green-500/40 shadow-inner">
                    <span className="truncate mr-4 font-bold text-2xl tracking-widest break-all">{generatedKey.key}</span>
                  </div>
                  <button onClick={() => setGeneratedKey(null)} className="mt-4 px-5 py-2.5 bg-green-500/20 rounded-lg text-sm text-green-300 hover:text-white hover:bg-green-500/40 font-bold transition-all border border-green-500/30">Dismiss Warning</button>
                </div>
              )}

              {/* Generate Key Form */}
              <form onSubmit={handleCreateKey} className="flex flex-col sm:flex-row gap-4 items-end" style={{ position: 'relative', zIndex: 1 }}>
                <div className="flex-grow">
                  <label className="block text-xs font-semibold text-blue-200/50 mb-1 ml-1 uppercase tracking-wider">New Key Label</label>
                  <input 
                    type="text" 
                    placeholder="e.g. CS201 Final Project" 
                    value={newKeyName} onChange={e => setNewKeyName(e.target.value)}
                    className="glass-input focus:border-neon-blue/80 w-full" 
                  />
                </div>
                <button type="submit" disabled={!newKeyName.trim()} className="glass-button py-[14px] bg-neon-blue/20 text-neon-blue hover:bg-neon-blue/30 whitespace-nowrap min-w-[180px]">
                  Generate Token
                </button>
              </form>

              {errorMsg && <p className="text-red-400 text-sm bg-red-500/10 p-2 rounded">{errorMsg}</p>}

              {/* API Keys Table */}
              <div className="overflow-hidden rounded-xl border border-white/5 bg-black/20">
                {loadingKeys ? (
                  <div className="p-8 text-center text-blue-200/50">Loading keys...</div>
                ) : apiKeys.length === 0 ? (
                   <div className="p-8 text-center text-blue-200/50 text-sm">You haven't generated any API keys yet.</div>
                ) : (
                  <table className="w-full text-left text-sm text-blue-100/80">
                    <thead className="bg-white/5 text-blue-200 border-b border-white/10 uppercase font-semibold text-xs tracking-wider">
                      <tr>
                        <th className="px-6 py-4">Key Label</th>
                        <th className="px-6 py-4">Access Scope</th>
                        <th className="px-6 py-4 text-center">Lifetime Requests</th>
                        <th className="px-6 py-4 text-center">Hourly Bandwidth</th>
                        <th className="px-6 py-4">Prefix</th>
                        <th className="px-6 py-4 text-right">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                      {apiKeys.map(key => (
                        <tr key={key.id} className="hover:bg-white/[0.02] transition-colors">
                          <td className="px-6 py-4 font-medium text-white">{key.name}</td>
                          <td className="px-6 py-4 font-medium">
                            <span className="px-2 py-1 rounded bg-blue-500/20 text-blue-300 text-xs font-bold uppercase tracking-wider border border-blue-500/30">
                              {key.service === 'all' ? 'Universal' : key.service}
                            </span>
                          </td>
                          <td className="px-6 py-4 text-center">
                            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-blue-200 font-mono text-xs shadow-inner shadow-black/50">
                               <svg className="w-3.5 h-3.5 text-neon-blue" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg>
                               {key.total_requests?.toLocaleString() || '0'}
                            </div>
                          </td>
                          <td className="px-6 py-4 text-center">
                            <div className="w-full max-w-[120px] mx-auto bg-black/60 rounded-full h-4 border border-white/10 overflow-hidden relative shadow-inner">
                               <div 
                                 className={`absolute top-0 left-0 h-full transition-all duration-1000 ${key.hourly_requests >= 100 ? 'bg-red-500' : key.hourly_requests >= 75 ? 'bg-orange-500' : 'bg-green-500'}`} 
                                 style={{ width: `${Math.min((key.hourly_requests / 100) * 100, 100)}%` }}
                               ></div>
                               <span className="absolute inset-0 flex items-center justify-center text-[10px] font-bold text-white uppercase mix-blend-difference tracking-widest">{key.hourly_requests || 0} / 100</span>
                            </div>
                          </td>
                          <td className="px-6 py-4 font-mono text-blue-300/80 text-xs">{key.prefix}••••••••</td>
                          <td className="px-6 py-4 text-right">
                            <button 
                              onClick={() => handleRevokeKey(key.id)}
                              className="text-red-400 hover:text-red-300 bg-red-500/10 hover:bg-red-500/20 px-3 py-1.5 rounded-md transition-colors font-semibold"
                            >
                              Revoke
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            </div>

            {/* Documentation Section */}
            <div>
              <h2 className="text-2xl font-bold text-white mb-6 uppercase tracking-widest text-center mt-12 bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-neon-blue">
                Target Backend Catalog
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                
                {/* AI Endpoint Doc */}
                <div className="glass-card flex flex-col gap-4 border-orange-500/20">
                  <div className="flex items-center gap-3 border-b border-white/5 pb-3">
                    <span className="px-2 py-1 bg-orange-500/20 text-orange-400 rounded text-xs font-bold font-mono">POST</span>
                    <h3 className="font-bold text-white text-lg">/ai/generate</h3>
                  </div>
                  <p className="text-sm text-blue-100/60">Generate text responses utilizing high-performance NLP models. Note the required Gateway `X-API-Key` standard header.</p>
                  <div className="bg-[#0b1021] border border-white/10 rounded-lg p-4 font-mono text-xs text-blue-300 overflow-x-auto mt-auto leading-relaxed">
                    <span className="text-pink-400">curl</span> -X POST http://localhost:8000/ai/generate \<br/>
                    &nbsp;&nbsp;-H <span className="text-green-300">"X-API-Key: YOUR_API_KEY"</span> \<br/>
                    &nbsp;&nbsp;-H <span className="text-green-300">"Content-Type: application/json"</span> \<br/>
                    &nbsp;&nbsp;-d <span className="text-yellow-300">'&#123;"prompt": "Explain quantum computing", "model": "llama-3.1-8b-instant"&#125;'</span>
                  </div>
                </div>

                {/* ML Endpoint Doc */}
                <div className="glass-card flex flex-col gap-4 border-green-500/20">
                  <div className="flex items-center gap-3 border-b border-white/5 pb-3">
                    <span className="px-2 py-1 bg-green-500/20 text-green-400 rounded text-xs font-bold font-mono">POST</span>
                    <h3 className="font-bold text-white text-lg">/ml/train</h3>
                  </div>
                  <p className="text-sm text-blue-100/60">Dispatch asynchronous long-running model training jobs to RabbitMQ workers securely.</p>
                  <div className="bg-[#0b1021] border border-white/10 rounded-lg p-4 font-mono text-xs text-blue-300 overflow-x-auto mt-auto leading-relaxed">
                    <span className="text-pink-400">curl</span> -X POST http://localhost:8000/ml/train \<br/>
                    &nbsp;&nbsp;-H <span className="text-green-300">"X-API-Key: YOUR_API_KEY"</span> \<br/>
                    &nbsp;&nbsp;-H <span className="text-green-300">"Content-Type: application/json"</span> \<br/>
                    &nbsp;&nbsp;-d <span className="text-yellow-300">'&#123;"name": "my-classifier", "model_type": "xgboost"&#125;'</span>
                  </div>
                </div>

                {/* AI Chat Endpoint Doc */}
                <div className="glass-card flex flex-col gap-4 border-indigo-500/20">
                  <div className="flex items-center gap-3 border-b border-white/5 pb-3">
                    <span className="px-2 py-1 bg-indigo-500/20 text-indigo-400 rounded text-xs font-bold font-mono">POST</span>
                    <h3 className="font-bold text-white text-lg">/ai/chat</h3>
                  </div>
                  <p className="text-sm text-blue-100/60">Pass a conversational state array to execute continuous multi-turn system integrations.</p>
                  <div className="bg-[#0b1021] border border-white/10 rounded-lg p-4 font-mono text-xs text-blue-300 overflow-x-auto mt-auto leading-relaxed">
                    <span className="text-pink-400">curl</span> -X POST http://localhost:8000/ai/chat \<br/>
                    &nbsp;&nbsp;-H <span className="text-green-300">"X-API-Key: YOUR_API_KEY"</span> \<br/>
                    &nbsp;&nbsp;-H <span className="text-green-300">"Content-Type: application/json"</span> \<br/>
                    &nbsp;&nbsp;-d <span className="text-yellow-300">'&#123;"messages": [&#123;"role":"user", "content":"Hello!"&#125;]&#125;'</span>
                  </div>
                </div>

                {/* Data Clean Endpoint Doc */}
                <div className="glass-card flex flex-col gap-4 border-purple-500/20">
                  <div className="flex items-center gap-3 border-b border-white/5 pb-3">
                    <span className="px-2 py-1 bg-purple-500/20 text-purple-400 rounded text-xs font-bold font-mono">POST</span>
                    <h3 className="font-bold text-white text-lg">/data/clean/&#123;id&#125;</h3>
                  </div>
                  <p className="text-sm text-blue-100/60">Execute Pandas dataframe pre-processing commands dynamically against stored Postgres datasets.</p>
                  <div className="bg-[#0b1021] border border-white/10 rounded-lg p-4 font-mono text-xs text-blue-300 overflow-x-auto mt-auto leading-relaxed">
                    <span className="text-pink-400">curl</span> -X POST http://localhost:8000/data/clean/your-uuid \<br/>
                    &nbsp;&nbsp;-H <span className="text-green-300">"X-API-Key: YOUR_API_KEY"</span> \<br/>
                    &nbsp;&nbsp;-H <span className="text-green-300">"Content-Type: application/json"</span> \<br/>
                    &nbsp;&nbsp;-d <span className="text-yellow-300">'&#123;"drop_duplicates": true, "drop_nulls": false&#125;'</span>
                  </div>
                </div>

              </div>
            </div>

          </div>
        )}

      </div>
    </main>
  );
}
