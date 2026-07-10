import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import { api } from '../../services/api';
import type { DashboardMetrics, FollowUp, HCP, Interaction } from '../../types';

type CRMState = { dashboard?: DashboardMetrics; hcps: HCP[]; interactions: Interaction[]; followUps: FollowUp[]; loading: boolean };
const initialState: CRMState = { hcps: [], interactions: [], followUps: [], loading: false };
export const fetchDashboard = createAsyncThunk('crm/dashboard', async () => (await api.get('/dashboard')).data);
export const fetchHcps = createAsyncThunk('crm/hcps', async (q?: string) => (await api.get('/hcp', { params: { q } })).data);
export const fetchInteractions = createAsyncThunk('crm/interactions', async (params?: { q?: string; sentiment?: string }) => (await api.get('/interactions', { params })).data);
export const fetchFollowUps = createAsyncThunk('crm/followups', async () => (await api.get('/follow-ups')).data);

const slice = createSlice({
  name: 'crm',
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder.addCase(fetchDashboard.fulfilled, (s, a) => { s.dashboard = a.payload; });
    builder.addCase(fetchHcps.fulfilled, (s, a) => { s.hcps = a.payload; });
    builder.addCase(fetchInteractions.fulfilled, (s, a) => { s.interactions = a.payload; });
    builder.addCase(fetchFollowUps.fulfilled, (s, a) => { s.followUps = a.payload; });
  }
});
export default slice.reducer;
