import type { ReactElement } from 'react';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { useEffect } from 'react';
import { useAppSelector } from './redux/hooks';
import { useAppDispatch } from './redux/hooks';
import { fetchMe } from './redux/slices/authSlice';
import { AppLayout } from './components/layout/AppLayout';
import { Login } from './pages/Login';
import { Register } from './pages/Register';
import { ForgotPassword } from './pages/ForgotPassword';
import { Dashboard } from './pages/Dashboard';
import { HCPDirectory } from './pages/HCPDirectory';
import { LogInteraction } from './pages/LogInteraction';
import { InteractionHistory } from './pages/InteractionHistory';
import { Analytics } from './pages/Analytics';
import { Settings } from './pages/Settings';
import { AIAssistant } from './pages/AIAssistant';

function Protected({ children }: { children: ReactElement }) {
  const token = useAppSelector((s) => s.auth.token);
  return token ? children : <Navigate to="/login" replace />;
}

export default function App() {
  const dispatch = useAppDispatch();
  const token = useAppSelector((s) => s.auth.token);
  useEffect(() => { if (token) dispatch(fetchMe()); }, [dispatch, token]);
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/" element={<Protected><AppLayout /></Protected>}>
          <Route index element={<Dashboard />} />
          <Route path="hcps" element={<HCPDirectory />} />
          <Route path="log-interaction" element={<LogInteraction />} />
          <Route path="history" element={<InteractionHistory />} />
          <Route path="analytics" element={<Analytics />} />
          <Route path="ai" element={<AIAssistant />} />
          <Route path="settings" element={<Settings />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
