import { Link, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { AuthShell } from './AuthShell';
import { useAppDispatch } from '../redux/hooks';
import { register as registerUser } from '../redux/slices/authSlice';

export function Register() {
  const { register, handleSubmit } = useForm({ defaultValues: { full_name: '', email: '', password: '' } });
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  return <AuthShell title="Create workspace" subtitle="Start a secure MedIntel AI CRM account."><form className="space-y-4" onSubmit={handleSubmit(async (values) => { await dispatch(registerUser(values)).unwrap(); navigate('/'); })}><input className="input" placeholder="Full name" {...register('full_name')} /><input className="input" placeholder="Email" {...register('email')} /><input className="input" type="password" placeholder="Password" {...register('password')} /><button className="btn-primary w-full">Register</button><Link className="block text-sm text-slate-300" to="/login">Already have an account?</Link></form></AuthShell>;
}
