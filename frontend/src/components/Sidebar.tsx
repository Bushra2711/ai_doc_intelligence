type SidebarProps = {
  activePage: string;
  setActivePage: (page: string) => void;
};

function Sidebar({ activePage, setActivePage }: SidebarProps) {
  const menuItems = [
    { id: "dashboard", icon: "⌂", label: "Dashboard" },
    { id: "documents", icon: "▣", label: "Documents" },
    { id: "processing", icon: "⚙", label: "AI Processing" },
    { id: "invoices", icon: "▤", label: "Invoices" },
    { id: "compliance", icon: "✓", label: "Compliance" },
    { id: "analytics", icon: "▥", label: "Analytics" },
    { id: "audit", icon: "◉", label: "Audit Logs" },
  ];

  return (
    <aside className="fixed left-0 top-0 z-40 flex h-screen w-64 flex-col border-r border-slate-800 bg-slate-950">
      
      {/* Logo */}
      <div className="border-b border-slate-800 px-6 py-6">
        <p className="text-xs font-semibold uppercase tracking-[0.3em] text-sky-400">
          DocuMind AI
        </p>

        <h1 className="mt-2 text-xl font-bold text-white">
          Document Intelligence
        </h1>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-2 px-4 py-6">
        <p className="mb-4 px-3 text-xs font-semibold uppercase tracking-wider text-slate-500">
          Workspace
        </p>

        {menuItems.map((item) => (
          <button
            key={item.id}
            onClick={() => setActivePage(item.id)}
            className={`flex w-full items-center gap-3 rounded-xl px-4 py-3 text-left text-sm font-medium transition ${
              activePage === item.id
                ? "bg-sky-500/10 text-sky-400"
                : "text-slate-400 hover:bg-slate-900 hover:text-white"
            }`}
          >
            <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-slate-900 text-base">
              {item.icon}
            </span>

            {item.label}
          </button>
        ))}
      </nav>

      {/* Bottom */}
      <div className="border-t border-slate-800 p-4">
        <button
          onClick={() => setActivePage("settings")}
          className="flex w-full items-center gap-3 rounded-xl px-4 py-3 text-sm text-slate-400 hover:bg-slate-900 hover:text-white"
        >
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-slate-900">
            ⚙
          </span>

          Settings
        </button>
      </div>
    </aside>
  );
}

export default Sidebar;