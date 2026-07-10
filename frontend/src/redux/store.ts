import { configureStore } from '@reduxjs/toolkit';
import authReducer from './slices/authSlice';
import crmReducer from './slices/crmSlice';

export const store = configureStore({ reducer: { auth: authReducer, crm: crmReducer } });
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
