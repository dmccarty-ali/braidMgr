// =============================================================================
// Sidebar Component
// Navigation sidebar with view links
// =============================================================================

import { NavLink, useParams } from "react-router-dom";
import { cn } from "@/lib/utils";

// Navigation item configuration
const navItems = [
  { path: "dashboard", label: "Dashboard", icon: "📊" },
  { path: "items", label: "All Items", icon: "📋" },
  { path: "active", label: "Active Items", icon: "🔥" },
  { path: "timeline", label: "Timeline", icon: "📅" },
  { path: "chronology", label: "Chronology", icon: "📆" },
  { path: "help", label: "Help", icon: "❓" },
];

export function Sidebar() {
  const { projectId } = useParams<{ projectId: string }>();

  return (
    <aside className="w-56 border-r bg-muted/30 flex flex-col">
      {/* Navigation links */}
      <nav className="flex-1 p-4 space-y-1" data-tour="sidebar-nav">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={`/projects/${projectId}/${item.path}`}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors",
                isActive
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:bg-muted hover:text-foreground"
              )
            }
          >
            <span className="text-base">{item.icon}</span>
            {item.label}
          </NavLink>
        ))}
      </nav>

      {/* Back to projects link */}
      <div className="p-4 border-t">
        <NavLink
          to="/projects"
          className="flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
        >
          <span className="text-base">←</span>
          All Projects
        </NavLink>
      </div>
    </aside>
  );
}

export default Sidebar;
