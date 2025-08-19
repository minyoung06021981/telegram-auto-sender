import { NavLink } from 'react-router-dom'
import { 
  LayoutDashboard, 
  MessageSquare, 
  Users, 
  FileText, 
  Settings, 
  Menu,
  Bot
} from 'lucide-react'
import { useAppStore } from '@/stores/app-store'
import { useAuthStore } from '@/stores/auth-store'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'

const navigationItems = [
  {
    name: 'Dashboard',
    href: '/dashboard',
    icon: LayoutDashboard,
  },
  {
    name: 'Telegram',
    href: '/telegram',
    icon: Bot,
  },
  {
    name: 'Groups',
    href: '/groups',
    icon: Users,
  },
  {
    name: 'Templates',
    href: '/templates',
    icon: FileText,
  },
  {
    name: 'Settings',
    href: '/settings',
    icon: Settings,
  },
]

export function Sidebar() {
  const { sidebarCollapsed, toggleSidebar } = useAppStore()
  const { user } = useAuthStore()

  return (
    <div className={cn(
      "fixed left-0 top-0 z-40 h-screen bg-card border-r border-border transition-all duration-300",
      sidebarCollapsed ? "w-16" : "w-64"
    )}>
      <div className="flex flex-col h-full">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-border">
          {!sidebarCollapsed && (
            <div className="flex items-center space-x-2">
              <MessageSquare className="h-8 w-8 text-primary" />
              <span className="font-bold text-lg">AutoSender</span>
            </div>
          )}
          
          <Button
            variant="ghost"
            size="icon"
            onClick={toggleSidebar}
            className={cn(sidebarCollapsed && "w-full")}
          >
            <Menu className="h-5 w-5" />
          </Button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-4 py-4 space-y-2">
          {navigationItems.map((item) => (
            <NavLink
              key={item.name}
              to={item.href}
              className={({ isActive }) =>
                cn(
                  "flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors",
                  "hover:bg-accent hover:text-accent-foreground",
                  isActive
                    ? "bg-accent text-accent-foreground"
                    : "text-muted-foreground",
                  sidebarCollapsed && "justify-center px-2"
                )
              }
            >
              <item.icon className={cn(
                "h-5 w-5 flex-shrink-0",
                !sidebarCollapsed && "mr-3"
              )} />
              
              {!sidebarCollapsed && (
                <span className="truncate">{item.name}</span>
              )}
            </NavLink>
          ))}
        </nav>

        {/* User info */}
        {!sidebarCollapsed && user && (
          <div className="p-4 border-t border-border">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center">
                <span className="text-primary-foreground text-sm font-medium">
                  {user.full_name.charAt(0).toUpperCase()}
                </span>
              </div>
              
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">
                  {user.full_name}
                </p>
                <p className="text-xs text-muted-foreground truncate">
                  {user.subscription_type}
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}