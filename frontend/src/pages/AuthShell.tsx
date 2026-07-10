export function AuthShell({ title, subtitle, children }: { title: string; subtitle: string; children: React.ReactNode }) {
  return <div className="grid min-h-screen place-items-center bg-slate-950 px-4 text-white"><div className="w-full max-w-md rounded-lg border border-white/10 bg-white/10 p-8 shadow-2xl backdrop-blur"><div className="mb-6"><h1 className="text-2xl font-semibold">{title}</h1><p className="mt-2 text-sm text-slate-300">{subtitle}</p></div>{children}</div></div>;
}
