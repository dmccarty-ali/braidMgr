// =============================================================================
// AppLayout Component
// Main layout wrapper with header, sidebar, and content area
// =============================================================================

import { useParams } from "react-router-dom";
import { Header } from "./Header";
import { Sidebar } from "./Sidebar";

interface AppLayoutProps {
  children: React.ReactNode;
}

export function AppLayout({ children }: AppLayoutProps) {
  const { projectId } = useParams<{ projectId: string }>();

  if (!projectId) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <p className="text-muted-foreground">No project selected</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Top header */}
      <Header projectId={projectId} />

      {/* Main content area with sidebar */}
      <div className="flex-1 flex">
        {/* Left sidebar */}
        <Sidebar />

        {/* Content area */}
        <main className="flex-1 p-6 overflow-auto">
          {children}
        </main>
      </div>
    </div>
  );
}

export default AppLayout;
