import { Navigate } from "react-router-dom";
import { useAuth } from "../lib/auth";

const HOME_FOR_ROLE: Record<string, string> = { citizen: "/citizen", worker: "/worker", admin: "/admin" };

export default function ProtectedRoute({
  children,
  allowedRoles,
}: {
  children: React.ReactNode;
  allowedRoles: string[];
}) {
  const { user, loading, isLoggingOut } = useAuth();

  if (loading) return null;
  // Mid-logout, we've already navigated to where we want to be (see TopBar).
  // Skip our own redirect so a stale render of this route doesn't win the
  // race and send the user to /login instead.
  if (isLoggingOut) return null;
  if (!user) return <Navigate to="/login" replace />;
  if (!allowedRoles.includes(user.role)) return <Navigate to={HOME_FOR_ROLE[user.role] || "/login"} replace />;

  return <>{children}</>;
}
