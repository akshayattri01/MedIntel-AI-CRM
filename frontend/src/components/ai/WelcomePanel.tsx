import { BarChart3, CalendarClock, FileText, Mail, Search, Sparkles } from 'lucide-react';

const prompts = [
  ['Summarize interactions', 'Summarize recent interactions with cardiologists this month.', FileText],
  ['Follow-up plan', 'Generate a prioritized follow-up plan for doctors with pending actions.', CalendarClock],
  ['Draft email', 'Draft a professional follow-up email after my last positive meeting.', Mail],
  ['Find by sentiment', 'Find doctors with negative sentiment and suggest recovery actions.', Search],
  ['Explain analytics', 'Explain the dashboard analytics and what I should do next.', BarChart3],
  ['AI insights', 'Give me AI insights from recent CRM activity.', Sparkles],
] as const;

export function WelcomePanel({ onPrompt }: { onPrompt: (prompt: string) => void }) {
  return (
    <div className="mx-auto flex min-h-[calc(100vh-17rem)] max-w-5xl flex-col justify-center">
      <div className="mb-8 max-w-3xl">
        <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-sm font-medium text-blue-700 dark:border-blue-900/60 dark:bg-blue-950/40 dark:text-blue-200">
          <Sparkles size={16} />
          Llama 3.3 70B Connected
        </div>
        <h2 className="text-3xl font-semibold tracking-normal text-slate-950 dark:text-white sm:text-4xl">How can I help with your healthcare CRM today?</h2>
        <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-500 dark:text-slate-400">Ask for interaction summaries, follow-up planning, email drafts, sentiment searches, meeting prep, or analytics explanations using your existing CRM data.</p>
      </div>
      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
        {prompts.map(([title, prompt, Icon]) => (
          <button key={title} type="button" onClick={() => onPrompt(prompt)} className="rounded-lg border border-slate-200 bg-white p-4 text-left shadow-sm transition hover:border-blue-300 hover:bg-blue-50/60 dark:border-slate-800 dark:bg-slate-900 dark:hover:border-blue-800 dark:hover:bg-blue-950/30">
            <Icon className="mb-3 text-blue-600 dark:text-blue-300" size={20} />
            <div className="font-medium text-slate-900 dark:text-slate-100">{title}</div>
            <p className="mt-1 text-sm leading-5 text-slate-500 dark:text-slate-400">{prompt}</p>
          </button>
        ))}
      </div>
    </div>
  );
}
