import ReactMarkdown from 'react-markdown';
import { Check, Copy } from 'lucide-react';
import { useState } from 'react';

function CodeBlock({ className, children }: { className?: string; children: React.ReactNode }) {
  const [copied, setCopied] = useState(false);
  const code = String(children).replace(/\n$/, '');
  const language = /language-(\w+)/.exec(className ?? '')?.[1];

  async function copyCode() {
    await navigator.clipboard.writeText(code);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1500);
  }

  return (
    <div className="my-3 overflow-hidden rounded-lg border border-slate-200 bg-slate-950 text-slate-50 dark:border-slate-700">
      <div className="flex items-center justify-between border-b border-slate-800 px-3 py-2 text-xs text-slate-400">
        <span>{language ?? 'code'}</span>
        <button type="button" onClick={copyCode} className="inline-flex items-center gap-1 rounded-md px-2 py-1 text-slate-300 transition hover:bg-slate-800 hover:text-white">
          {copied ? <Check size={14} /> : <Copy size={14} />}
          {copied ? 'Copied' : 'Copy'}
        </button>
      </div>
      <pre className="overflow-x-auto p-3 text-sm leading-6">
        <code>{code}</code>
      </pre>
    </div>
  );
}

export function MarkdownMessage({ content }: { content: string }) {
  return (
    <ReactMarkdown
      components={{
        code({ className, children, ...props }) {
          const inline = !className;
          if (inline) {
            return <code className="rounded bg-slate-100 px-1.5 py-0.5 text-[0.92em] text-slate-900 dark:bg-slate-800 dark:text-slate-100" {...props}>{children}</code>;
          }
          return <CodeBlock className={className}>{children}</CodeBlock>;
        },
        p({ children }) {
          return <p className="mb-3 last:mb-0">{children}</p>;
        },
        ul({ children }) {
          return <ul className="mb-3 list-disc space-y-1 pl-5">{children}</ul>;
        },
        ol({ children }) {
          return <ol className="mb-3 list-decimal space-y-1 pl-5">{children}</ol>;
        },
        a({ children, href }) {
          return <a href={href} target="_blank" rel="noreferrer" className="font-medium text-blue-600 underline underline-offset-2 dark:text-blue-300">{children}</a>;
        },
      }}
    >
      {content}
    </ReactMarkdown>
  );
}
