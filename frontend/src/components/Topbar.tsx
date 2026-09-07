type TopbarProps = {
  title: string;
  onLogout: () => void;
};

function Topbar({ title, onLogout }: TopbarProps) {
  return (
    <header className="sticky top-0 z-30 flex h-20 items-center justify-between border-b border-slate-800 bg-slate-950/95 px-8 backdrop-blur">
      
      <div>
        <p className="text-sm text-slate-500">
          Workspace
        </p>

        <h2 className="text-xl font-bold text-white">
          {title}
        </h2>
      </div>

      <div className="flex items-center gap-4">
        
        <button className="flex h-10 w-10 items-center justify-center rounded-xl border border-slate-800 bg-slate-900 text-slate-400 hover:text-white">
          🔔
        </button>

        <div className="flex items-center gap-3 border-l border-slate-800 pl-4">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-sky-500 font-bold text-slate-950">
            U
          </div>

          <div className="hidden sm:block">
            <p className="text-sm font-semibold text-white">
              User
            </p>

            <p className="text-xs text-slate-500">
              Administrator
            </p>
          </div>

          <button
            onClick={onLogout}
            className="ml-2 text-sm text-slate-500 hover:text-red-400"
          >
            Logout
          </button>
        </div>
      </div>
    </header>
  );
}

export default Topbar;