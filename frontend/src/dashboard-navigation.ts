const viewMap: Record<string, string> = { "⌂ Overview": "overview", "▣ Documents": "documents", "◈ AI Processing": "processing", "◌ Audit logs": "audit", Overview: "overview", Documents: "documents", "AI Processing": "processing", "Audit logs": "audit" };
function setView(label: string) { const view = viewMap[label]; if (view) document.documentElement.dataset.dashboardView = view; }
function applyIdentity() {
  const heading = document.querySelector(".calm-app .topbar h1") as HTMLElement | null;
  if (heading) heading.textContent = "See you again with DocuMind AI";
  const token = localStorage.getItem("documind_token");
  const nameEl = document.querySelector(".calm-app .user-chip strong") as HTMLElement | null;
  const roleEl = document.querySelector(".calm-app .user-chip small") as HTMLElement | null;
  const initialEl = document.querySelector(".calm-app .user-chip > span") as HTMLElement | null;
  if (token && nameEl && nameEl.textContent?.trim() === "Workspace user") {
    fetch("http://127.0.0.1:8000/api/v1/users/me", { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.ok ? r.json() : null).then(profile => {
        if (!profile?.full_name) return;
        nameEl.textContent = profile.full_name; if (roleEl) roleEl.textContent = "Workspace"; if (initialEl) initialEl.textContent = profile.full_name.charAt(0).toUpperCase();
      }).catch(() => undefined);
  }
}
export function installDashboardNavigation() {
  setView("Overview");
  const observer = new MutationObserver(() => applyIdentity());
  observer.observe(document.body, { childList: true, subtree: true });
  window.setTimeout(applyIdentity, 100);
  document.addEventListener("click", event => {
    const target = event.target as HTMLElement | null;
    const item = target?.closest(".side-nav-item, .sidebar nav a") as HTMLElement | null;
    if (!item) return;
    const label = item.textContent?.replace("›", "").replace(/\s+/g, " ").trim() || "";
    if (viewMap[label]) { event.preventDefault(); setView(label); document.querySelectorAll(".sidebar nav a, .side-nav-item").forEach(el => el.classList.remove("active")); item.classList.add("active"); }
  });
}
