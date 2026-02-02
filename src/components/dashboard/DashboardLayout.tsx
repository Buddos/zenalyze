import { ReactNode } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { 
  LayoutDashboard, 
  SmilePlus, 
  Dumbbell, 
  MessageCircle, 
  Calendar, 
  AlertTriangle,
  LogOut,
  Leaf
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuth } from "@/hooks/useAuth";
import { Button } from "@/components/ui/button";

interface DashboardLayoutProps {
  children: ReactNode;
}

const navItems = [
  { icon: LayoutDashboard, label: "Dashboard", path: "/dashboard" },
  { icon: SmilePlus, label: "Mood", path: "/dashboard/mood" },
  { icon: Dumbbell, label: "Exercises", path: "/dashboard/exercises" },
  { icon: MessageCircle, label: "AI Chat", path: "/dashboard/chat" },
  { icon: Calendar, label: "Therapy", path: "/dashboard/therapy" },
  { icon: AlertTriangle, label: "Crisis Help", path: "/dashboard/emergency" },
];

const DashboardLayout = ({ children }: DashboardLayoutProps) => {
  const location = useLocation();
  const navigate = useNavigate();
  const { signOut } = useAuth();

  const handleSignOut = async () => {
    await signOut();
    navigate("/");
  };

  return (
    <div className="min-h-screen bg-background flex">
      {/* Sidebar */}
      <aside className="fixed left-0 top-0 h-full w-64 bg-sidebar border-r border-sidebar-border p-4 flex flex-col">
        {/* Logo */}
        <Link to="/dashboard" className="flex items-center gap-2 mb-8 px-2">
          <div className="w-9 h-9 rounded-lg bg-sidebar-primary flex items-center justify-center">
            <Leaf className="w-5 h-5 text-sidebar-primary-foreground" />
          </div>
          <span className="font-serif text-xl font-semibold text-sidebar-foreground">Zenalyze</span>
        </Link>

        {/* Navigation */}
        <nav className="flex-1 space-y-1">
          {navItems.map((item) => {
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={cn(
                  "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200",
                  isActive
                    ? "bg-sidebar-accent text-sidebar-accent-foreground"
                    : "text-sidebar-foreground/70 hover:bg-sidebar-accent/50 hover:text-sidebar-foreground"
                )}
              >
                <item.icon className={cn("w-5 h-5", isActive && "text-sidebar-primary")} />
                {item.label}
              </Link>
            );
          })}
        </nav>

        {/* Sign out */}
        <Button
          variant="ghost"
          onClick={handleSignOut}
          className="justify-start gap-3 text-sidebar-foreground/70 hover:text-sidebar-foreground hover:bg-sidebar-accent/50"
        >
          <LogOut className="w-5 h-5" />
          Sign Out
        </Button>
      </aside>

      {/* Main content */}
      <main className="flex-1 ml-64">
        <div className="p-8">
          {children}
        </div>
      </main>
    </div>
  );
};

export default DashboardLayout;
