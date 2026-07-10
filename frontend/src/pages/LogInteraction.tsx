import { useEffect, useRef, useState } from 'react';
import { useForm } from 'react-hook-form';
import ReactMarkdown from 'react-markdown';
import { Bot, RefreshCw, Save, Send, Trash2 } from 'lucide-react';
import { toast } from 'sonner';
import { Card } from '../components/ui/Card';
import { api, crmApi } from '../services/api';
import { useAppDispatch, useAppSelector } from '../redux/hooks';
import { fetchHcps, fetchInteractions } from '../redux/slices/crmSlice';
import type { Interaction } from '../types';

type Message = { role: 'user' | 'assistant'; content: string };
type FormValues = { hcp_name: string; interaction_type: string; occurred_at: string; attendees: string; topics_discussed: string; materials_shared: string; samples_distributed: string; observed_sentiment: string; outcome: string; follow_up_action: string; summary: string };

const defaults = (): FormValues => ({ hcp_name: '', interaction_type: 'in-person', occurred_at: new Date().toISOString().slice(0, 16), attendees: '', topics_discussed: '', materials_shared: '', samples_distributed: '', observed_sentiment: 'neutral', outcome: '', follow_up_action: '', summary: '' });
const split = (value: string) => value.split(',').map((item) => item.trim()).filter(Boolean);
const join = (value?: string[]) => value?.join(', ') ?? '';

export function LogInteraction() {
  const { register, handleSubmit, reset, setValue, watch } = useForm<FormValues>({ defaultValues: defaults() });
  const [messages, setMessages] = useState<Message[]>([{ role: 'assistant', content: 'Tell me about your HCP meeting and I will extract fields, log it, and plan the follow-up.' }]);
  const [draft, setDraft] = useState('');
  const [streaming, setStreaming] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const endRef = useRef<HTMLDivElement>(null);
  const dispatch = useAppDispatch();
  const hcps = useAppSelector((s) => s.crm.hcps);
  const interactions = useAppSelector((s) => s.crm.interactions);

  useEffect(() => { dispatch(fetchHcps()); dispatch(fetchInteractions()); }, [dispatch]);
  useEffect(() => { endRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages, streaming]);

  async function send() {
    if (!draft.trim()) return;
    const content = draft;
    setDraft('');
    setMessages((m) => [...m, { role: 'user', content }]);
    setStreaming(true);
    try {
      const response = await fetch(`${api.defaults.baseURL}/ai/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('medintel_token')}` },
        body: JSON.stringify({ message: content }),
      });
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      while (reader) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        for (const chunk of buffer.split('\n\n')) {
          if (!chunk.startsWith('data: ')) continue;
          const raw = chunk.replace('data: ', '').trim();
          if (raw === '[DONE]') continue;
          const event = JSON.parse(raw);
          if (event.type === 'status') setMessages((m) => [...m, { role: 'assistant', content: event.message }]);
          if (event.type === 'result') {
            const payload = event.payload;
            setMessages((m) => [...m, { role: 'assistant', content: payload.response }]);
            const form = payload.data?.form;
            if (form) applyAiForm(form);
            if (payload.data?.interaction_id) {
              setEditingId(payload.data.interaction_id);
              dispatch(fetchInteractions());
              toast.success('AI saved the interaction');
            }
          }
        }
        buffer = buffer.endsWith('\n\n') ? '' : buffer.slice(buffer.lastIndexOf('\n\n') + 2);
      }
    } catch {
      setMessages((m) => [...m, { role: 'assistant', content: 'The AI stream failed. Please check the API server and token.' }]);
    } finally {
      setStreaming(false);
    }
  }

  function applyAiForm(form: any) {
    setValue('hcp_name', form.hcp_name ?? '');
    setValue('interaction_type', form.interaction_type ?? 'in-person');
    setValue('occurred_at', form.occurred_at ? new Date(form.occurred_at).toISOString().slice(0, 16) : defaults().occurred_at);
    setValue('attendees', join(form.attendees));
    setValue('topics_discussed', join(form.topics_discussed));
    setValue('materials_shared', join(form.materials_shared));
    setValue('samples_distributed', join(form.samples_distributed));
    setValue('observed_sentiment', form.observed_sentiment ?? 'neutral');
    setValue('outcome', form.outcome ?? '');
    setValue('follow_up_action', form.follow_up_action ?? '');
    setValue('summary', form.summary ?? '');
  }

  function editInteraction(item: Interaction) {
    setEditingId(item.id);
    reset({ hcp_name: item.hcp?.name ?? '', interaction_type: item.interaction_type, occurred_at: new Date(item.occurred_at).toISOString().slice(0, 16), attendees: join(item.attendees), topics_discussed: join(item.topics_discussed), materials_shared: join(item.materials_shared), samples_distributed: join(item.samples_distributed), observed_sentiment: item.observed_sentiment, outcome: item.outcome, follow_up_action: item.follow_up_action ?? '', summary: item.summary });
  }

  async function onSubmit(values: FormValues) {
    const payload = { hcp_name: values.hcp_name, interaction_type: values.interaction_type, occurred_at: new Date(values.occurred_at).toISOString(), attendees: split(values.attendees), topics_discussed: split(values.topics_discussed), materials_shared: split(values.materials_shared), samples_distributed: split(values.samples_distributed), observed_sentiment: values.observed_sentiment, outcome: values.outcome, follow_up_action: values.follow_up_action || undefined, summary: values.summary };
    if (!payload.hcp_name || !payload.outcome || !payload.summary) {
      toast.error('HCP, outcome, and summary are required');
      return;
    }
    if (editingId) await crmApi.updateInteraction(editingId, payload);
    else await crmApi.createInteraction(payload);
    toast.success(editingId ? 'Interaction updated' : 'Interaction saved');
    setEditingId(null);
    reset(defaults());
    dispatch(fetchInteractions());
    dispatch(fetchHcps());
  }

  async function removeCurrent() {
    if (!editingId) return;
    await crmApi.deleteInteraction(editingId);
    toast.success('Interaction deleted');
    setEditingId(null);
    reset(defaults());
    dispatch(fetchInteractions());
  }

  return <div className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]"><Card className="max-h-[calc(100vh-9rem)] overflow-y-auto"><div className="flex items-center justify-between"><h2 className="text-xl font-semibold">{editingId ? 'Edit HCP Interaction' : 'Log HCP Interaction'}</h2><button className="btn-secondary inline-flex items-center gap-2" onClick={() => { setEditingId(null); reset(defaults()); }}><RefreshCw size={16}/> New</button></div><form className="mt-5 grid gap-4" onSubmit={handleSubmit(onSubmit)}><input className="input" list="hcp-list" placeholder="HCP Name" {...register('hcp_name')} /><datalist id="hcp-list">{hcps.map((hcp) => <option key={hcp.id} value={hcp.name} />)}</datalist><div className="grid gap-4 md:grid-cols-2"><select className="input" {...register('interaction_type')}><option value="in-person">In-person</option><option value="virtual">Virtual</option><option value="phone">Phone</option><option value="email">Email</option></select><input className="input" type="datetime-local" {...register('occurred_at')} /></div><input className="input" placeholder="Attendees, comma separated" {...register('attendees')} /><textarea className="input min-h-24" placeholder="Topics Discussed" {...register('topics_discussed')} /><input className="input" placeholder="Materials Shared" {...register('materials_shared')} /><input className="input" placeholder="Samples Distributed" {...register('samples_distributed')} /><select className="input" {...register('observed_sentiment')}><option value="positive">Positive</option><option value="neutral">Neutral</option><option value="negative">Negative</option></select><textarea className="input min-h-24" placeholder="Outcome" {...register('outcome')} /><textarea className="input min-h-20" placeholder="Follow-up Action" {...register('follow_up_action')} /><textarea className="input min-h-24" placeholder="Summary" {...register('summary')} /><div className="flex flex-wrap gap-3"><button className="btn-primary inline-flex items-center gap-2"><Save size={17}/> {editingId ? 'Update' : 'Save'}</button>{editingId && <button type="button" className="btn-secondary inline-flex items-center gap-2" onClick={removeCurrent}><Trash2 size={16}/> Delete</button>}<button type="button" className="btn-secondary" onClick={() => reset(defaults())}>Cancel</button></div></form></Card><Card className="flex max-h-[calc(100vh-9rem)] flex-col p-0"><div className="border-b p-4 dark:border-slate-800"><h2 className="flex items-center gap-2 font-semibold"><Bot size={18}/> AI Assistant</h2></div><div className="flex-1 space-y-3 overflow-y-auto p-4">{messages.map((m, i) => <div key={`${m.role}-${i}`} className={`max-w-[88%] rounded-lg px-4 py-3 text-sm ${m.role === 'user' ? 'ml-auto bg-blue-600 text-white' : 'bg-slate-100 dark:bg-slate-800'}`}><ReactMarkdown>{m.content}</ReactMarkdown></div>)}{streaming && <div className="rounded-lg bg-slate-100 px-4 py-3 text-sm dark:bg-slate-800">Streaming...</div>}<div ref={endRef}/></div><div className="flex gap-2 border-t p-4 dark:border-slate-800"><textarea className="input min-h-12 flex-1" placeholder="Example: I met Dr Sharma today..." value={draft} onChange={(e) => setDraft(e.target.value)} onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); } }} /><button className="btn-primary px-4" onClick={send} disabled={streaming}><Send size={18}/></button></div><div className="border-t p-4 dark:border-slate-800"><h3 className="mb-3 text-sm font-semibold">Recent interactions</h3><div className="space-y-2">{interactions.slice(0, 5).map((item) => <button key={item.id} className="block w-full rounded-lg border p-3 text-left text-sm hover:bg-slate-50 dark:border-slate-800 dark:hover:bg-slate-800" onClick={() => editInteraction(item)}><b>{item.hcp?.name ?? 'HCP'}</b><p className="truncate text-slate-500">{item.summary}</p></button>)}</div></div></Card></div>;
}
