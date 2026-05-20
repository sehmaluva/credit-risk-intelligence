import { Link, Outlet, useLocation } from "react-router-dom";
import {
  LayoutDashboard,
  FilePlus,
  BarChart3,
  FileText,
  Users,
  Shield,
  Settings,
  LogOut,
} from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { cn } from "@/lib/utils";

const nav = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard },
  { to: "/applications/new", label: "New Application", icon: FilePlus },
  { to: "/analytics", label: "Analytics", icon: BarChart3 },
  { to: "/reports", label: "Reports", icon: FileText },
  { to: "/users", label: "Users", icon: Users, roles: ["admin"] },
  { to: "/audit", label: "Audit Logs", icon: Shield, roles: ["admin", "risk_manager"] },
  { to: "/settings", label: "Settings", icon: Settings },
];

export function AppShell() {
  const { user, logout } = useAuth();
  const location = useLocation();

  const filteredNav = nav.filter(
    (item) => !item.roles || (user && item.roles.includes(user.role))
  );

  return (
    <div className="flex min-h-screen">
      <aside className="w-64 flex-shrink-0 bg-slate-900 text-slate-100">
        <div className="border-b border-slate-700 p-6">
          <h1 className="text-lg font-bold text-emerald-400">CreditRisk AI</h1>
          <p className="text-xs text-slate-400">Intelligence Platform</p>
        </div>
        <nav className="space-y-1 p-4">
          {filteredNav.map(({ to, label, icon: Icon }) => (
            <Link
              key={to}
              to={to}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition",
                location.pathname === to || (to !== "/" && location.pathname.startsWith(to))
                  ? "bg-emerald-600/20 text-emerald-300"
                  : "text-slate-300 hover:bg-slate-800"
              )}
            >
              <Icon size={18} />
              {label}
            </Link>
          ))}
        </nav>
        <div className="absolute bottom-0 w-64 border-t border-slate-700 p-4">
          <p className="truncate text-xs text-slate-400">{user?.email}</p>
          <p className="text-xs capitalize text-slate-500">{user?.role?.replace("_", " ")}</p>
          <button
            onClick={() => logout()}
            className="mt-2 flex items-center gap-2 text-sm text-slate-400 hover:text-white"
          >
            <LogOut size={14} /> Logout
          </button>
        </div>
      </aside>
      <main className="flex-1 overflow-auto">
        <header className="border-b border-slate-200 bg-white px-8 py-4">
          <p className="text-sm text-slate-500">Branch: {user?.branch}</p>
        </header>
        <div className="p-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
