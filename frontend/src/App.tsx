// =============================================================================
// App Component
// Main application component with auth handling and routing
// =============================================================================

import { useState, useEffect } from "react";
import { Routes, Route, Navigate, Outlet, useNavigate, useLocation, useSearchParams } from "react-router-dom";
import { useAuth } from "./lib/auth";
import { LoginForm, RegisterForm, ForgotPasswordForm } from "./components/auth";
import { AppLayout } from "./components/layout";
import { ChatProvider, ChatDrawer, CommandPalette } from "./components/features/chat";
import { TourOverlay, useTourContext } from "./components/tour";
import { lazy, Suspense } from "react";

// Lazy load views for code splitting
const DashboardView = lazy(() => import("@/components/features/dashboard/DashboardView"));
const AllItemsView = lazy(() => import("@/components/features/items/AllItemsView"));
const ActiveItemsView = lazy(() => import("@/components/features/items/ActiveItemsView"));
const TimelineView = lazy(() => import("@/components/features/timeline/TimelineView"));
const ChronologyView = lazy(() => import("@/components/features/chronology/ChronologyView"));
const HelpView = lazy(() => import("@/components/features/help/HelpView"));

// =============================================================================
// Loading Fallback
// =============================================================================

function ViewLoading() {
  return (
    <div className="flex items-center justify-center h-64">
      <div className="text-muted-foreground">Loading...</div>
    </div>
  );
}

// =============================================================================
// Auth Views Container
// =============================================================================

type AuthView = "login" | "register" | "forgot-password";

function AuthContainer() {
  const location = useLocation();
  const navigate = useNavigate();

  // Determine initial view from URL path
  const getInitialView = (): AuthView => {
    if (location.pathname === "/register") return "register";
    if (location.pathname === "/forgot-password") return "forgot-password";
    return "login";
  };

  const [authView, setAuthView] = useState<AuthView>(getInitialView);

  const handleSuccess = () => {
    navigate("/projects");
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold tracking-tight">BRAID Manager</h1>
          <p className="text-muted-foreground mt-2">
            Multi-tenant Budget & RAID log management
          </p>
        </div>

        <div className="p-6 rounded-lg border bg-card">
          {authView === "login" && (
            <LoginForm
              onSuccess={handleSuccess}
              onRegisterClick={() => setAuthView("register")}
              onForgotPasswordClick={() => setAuthView("forgot-password")}
            />
          )}

          {authView === "register" && (
            <RegisterForm
              onSuccess={handleSuccess}
              onLoginClick={() => setAuthView("login")}
            />
          )}

          {authView === "forgot-password" && (
            <ForgotPasswordForm
              onSuccess={() => setAuthView("login")}
              onBackClick={() => setAuthView("login")}
            />
          )}
        </div>
      </div>
    </div>
  );
}

// =============================================================================
// Protected Route Wrapper
// =============================================================================

function ProtectedRoute() {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center space-y-4">
          <h1 className="text-4xl font-bold tracking-tight">BRAID Manager</h1>
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
}

// =============================================================================
// Public Only Route Wrapper
// =============================================================================

function PublicOnlyRoute() {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center space-y-4">
          <h1 className="text-4xl font-bold tracking-tight">BRAID Manager</h1>
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  if (isAuthenticated) {
    return <Navigate to="/projects" replace />;
  }

  return <Outlet />;
}

// =============================================================================
// Project Layout Wrapper
// Includes chat drawer and command palette for project views
// =============================================================================

function ProjectLayout() {
  return (
    <ChatProvider>
      <AppLayout>
        <Suspense fallback={<ViewLoading />}>
          <Outlet />
        </Suspense>
      </AppLayout>

      {/* Chat UI components - available on all project pages */}
      <ChatDrawer />
      <CommandPalette />
    </ChatProvider>
  );
}

// =============================================================================
// Project List Page
// =============================================================================

import { useProjects } from "@/hooks/useProjects";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";

function ProjectListPage() {
  const { user, logout } = useAuth();
  const { data, isLoading, error } = useProjects();
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <h1 className="text-xl font-bold">BRAID Manager</h1>
          <div className="flex items-center gap-4">
            <span className="text-sm text-muted-foreground">
              {user?.name}
            </span>
            <Button variant="outline" size="sm" onClick={logout}>
              Sign out
            </Button>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <h2 className="text-2xl font-bold mb-6">Select a Project</h2>

        {isLoading && (
          <p className="text-muted-foreground">Loading projects...</p>
        )}

        {error && (
          <p className="text-destructive">Failed to load projects</p>
        )}

        {data && data.projects.length === 0 && (
          <p className="text-muted-foreground">No projects found</p>
        )}

        {data && data.projects.length > 0 && (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4" data-tour="project-list">
            {data.projects.map((project) => (
              <Card
                key={project.id}
                className="cursor-pointer hover:border-primary transition-colors"
                onClick={() => navigate(`/projects/${project.id}/dashboard`)}
              >
                <CardHeader>
                  <CardTitle className="text-lg">{project.name}</CardTitle>
                </CardHeader>
                <CardContent>
                  {project.client_name && (
                    <p className="text-sm text-muted-foreground">
                      {project.client_name}
                    </p>
                  )}
                  {project.project_start && project.project_end && (
                    <p className="text-xs text-muted-foreground mt-1">
                      {project.project_start} - {project.project_end}
                    </p>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

// =============================================================================
// Demo Mode Detection
// Starts tour automatically when ?demo=true is in URL
// =============================================================================

function DemoModeDetector() {
  const [searchParams] = useSearchParams();
  const { startTour, isActive } = useTourContext();

  useEffect(() => {
    // Check for ?demo=true URL parameter
    if (searchParams.get("demo") === "true" && !isActive) {
      // Small delay to let the page render first
      const timer = setTimeout(() => {
        startTour();
      }, 500);
      return () => clearTimeout(timer);
    }
  }, [searchParams, startTour, isActive]);

  return null;
}

// =============================================================================
// Main App Component
// =============================================================================

function App() {
  return (
    <>
      {/* Demo mode URL param detection */}
      <DemoModeDetector />

      {/* Tour overlay - renders when tour is active */}
      <TourOverlay />

      <Routes>
      {/* Public routes */}
      <Route element={<PublicOnlyRoute />}>
        <Route path="/login" element={<AuthContainer />} />
        <Route path="/register" element={<AuthContainer />} />
        <Route path="/forgot-password" element={<AuthContainer />} />
      </Route>

      {/* Protected routes */}
      <Route element={<ProtectedRoute />}>
        <Route path="/" element={<Navigate to="/projects" replace />} />
        <Route path="/projects" element={<ProjectListPage />} />

        {/* Project views */}
        <Route path="/projects/:projectId" element={<ProjectLayout />}>
          <Route index element={<Navigate to="dashboard" replace />} />
          <Route path="dashboard" element={<DashboardView />} />
          <Route path="items" element={<AllItemsView />} />
          <Route path="active" element={<ActiveItemsView />} />
          <Route path="timeline" element={<TimelineView />} />
          <Route path="chronology" element={<ChronologyView />} />
          <Route path="help" element={<HelpView />} />
        </Route>
      </Route>

      {/* 404 fallback */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
    </>
  );
}

export default App;
