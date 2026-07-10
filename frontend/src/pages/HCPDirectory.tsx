import { useEffect, useState } from 'react';
import { Search, UserPlus, X } from 'lucide-react';
import { toast } from 'sonner';
import { Card } from '../components/ui/Card';
import { useAppDispatch, useAppSelector } from '../redux/hooks';
import { fetchHcps } from '../redux/slices/crmSlice';
import { crmApi } from '../services/api';
import type { HCP, Interaction } from '../types';

const emptyForm = { name: '', specialty: '', institution: '', city: '', email: '', phone: '' };

export function HCPDirectory() {
  const [q, setQ] = useState('');
  const [editing, setEditing] = useState<HCP | null>(null);
  const [profile, setProfile] = useState<HCP | null>(null);
  const [history, setHistory] = useState<Interaction[]>([]);
  const [form, setForm] = useState(emptyForm);
  const dispatch = useAppDispatch();
  const hcps = useAppSelector((s) => s.crm.hcps);

  useEffect(() => { dispatch(fetchHcps(q)); }, [dispatch, q]);

  function openEditor(hcp?: HCP) {
    setEditing(hcp ?? { id: '', sentiment_score: 0.5, ...emptyForm });
    setForm(hcp ? { name: hcp.name, specialty: hcp.specialty, institution: hcp.institution ?? '', city: hcp.city ?? '', email: hcp.email ?? '', phone: hcp.phone ?? '' } : emptyForm);
  }

  async function saveHcp() {
    if (!form.name.trim() || !form.specialty.trim()) {
      toast.error('Name and specialty are required');
      return;
    }
    if (editing?.id) await crmApi.updateHcp(editing.id, form);
    else await crmApi.createHcp(form);
    toast.success(editing?.id ? 'HCP updated' : 'HCP added');
    setEditing(null);
    dispatch(fetchHcps(q));
  }

  async function deleteHcp(id: string) {
    await crmApi.deleteHcp(id);
    toast.success('HCP deleted');
    dispatch(fetchHcps(q));
  }

  async function openProfile(hcp: HCP) {
    setProfile(hcp);
    const { data } = await crmApi.hcpHistory(hcp.id);
    setHistory(data);
  }

  return (
    <div className="space-y-5">
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div><h2 className="text-2xl font-semibold">HCP Directory</h2><p className="text-sm text-slate-500">Manage doctor profiles, specialties, and meeting history.</p></div>
        <button className="btn-primary inline-flex items-center gap-2" onClick={() => openEditor()}><UserPlus size={17}/> Add HCP</button>
      </div>
      <div className="relative"><Search className="absolute left-3 top-3 text-slate-400" size={18}/><input className="input bg-white pl-10 dark:bg-slate-900" placeholder="Search doctors, specialties, hospitals" value={q} onChange={(e) => setQ(e.target.value)} /></div>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {hcps.map((hcp) => (
          <Card key={hcp.id}>
            <div className="flex items-start justify-between"><div><h3 className="font-semibold">{hcp.name}</h3><p className="text-sm text-slate-500">{hcp.specialty}</p></div><span className="rounded-full bg-blue-50 px-2 py-1 text-xs text-blue-700 dark:bg-blue-950 dark:text-blue-200">{Math.round(hcp.sentiment_score * 100)}%</span></div>
            <p className="mt-4 text-sm text-slate-500">{hcp.institution || 'Independent practice'} {hcp.city ? `- ${hcp.city}` : ''}</p>
            <div className="mt-4 flex gap-2"><button className="btn-secondary" onClick={() => openProfile(hcp)}>Profile</button><button className="btn-secondary" onClick={() => openEditor(hcp)}>Edit</button><button className="btn-secondary" onClick={() => deleteHcp(hcp.id)}>Delete</button></div>
          </Card>
        ))}
        {!hcps.length && <Card className="md:col-span-2 xl:col-span-3"><p className="text-sm text-slate-500">No HCPs match the current search.</p></Card>}
      </div>

      {editing && <div className="fixed inset-0 z-30 grid place-items-center bg-slate-950/40 p-4"><Card className="w-full max-w-2xl"><div className="mb-4 flex items-center justify-between"><h3 className="font-semibold">{editing.id ? 'Edit HCP' : 'Add HCP'}</h3><button onClick={() => setEditing(null)}><X size={18}/></button></div><div className="grid gap-3 md:grid-cols-2">{Object.entries(form).map(([key, value]) => <input key={key} className="input" placeholder={key.replace('_', ' ')} value={value} onChange={(e) => setForm({ ...form, [key]: e.target.value })} />)}</div><div className="mt-5 flex justify-end gap-2"><button className="btn-secondary" onClick={() => setEditing(null)}>Cancel</button><button className="btn-primary" onClick={saveHcp}>Save</button></div></Card></div>}

      {profile && <div className="fixed inset-0 z-30 grid place-items-center bg-slate-950/40 p-4"><Card className="max-h-[85vh] w-full max-w-3xl overflow-y-auto"><div className="mb-4 flex items-center justify-between"><div><h3 className="text-xl font-semibold">{profile.name}</h3><p className="text-sm text-slate-500">{profile.specialty} - {profile.institution || 'Independent practice'}</p></div><button onClick={() => setProfile(null)}><X size={18}/></button></div><div className="grid gap-3 md:grid-cols-3"><div className="rounded-lg bg-slate-50 p-3 dark:bg-slate-800"><p className="text-xs text-slate-500">Sentiment</p><b>{Math.round(profile.sentiment_score * 100)}%</b></div><div className="rounded-lg bg-slate-50 p-3 dark:bg-slate-800"><p className="text-xs text-slate-500">City</p><b>{profile.city || 'Not set'}</b></div><div className="rounded-lg bg-slate-50 p-3 dark:bg-slate-800"><p className="text-xs text-slate-500">Last contact</p><b>{profile.last_contacted_at ? new Date(profile.last_contacted_at).toLocaleDateString() : 'None'}</b></div></div><h4 className="mt-6 font-semibold">Meeting history</h4><div className="mt-3 space-y-3">{history.map((item) => <div key={item.id} className="rounded-lg border p-3 dark:border-slate-800"><div className="flex justify-between text-sm"><b>{item.interaction_type}</b><span>{new Date(item.occurred_at).toLocaleDateString()}</span></div><p className="mt-1 text-sm text-slate-500">{item.summary}</p></div>)}{!history.length && <p className="text-sm text-slate-500">No meetings recorded for this HCP yet.</p>}</div></Card></div>}
    </div>
  );
}
