const viewMap: Record<string, string> = { "⌂ Overview": "overview", "▣ Documents": "documents", "◈ AI Processing": "processing", "◌ Audit logs": "audit", Overview: "overview", Documents: "documents", "AI Processing": "processing", "Audit logs": "audit" };
function setView(label: string) { const view = viewMap[label]; if (view) document.documentElement.dataset.dashboardView = view; }
export function installDashboardNavigation() {
  setView("Overview");
  document.addEventListener("click", event => {
    const target = event.target as HTMLElement | null;
    const item = target?.closest(".side-nav-item, .sidebar nav a") as HTMLElement | null;
    if (!item) return;
    const label = item.textContent?.replace("›", "").replace(/\s+/g, " ").trim() || "";
    if (viewMap[label]) { event.preventDefault(); setView(label); document.querySelectorAll(".sidebar nav a, .side-nav-item").forEach(el => el.classList.remove("active")); item.classList.add("active"); }
  });
}
