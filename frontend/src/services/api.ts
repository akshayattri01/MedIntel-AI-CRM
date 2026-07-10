import axios from 'axios';
import type { AIChatResponse, HCP, Interaction, User } from '../types';

export const api = axios.create({ baseURL: import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api/v1' });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('medintel_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;
    const refreshToken = localStorage.getItem('medintel_refresh_token');
    if (error.response?.status === 401 && refreshToken && !original._retry && !original.url?.includes('/auth/refresh')) {
      original._retry = true;
      const { data } = await api.post('/auth/refresh', { refresh_token: refreshToken });
      localStorage.setItem('medintel_token', data.access_token);
      localStorage.setItem('medintel_refresh_token', data.refresh_token);
      original.headers.Authorization = `Bearer ${data.access_token}`;
      return api(original);
    }
    return Promise.reject(error);
  }
);

export const crmApi = {
  createHcp: (payload: Omit<HCP, 'id' | 'sentiment_score' | 'last_contacted_at' | 'interaction_count'>) => api.post('/hcp', payload),
  updateHcp: (id: string, payload: Partial<HCP>) => api.patch(`/hcp/${id}`, payload),
  deleteHcp: (id: string) => api.delete(`/hcp/${id}`),
  hcpHistory: (id: string) => api.get<Interaction[]>(`/hcp/${id}/interactions`),
  createInteraction: (payload: Partial<Interaction> & { hcp_name?: string }) => api.post('/interactions', payload),
  updateInteraction: (id: string, payload: Partial<Interaction>) => api.patch(`/interactions/${id}`, payload),
  deleteInteraction: (id: string) => api.delete(`/interactions/${id}`),
  updateProfile: (payload: Partial<User>) => api.patch('/users/me', payload),
  settings: () => api.get('/users/settings'),
};
// ================= AI =================

export const aiApi = {
  chat: (message: string) =>
    api.post<AIChatResponse>("/ai/chat", {
      message,
    }),

  streamChat: (message: string) =>
    fetch(`${import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1"}/ai/chat/stream`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${localStorage.getItem("medintel_token")}`,
      },
      body: JSON.stringify({ message }),
    }),
};
