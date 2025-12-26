// =============================================================================
// Header Component
// Top navigation bar with project selector and user menu
// =============================================================================

import { useAuth } from "@/lib/auth";
import { useProject } from "@/hooks/useProjects";
import { Button } from "@/components/ui/button";

interface HeaderProps {
  projectId: string;
}

export function Header({ projectId }: HeaderProps) {
  const { user, logout } = useAuth();
  const { data: project } = useProject(projectId);

  return (
    <header className="h-14 border-b bg-background px-4 flex items-center justify-between">
      {/* Left: Project name */}
      <div className="flex items-center gap-4">
        <h1 className="text-xl font-bold text-primary">BRAID Manager</h1>
        {project && (
          <>
            <span className="text-muted-foreground">/</span>
            <span className="font-medium">{project.name}</span>
          </>
        )}
      </div>

      {/* Right: User info and logout */}
      <div className="flex items-center gap-4">
        <span className="text-sm text-muted-foreground">
          {user?.name}
        </span>
        <Button variant="outline" size="sm" onClick={logout}>
          Sign out
        </Button>
      </div>
    </header>
  );
}

export default Header;
