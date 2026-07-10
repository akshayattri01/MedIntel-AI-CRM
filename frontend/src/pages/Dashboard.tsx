import { useEffect } from 'react';
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { Activity, Calendar, CheckCircle2, ContactRound, TrendingUp } from 'lucide-react';
import { toast } from 'sonner';
import { Card } from '../components/ui/Card';
import { Skeleton } from '../components/ui/Skeleton';
import { useAppDispatch, useAppSelector } from '../redux/hooks';
import { fetchDashboard } from '../redux/slices/crmSlice';
import { api } from '../services/api';

export function Dashboard() {
  const dispatch = useAppDispatch();
  const data = useAppSelector((s) => s.crm.dashboard);
  useEffect(() => { dispatch(fetchDashboard()); }, [dispatch]);

  async function completeFollowUp(id?: string) {
    if (!id) return;
    await api.patch(`/follow-ups/${id}/complete`);
    toast.success('Follow-up completed');
    dispatch(fetchDashboard());
  }

  if (!data) return <div className="grid gap-4 md:grid-cols-4"><Skeleton className="h-32" /><Skeleton className="h-32" /><Skeleton className="h-32" /><Skeleton className="h-32" /></div>;

  const cards = [
    [ContactRound, 'Total HCPs', data.total_hcps],
    [Calendar, "Today's meetings", data.todays_meetings],
    [Activity, 'Pending follow-ups', data.pending_followups],
    [TrendingUp, 'Positive sentiment', `${data.positive_sentiment_pct}%`],
  ] as const;

  return <div className="space-y-6"><div className="grid gap-4 md:grid-cols-4">{cards.map(([Icon, label, value]) => <Card key={label}><div className="flex items-center justify-between"><div><p className="text-sm text-slate-500">{label}</p><p className="mt-2 text-3xl font-semibold">{value}</p></div><Icon className="text-blue-600" /></div></Card>)}</div><div className="grid gap-6 xl:grid-cols-[1.6fr_1fr]"><Card><h2 className="mb-4 font-semibold">Monthly interactions</h2><ResponsiveContainer width="100%" height={280}><AreaChart data={data.monthly_interactions}><defs><linearGradient id="meetings" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#2563eb" stopOpacity={0.35}/><stop offset="95%" stopColor="#2563eb" stopOpacity={0}/></linearGradient></defs><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="month" /><YAxis /><Tooltip /><Area type="monotone" dataKey="meetings" stroke="#2563eb" fill="url(#meetings)" /></AreaChart></ResponsiveContainer></Card><Card><h2 className="mb-4 font-semibold">Recent activity</h2><div className="space-y-3">{data.recent_activity.map((item) => <div key={`${item.doctor}-${item.date}`} className="rounded-lg bg-slate-50 p-3 dark:bg-slate-800"><div className="flex justify-between text-sm"><b>{item.doctor}</b><span className="capitalize text-blue-600">{item.sentiment}</span></div><p className="mt-1 text-sm text-slate-500">{item.summary}</p></div>)}{!data.recent_activity.length && <p className="text-sm text-slate-500">No activity yet.</p>}</div></Card></div><Card><h2 className="mb-4 font-semibold">Upcoming follow-ups</h2><div className="grid gap-3 md:grid-cols-2">{data.upcoming_meetings.map((m) => <div className="rounded-lg border p-4 dark:border-slate-800" key={`${m.id}-${m.doctor}`}><div className="flex items-start justify-between gap-3"><div><b>{m.doctor}</b><p className="text-sm text-slate-500">{m.type}</p><p className="mt-1 text-xs text-slate-400">{m.time}</p></div><button className="btn-secondary inline-flex items-center gap-2" onClick={() => completeFollowUp(m.id)}><CheckCircle2 size={15}/> Complete</button></div></div>)}{!data.upcoming_meetings.length && <p className="text-sm text-slate-500">No pending follow-ups.</p>}</div></Card></div>;
}
