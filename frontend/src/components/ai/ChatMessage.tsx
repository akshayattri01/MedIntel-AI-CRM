import { Bot, Check, Copy, UserRound } from 'lucide-react';
import { useState } from 'react';
import { cn } from '../../utils/cn';
import { MarkdownMessage } from './MarkdownMessage';

export type ChatMessageRole = 'user' | 'assistant';

export type ChatMessageItem = {
  id: string;
  role: ChatMessageRole;
  content: string;
  createdAt: string;
  status?: string;
  isStreaming?: boolean;
  isError?: boolean;
};

function formatTime(value: string) {
  return new Intl.DateTimeFormat(undefined, { hour: 'numeric', minute: '2-digit' }).format(new Date(value));
}

export function ChatMessage({ message }: { message: ChatMessageItem }) {
  const [copied, setCopied] = useState(false);
  const isUser = message.role === 'user';

  async function copyMessage() {
    await navigator.clipboard.writeText(message.content);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1500);
  }

  return (
    <article className={cn('flex gap-3', isUser && 'flex-row-reverse')}>
      <div className={cn('grid h-9 w-9 shrink-0 place-items-center rounded-lg border', isUser ? 'border-blue-500 bg-blue-600 text-white' : 'border-slate-200 bg-white text-blue-600 dark:border-slate-800 dark:bg-slate-900')}>
        {isUser ? <UserRound size={18} /> : <Bot size={18} />}
      </div>
      <div className={cn('group max-w-[min(780px,calc(100%-3rem))]', isUser && 'items-end')}>
        <div className={cn('rounded-lg border px-4 py-3 text-sm leading-6 shadow-sm', isUser ? 'border-blue-600 bg-blue-600 text-white' : message.isError ? 'border-red-200 bg-red-50 text-red-900 dark:border-red-900/60 dark:bg-red-950/40 dark:text-red-100' : 'border-slate-200 bg-white text-slate-800 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-100')}>
          {message.content ? (
            isUser ? <p className="whitespace-pre-wrap">{message.content}</p> : <MarkdownMessage content={message.content} />
          ) : (
            <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400">
              <span className="h-2 w-2 animate-bounce rounded-full bg-blue-500 [animation-delay:-0.2s]" />
              <span className="h-2 w-2 animate-bounce rounded-full bg-blue-500 [animation-delay:-0.1s]" />
              <span className="h-2 w-2 animate-bounce rounded-full bg-blue-500" />
              <span>{message.status ?? 'Thinking'}</span>
            </div>
          )}
        </div>
        <div className={cn('mt-1 flex items-center gap-2 text-xs text-slate-400', isUser && 'justify-end')}>
          <span>{formatTime(message.createdAt)}</span>
          {!isUser && message.content && (
            <button type="button" onClick={copyMessage} className="inline-flex items-center gap-1 rounded px-1.5 py-0.5 opacity-100 transition hover:bg-slate-100 hover:text-slate-600 dark:hover:bg-slate-800 dark:hover:text-slate-200 sm:opacity-0 sm:group-hover:opacity-100">
              {copied ? <Check size={13} /> : <Copy size={13} />}
              {copied ? 'Copied' : 'Copy'}
            </button>
          )}
          {message.status && !message.content && <span>{message.status}</span>}
        </div>
      </div>
    </article>
  );
}
