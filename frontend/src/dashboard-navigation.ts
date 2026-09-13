const viewMap: Record<string, string> = {
  Overview: "overview",
  Documents: "documents",
  "AI Processing": "processing",
  "Audit logs": "audit",
};

function setView(label: string) {
  const view = viewMap[label];
  if (view) document.documentElement.dataset.dashboardView = view;
}

export function installDashboardNavigation() {
  setView("Overview");
  document.addEventListener("click", (event) => {
    const target = event.target as HTMLElement | null;
    const item = target?.closest(".side-nav-item, .sidebar nav a") as HTMLElement | null;
    if (!item) return;
    const label = item.textContent?.replace("›", "").trim() || "";
    if (viewMap[label]) {
      event.preventDefault();
      setView(label);
    }
  });
}
