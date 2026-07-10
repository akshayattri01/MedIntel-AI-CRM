import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { Activity, BarChart3, CalendarPlus, ContactRound, LayoutDashboard, LogOut, Settings, Sparkles } from 'lucide-react';
import { logout } from '../../redux/slices/authSlice';
import { useAppDispatch } from '../../redux/hooks';

function RobotIcon({ size = 18 }: { size?: number }) {
  return <span aria-hidden="true" style={{ fontSize: size, lineHeight: 1 }}>🤖</span>;
}

const nav = [
  ['/', LayoutDashboard, 'Dashboard'],
  ['/hcps', ContactRound, 'HCP Directory'],
  ['/log-interaction', CalendarPlus, 'Log Interaction'],
  ['/history', Activity, 'History'],
  ['/analytics', BarChart3, 'Analytics'],
  ['/ai', RobotIcon, 'AI Assistant'],
  ['/settings', Settings, 'Settings']
] as const;

export function AppLayout() {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  return (
    <div className="min-h-screen bg-slate-50 text-slate-950 dark:bg-slate-950 dark:text-slate-100">
      <aside className="fixed inset-y-0 left-0 hidden w-72 border-r border-slate-200 bg-white/90 p-5 backdrop-blur-xl dark:border-slate-800 dark:bg-slate-950/90 lg:block">
        <div className="mb-8 flex items-center gap-3">
          <div className="grid h-10 w-10 place-items-center rounded-xl bg-blue-600 text-white"><Sparkles size={20} /></div>
          <div><div className="font-semibold">MedIntel AI CRM</div><div className="text-xs text-slate-500">Healthcare intelligence</div></div>
        </div>
        <nav className="space-y-1">
          {nav.map(([to, Icon, label]) => (
            <NavLink key={to} to={to} className={({ isActive }) => `flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm transition ${isActive ? 'bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-200' : 'text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-900'}`}>
              <Icon size={18} /> {label}
            </NavLink>
          ))}
        </nav>
        <button className="absolute bottom-5 flex items-center gap-2 rounded-lg px-3 py-2 text-sm text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-900" onClick={() => { dispatch(logout()); navigate('/login'); }}><LogOut size={17} /> Sign out</button>
      </aside>
              <main className="pb-20 lg:pb-0 lg:pl-72">
                <header className="sticky top-0 z-10 border-b border-slate-200 bg-white/80 px-6 py-4 backdrop-blur dark:border-slate-800 dark:bg-slate-950/80">
                  <div className="flex items-center justify-between"><div><p className="text-sm text-slate-500">Enterprise healthcare CRM</p><h1 className="text-xl font-semibold">Command center</h1></div><div className="rounded-full border px-3 py-1 text-sm text-slate-500 dark:border-slate-800">Llama 3.3 70B ready</div></div>
                </header>
                <div className="p-6"><Outlet /></div>
              </main>
              <nav className="fixed inset-x-0 bottom-0 z-20 grid grid-cols-7 border-t border-slate-200 bg-white lg:hidden dark:border-slate-800 dark:bg-slate-950">
                {nav.map(([to, Icon, label]) => (
                  <NavLink key={to} to={to} className={({ isActive }) => `grid place-items-center gap-1 px-1 py-2 text-[10px] ${isActive ? 'text-blue-600' : 'text-slate-500'}`}>
                    <Icon size={18} /><span className="truncate">{label.split(' ')[0]}</span>
                  </NavLink>
                ))}
              </nav>
            </div>
          );
        }
