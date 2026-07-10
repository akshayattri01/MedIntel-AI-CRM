import { useState } from 'react';
import { Link } from 'react-router-dom';
import { toast } from 'sonner';
import { api } from '../services/api';
import { AuthShell } from './AuthShell';

export function ForgotPassword() {
  const [email, setEmail] = useState('');
  async function submit() {
    await api.post('/auth/forgot-password', { email });
    toast.success('Password reset workflow requested');
  }
  return <AuthShell title="Reset password" subtitle="Enter your email and the reset workflow will be triggered."><div className="space-y-4"><input className="input" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} /><button className="btn-primary w-full" onClick={submit}>Send reset link</button><Link className="text-sm text-slate-300" to="/login">Back to login</Link></div></AuthShell>;
}
