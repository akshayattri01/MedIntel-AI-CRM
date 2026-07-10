import { Link, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { toast } from 'sonner';
import { AuthShell } from './AuthShell';
import { useAppDispatch } from '../redux/hooks';
import { login } from '../redux/slices/authSlice';

export function Login() {
  const { register, handleSubmit } = useForm({ defaultValues: { email: 'rep@medintel.ai', password: 'Password123!' } });
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  return <AuthShell title="Welcome back" subtitle="Sign in to manage HCP relationships and AI-assisted interactions."><form className="space-y-4" onSubmit={handleSubmit(async (values) => { try { await dispatch(login(values)).unwrap(); navigate('/'); } catch { toast.error('Invalid credentials'); } })}><input className="input" placeholder="Email" {...register('email')} /><input className="input" type="password" placeholder="Password" {...register('password')} /><button className="btn-primary w-full">Sign in</button><div className="flex justify-between text-sm text-slate-300"><Link to="/forgot-password">Forgot password?</Link><Link to="/register">Create account</Link></div></form></AuthShell>;
}
