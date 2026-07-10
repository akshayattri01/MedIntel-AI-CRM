import { useEffect, useState } from 'react';
import { Bar, BarChart, CartesianGrid, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { Card } from '../components/ui/Card';
import { api } from '../services/api';

export function Analytics() {
  const [data, setData] = useState<any>();
  useEffect(() => { api.get('/analytics').then((r) => setData(r.data)); }, []);
  if (!data) return <Card>Loading analytics...</Card>;
  return <div className="grid gap-6 xl:grid-cols-2"><Card><h2 className="mb-4 font-semibold">Meetings trend</h2><ResponsiveContainer width="100%" height={280}><BarChart data={data.meetings}><CartesianGrid strokeDasharray="3 3"/><XAxis dataKey="month"/><YAxis/><Tooltip/><Bar dataKey="meetings" fill="#2563eb" radius={[6,6,0,0]}/></BarChart></ResponsiveContainer></Card><Card><h2 className="mb-4 font-semibold">Sentiment mix</h2><ResponsiveContainer width="100%" height={280}><PieChart><Pie data={data.sentiment} dataKey="value" nameKey="name" fill="#4f46e5" label /></PieChart></ResponsiveContainer></Card><Card><h2 className="mb-4 font-semibold">Top products</h2><div className="space-y-3">{data.products.map((p: any) => <div key={p.name} className="flex items-center justify-between rounded-lg bg-slate-50 p-3 dark:bg-slate-800"><span>{p.name}</span><b>{p.mentions}</b></div>)}</div></Card><Card><h2 className="mb-4 font-semibold">Follow-up completion</h2><p className="text-5xl font-semibold text-blue-600">{data.follow_up_completion}%</p><p className="mt-3 text-sm text-slate-500">Completion across pending and closed tasks.</p></Card></div>;
}
