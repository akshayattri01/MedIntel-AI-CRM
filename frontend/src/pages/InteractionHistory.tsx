import { useEffect, useState } from 'react';
import { toast } from 'sonner';
import { Card } from '../components/ui/Card';
import { useAppDispatch, useAppSelector } from '../redux/hooks';
import { fetchInteractions } from '../redux/slices/crmSlice';
import { crmApi } from '../services/api';
import type { Interaction } from '../types';

export function InteractionHistory() {
  const [q, setQ] = useState('');
  const [sentiment, setSentiment] = useState('');
  const [selected, setSelected] = useState<Interaction | null>(null);
  const [edit, setEdit] = useState<Interaction | null>(null);
  const dispatch = useAppDispatch();
  const interactions = useAppSelector((s) => s.crm.interactions);
  useEffect(() => { dispatch(fetchInteractions({ q, sentiment: sentiment || undefined })); }, [dispatch, q, sentiment]);

  async function saveEdit() {
    if (!edit) return;
    await crmApi.updateInteraction(edit.id, edit);
    toast.success('Interaction updated');
    setEdit(null);
    dispatch(fetchInteractions({ q, sentiment: sentiment || undefined }));
  }

  async function remove(id: string) {
    await crmApi.deleteInteraction(id);
    toast.success('Interaction deleted');
    dispatch(fetchInteractions({ q, sentiment: sentiment || undefined }));
  }

  return <div className="space-y-4"><div><h2 className="text-2xl font-semibold">Interaction History</h2><p className="text-sm text-slate-500">Search, filter, edit, delete, and inspect HCP interactions.</p></div><Card><div className="grid gap-3 md:grid-cols-3"><input className="input" placeholder="Search keyword" value={q} onChange={(e) => setQ(e.target.value)} /><select className="input" value={sentiment} onChange={(e) => setSentiment(e.target.value)}><option value="">All sentiment</option><option value="positive">Positive</option><option value="neutral">Neutral</option><option value="negative">Negative</option></select><button className="btn-secondary" onClick={() => { setQ(''); setSentiment(''); }}>Clear filters</button></div></Card><div className="space-y-3">{interactions.map((item) => <Card key={item.id}><div className="flex flex-col justify-between gap-3 md:flex-row md:items-center"><div><h3 className="font-semibold">{item.hcp?.name ?? 'HCP'} <span className="text-sm font-normal text-slate-500">{new Date(item.occurred_at).toLocaleString()}</span></h3><p className="text-sm text-slate-500">{item.summary}</p></div><div className="flex gap-2"><button className="btn-secondary" onClick={() => setSelected(item)}>View</button><button className="btn-secondary" onClick={() => setEdit(item)}>Edit</button><button className="btn-secondary" onClick={() => remove(item.id)}>Delete</button></div></div></Card>)}{!interactions.length && <Card><p className="text-sm text-slate-500">No interactions match the current filters.</p></Card>}</div>{selected && <Detail interaction={selected} onClose={() => setSelected(null)} />}{edit && <div className="fixed inset-0 z-30 grid place-items-center bg-slate-950/40 p-4"><Card className="w-full max-w-2xl"><h3 className="font-semibold">Edit interaction</h3><div className="mt-4 grid gap-3"><textarea className="input min-h-24" value={edit.summary} onChange={(e) => setEdit({ ...edit, summary: e.target.value })} /><textarea className="input min-h-20" value={edit.outcome} onChange={(e) => setEdit({ ...edit, outcome: e.target.value })} /><select className="input" value={edit.observed_sentiment} onChange={(e) => setEdit({ ...edit, observed_sentiment: e.target.value })}><option value="positive">Positive</option><option value="neutral">Neutral</option><option value="negative">Negative</option></select></div><div className="mt-5 flex justify-end gap-2"><button className="btn-secondary" onClick={() => setEdit(null)}>Cancel</button><button className="btn-primary" onClick={saveEdit}>Save</button></div></Card></div>}</div>;
}

function Detail({ interaction, onClose }: { interaction: Interaction; onClose: () => void }) {
  return <div className="fixed inset-0 z-30 grid place-items-center bg-slate-950/40 p-4"><Card className="w-full max-w-2xl"><h3 className="text-xl font-semibold">{interaction.hcp?.name ?? 'HCP'} details</h3><div className="mt-4 space-y-3 text-sm"><p><b>Summary:</b> {interaction.summary}</p><p><b>Outcome:</b> {interaction.outcome}</p><p><b>Topics:</b> {interaction.topics_discussed.join(', ') || 'None'}</p><p><b>Materials:</b> {interaction.materials_shared.join(', ') || 'None'}</p><p><b>Follow-up:</b> {interaction.follow_up_action || 'None'}</p></div><div className="mt-5 flex justify-end"><button className="btn-primary" onClick={onClose}>Close</button></div></Card></div>;
}
