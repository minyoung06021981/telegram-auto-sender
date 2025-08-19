import { useQuery } from '@tanstack/react-query'
import { BarChart3, Users, MessageSquare, Settings, TrendingUp, Activity } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { useAuthStore } from '@/stores/auth-store'

// Mock data - would be replaced with real API calls
const mockStats = {
  groups: {
    total: 25,
    active: 23,
    temp_blacklisted: 1,
    perm_blacklisted: 1
  },
  messages: {
    sent_24h: 145,
    failed_24h: 3
  },
  scheduler: {
    active: true
  }
}

export default function DashboardPage() {
  const { user } = useAuthStore()

  // Mock query - would be replaced with real API call
  const { data: stats = mockStats, isLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: async () => {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000))
      return mockStats
    },
  })

  const statCards = [
    {
      title: 'Total Groups',
      value: stats.groups.total,
      description: `${stats.groups.active} active, ${stats.groups.temp_blacklisted + stats.groups.perm_blacklisted} blacklisted`,
      icon: Users,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100 dark:bg-blue-900/20',
    },
    {
      title: 'Messages Today',
      value: stats.messages.sent_24h,
      description: `${stats.messages.failed_24h} failed`,
      icon: MessageSquare,
      color: 'text-green-600',
      bgColor: 'bg-green-100 dark:bg-green-900/20',
    },
    {
      title: 'Success Rate',
      value: `${Math.round((stats.messages.sent_24h / (stats.messages.sent_24h + stats.messages.failed_24h)) * 100)}%`,
      description: 'Last 24 hours',
      icon: TrendingUp,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100 dark:bg-purple-900/20',
    },
    {
      title: 'Scheduler Status',
      value: stats.scheduler.active ? 'Active' : 'Inactive',
      description: stats.scheduler.active ? 'Running automatically' : 'Stopped',
      icon: Activity,
      color: stats.scheduler.active ? 'text-green-600' : 'text-red-600',
      bgColor: stats.scheduler.active ? 'bg-green-100 dark:bg-green-900/20' : 'bg-red-100 dark:bg-red-900/20',
    },
  ]

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold">Dashboard</h1>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <Card key={i} className="animate-pulse">
              <CardContent className="p-6">
                <div className="h-16 bg-muted rounded"></div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <p className="text-muted-foreground">
            Welcome back, {user?.full_name?.split(' ')[0]}! Here's what's happening with your automation.
          </p>
        </div>
        
        <div className="flex space-x-2">
          <Button variant="outline">
            <BarChart3 className="mr-2 h-4 w-4" />
            View Reports
          </Button>
          <Button>
            <Settings className="mr-2 h-4 w-4" />
            Quick Setup
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat, index) => (
          <Card key={index} className="relative overflow-hidden">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">
                    {stat.title}
                  </p>
                  <p className="text-2xl font-bold">
                    {stat.value}
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    {stat.description}
                  </p>
                </div>
                
                <div className={`p-3 rounded-full ${stat.bgColor}`}>
                  <stat.icon className={`h-6 w-6 ${stat.color}`} />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>
              Common tasks to manage your Telegram automation
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button variant="outline" className="w-full justify-start">
              <Users className="mr-2 h-4 w-4" />
              Add New Groups
            </Button>
            <Button variant="outline" className="w-full justify-start">
              <MessageSquare className="mr-2 h-4 w-4" />
              Create Message Template
            </Button>
            <Button variant="outline" className="w-full justify-start">
              <Activity className="mr-2 h-4 w-4" />
              {stats.scheduler.active ? 'Stop' : 'Start'} Scheduler
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>
              Latest automation activities
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center space-x-3 text-sm">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span>Message sent to 15 groups</span>
                <span className="text-muted-foreground ml-auto">2 min ago</span>
              </div>
              <div className="flex items-center space-x-3 text-sm">
                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                <span>New template created</span>
                <span className="text-muted-foreground ml-auto">1 hour ago</span>
              </div>
              <div className="flex items-center space-x-3 text-sm">
                <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                <span>Group temporarily blacklisted</span>
                <span className="text-muted-foreground ml-auto">3 hours ago</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Subscription Status */}
      {user && (
        <Card>
          <CardHeader>
            <CardTitle>Subscription Status</CardTitle>
            <CardDescription>
              Your current plan and usage
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium capitalize">{user.subscription_type} Plan</p>
                <p className="text-sm text-muted-foreground">
                  {user.subscription_active ? 'Active' : 'Inactive'}
                </p>
              </div>
              
              <Button variant="outline">
                Upgrade Plan
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}