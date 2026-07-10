import { Send, Trash2 } from 'lucide-react';

export function ChatComposer({
  value,
  disabled,
  hasMessages,
  onChange,
  onClear,
  onSubmit,
}: {
  value: string;
  disabled: boolean;
  hasMessages: boolean;
  onChange: (value: string) => void;
  onClear: () => void;
  onSubmit: () => void;
}) {
  function handleKeyDown(event: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      onSubmit();
    }
  }

  return (
    <div className="border-t border-slate-200 bg-white/90 p-3 backdrop-blur dark:border-slate-800 dark:bg-slate-950/90 sm:p-4">
      <div className="mx-auto flex max-w-5xl items-end gap-2">
        <button type="button" onClick={onClear} disabled={!hasMessages || disabled} className="grid h-11 w-11 shrink-0 place-items-center rounded-lg border border-slate-200 text-slate-500 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40 dark:border-slate-800 dark:hover:bg-slate-900" aria-label="Clear chat">
          <Trash2 size={18} />
        </button>
        <div className="min-h-11 flex-1 rounded-lg border border-slate-200 bg-white px-3 py-2 shadow-sm focus-within:border-blue-500 focus-within:ring-4 focus-within:ring-blue-500/10 dark:border-slate-800 dark:bg-slate-950">
          <textarea
            value={value}
            onChange={(event) => onChange(event.target.value)}
            onKeyDown={handleKeyDown}
            rows={1}
            placeholder="Ask about HCPs, interactions, follow-ups, sentiment, or analytics..."
            className="max-h-40 min-h-7 w-full resize-none bg-transparent text-sm leading-7 outline-none placeholder:text-slate-400"
            disabled={disabled}
          />
        </div>
        <button type="button" onClick={onSubmit} disabled={disabled || !value.trim()} className="grid h-11 w-11 shrink-0 place-items-center rounded-lg bg-blue-600 text-white shadow-sm transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-40" aria-label="Send message">
          <Send size={18} />
        </button>
      </div>
    </div>
  );
}
