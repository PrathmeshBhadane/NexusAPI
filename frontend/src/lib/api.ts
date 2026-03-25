/**
 * API Client for AI Platform Gateway
 */

const API_BASE_URL = '';

export async function fetchApi<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;
  
  // Do not set Content-Type for FormData, the browser will set it automatically with the correct boundary
  const isFormData = typeof FormData !== 'undefined' && options.body instanceof FormData;
  
  let token = null;
  if (typeof window !== 'undefined') {
    token = localStorage.getItem('auth_token');
  }

  const headers = {
    ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const response = await fetch(url, { ...options, headers });

  if (!response.ok) {
    if (response.status === 401 && typeof window !== 'undefined') {
      localStorage.removeItem('auth_token');
      window.location.href = '/auth/login';
    }
    
    const errorText = await response.text();
    throw new Error(`API Error ${response.status}: ${errorText || response.statusText}`);
  }

  return response.json() as Promise<T>;
}

// Service Wrappers
export const aiService = {
  generateText: (prompt: string) => fetchApi<any>('/api/ai/generate', {
    method: 'POST',
    body: JSON.stringify({ prompt }),
  }),
};

export const authService = {
  login: (credentials: Record<string, string>) => fetchApi<any>('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify(credentials),
  }),
  register: (data: Record<string, string>) => fetchApi<any>('/api/auth/register', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
};

export const mlService = {
  trainModel: (modelConfig: Record<string, unknown>) => fetchApi<any>('/api/ml/train', {
    method: 'POST',
    body: JSON.stringify(modelConfig),
  }),
};

export const dataService = {
  uploadFile: (formData: FormData) => fetchApi<any>('/api/data/upload', {
    method: 'POST',
    body: formData,
  }),
};

export const keysService = {
  create: (name: string, service: string) => fetchApi<any>('/api/keys/create', {
    method: 'POST',
    body: JSON.stringify({ name, service }),
  }),
  list: () => fetchApi<any[]>('/api/keys/list', {
    method: 'GET',
  }),
  revoke: (keyId: string) => fetchApi<any>(`/api/keys/${keyId}`, {
    method: 'DELETE',
  }),
};
