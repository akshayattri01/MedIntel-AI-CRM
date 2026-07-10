import { useEffect, useRef } from 'react';
import { Bot, ShieldCheck } from 'lucide-react';
import { ChatComposer } from '../components/ai/ChatComposer';
import { ChatMessage } from '../components/ai/ChatMessage';
import { WelcomePanel } from '../components/ai/WelcomePanel';
import { useAiAssistant } from '../hooks/useAiAssistant';

export function AIAssistant() {
  const { messages, input, setInput, isLoading, status, hasMessages, sendMessage, clearChat } = useAiAssistant();
  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
  }, [messages]);

  return (
    <section className="-m-6 flex h-[calc(100vh-5.25rem)] flex-col bg-slate-50 dark:bg-slate-950">
      <div className="border-b border-slate-200 bg-white/80 px-4 py-3 backdrop-blur dark:border-slate-800 dark:bg-slate-950/80 sm:px-6">
        <div className="mx-auto flex max-w-5xl flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="grid h-10 w-10 place-items-center rounded-lg bg-blue-600 text-white">
              <Bot size={20} />
            </div>
            <div>
              <h2 className="font-semibold text-slate-950 dark:text-white">AI Assistant</h2>
              <p className="text-sm text-slate-500 dark:text-slate-400">Session chat for CRM intelligence and next-best actions</p>
            </div>
          </div>
          <div className="inline-flex items-center gap-2 rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-sm font-medium text-emerald-700 dark:border-emerald-900/70 dark:bg-emerald-950/40 dark:text-emerald-200">
            <ShieldCheck size={15} />
            Llama 3.3 70B Connected
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-4 py-6 sm:px-6">
        {!hasMessages ? (
          <WelcomePanel onPrompt={sendMessage} />
        ) : (
          <div className="mx-auto max-w-5xl space-y-6">
            {messages.map((message) => <ChatMessage key={message.id} message={message} />)}
            {isLoading && (
              <div className="rounded-lg border border-blue-200 bg-blue-50 px-4 py-3 text-sm text-blue-700 dark:border-blue-900/60 dark:bg-blue-950/30 dark:text-blue-200">
                {status}
              </div>
            )}
            <div ref={bottomRef} />
          </div>
        )}
      </div>

      <ChatComposer value={input} disabled={isLoading} hasMessages={hasMessages} onChange={setInput} onClear={clearChat} onSubmit={() => sendMessage()} />
    </section>
  );
}
