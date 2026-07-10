import { useEffect, useState } from 'react';
import { toast } from 'sonner';
import { Card } from '../components/ui/Card';
import { useTheme } from '../hooks/useTheme';
import { crmApi } from '../services/api';
import { useAppDispatch, useAppSelector } from '../redux/hooks';
import { fetchMe } from '../redux/slices/authSlice';

export function Settings() {
  const { dark, setDark } = useTheme();
  const user = useAppSelector((s) => s.auth.user);
  const [fullName, setFullName] = useState(user?.full_name ?? '');
  const [settings, setSettings] = useState<{ groq_model: string; api_configured: boolean } | null>(null);
  const [notifications, setNotifications] = useState(() => localStorage.getItem('medintel_notifications') !== 'off');
  const dispatch = useAppDispatch();

  useEffect(() => { crmApi.settings().then((r) => setSettings(r.data)); }, []);
  useEffect(() => { setFullName(user?.full_name ?? ''); }, [user]);

  async function saveProfile() {
    await crmApi.updateProfile({ full_name: fullName });
    await dispatch(fetchMe());
    toast.success('Profile updated');
  }

  function toggleNotifications(value: boolean) {
    setNotifications(value);
    localStorage.setItem('medintel_notifications', value ? 'on' : 'off');
  }

  return <div className="grid gap-6 xl:grid-cols-2"><Card><h2 className="font-semibold">Profile</h2><div className="mt-4 space-y-3"><input className="input" placeholder="Full name" value={fullName} onChange={(e) => setFullName(e.target.value)} /><input className="input" placeholder="Email" value={user?.email ?? ''} disabled /><button className="btn-primary" onClick={saveProfile}>Save profile</button></div></Card><Card><h2 className="font-semibold">API Keys</h2><div className="mt-4 rounded-lg bg-slate-50 p-4 text-sm dark:bg-slate-800"><p><b>Groq model:</b> {settings?.groq_model ?? 'Loading'}</p><p><b>Groq API:</b> {settings?.api_configured ? 'Configured' : 'Not configured in backend environment'}</p></div></Card><Card><h2 className="font-semibold">Theme</h2><label className="mt-4 flex items-center gap-3 text-sm"><input type="checkbox" checked={dark} onChange={(e) => setDark(e.target.checked)} /> Enable dark mode</label></Card><Card><h2 className="font-semibold">Notifications</h2><label className="mt-4 flex items-center gap-3 text-sm"><input type="checkbox" checked={notifications} onChange={(e) => toggleNotifications(e.target.checked)} /> Follow-up reminders</label></Card></div>;
}
