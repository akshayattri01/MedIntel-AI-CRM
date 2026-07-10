import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import { api } from '../../services/api';
import type { User } from '../../types';

type AuthState = { user: User | null; token: string | null; status: 'idle' | 'loading' | 'failed' };
const initialState: AuthState = { user: null, token: localStorage.getItem('medintel_token'), status: 'idle' };

export const login = createAsyncThunk('auth/login', async (payload: { email: string; password: string }) => {
  const { data } = await api.post('/auth/login', payload);
  localStorage.setItem('medintel_token', data.access_token);
  localStorage.setItem('medintel_refresh_token', data.refresh_token);
  return data;
});

export const register = createAsyncThunk('auth/register', async (payload: { email: string; full_name: string; password: string }) => {
  const { data } = await api.post('/auth/register', payload);
  localStorage.setItem('medintel_token', data.access_token);
  localStorage.setItem('medintel_refresh_token', data.refresh_token);
  return data;
});

export const fetchMe = createAsyncThunk('auth/me', async () => (await api.get('/users/me')).data);

const slice = createSlice({
  name: 'auth',
  initialState,
  reducers: { logout: (state) => { state.user = null; state.token = null; localStorage.removeItem('medintel_token'); localStorage.removeItem('medintel_refresh_token'); } },
  extraReducers: (builder) => {
    builder.addCase(login.pending, (s) => { s.status = 'loading'; }).addCase(login.fulfilled, (s, a) => { s.status = 'idle'; s.user = a.payload.user; s.token = a.payload.access_token; }).addCase(login.rejected, (s) => { s.status = 'failed'; });
    builder.addCase(register.fulfilled, (s, a) => { s.user = a.payload.user; s.token = a.payload.access_token; });
    builder.addCase(fetchMe.fulfilled, (s, a) => { s.user = a.payload; });
  }
});
export const { logout } = slice.actions;
export default slice.reducer;
