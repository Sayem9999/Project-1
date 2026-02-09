export const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? 'http://localhost:8000/api';

export function wsBaseFromApi(apiBase: string = API_BASE): string {
  if (apiBase.startsWith('https://')) return apiBase.replace('https://', 'wss://');
  if (apiBase.startsWith('http://')) return apiBase.replace('http://', 'ws://');
  return apiBase;
}

export async function apiFetch(path: string, options: RequestInit = {}) {
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
  const headers = new Headers(options.headers);
  headers.set('Content-Type', 'application/json');
  if (token) headers.set('Authorization', `Bearer ${token}`);
  return fetch(`${API_BASE}${path}`, { ...options, headers });
}
