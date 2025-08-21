import { useEffect } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from '@/stores/auth-store'
import { useAppStore } from '@/stores/app-store'
import { authApi } from '@/api/auth'

// Pages
import LoginPage from '@/pages/LoginPage'
import RegisterPage from '@/pages/RegisterPage'
import ProfilePage from '@/pages/ProfilePage'
import DashboardLayout from '@/components/layout/DashboardLayout'
import DashboardPage from '@/pages/DashboardPage'
import TelegramPage from '@/pages/TelegramPage'
import GroupsPage from '@/pages/GroupsPage'
import TemplatesPage from '@/pages/TemplatesPage'
import SettingsPage from '@/pages/SettingsPage'

function App() {
  const { isAuthenticated, token } = useAuthStore()
  const { theme, setTheme } = useAppStore()

  useEffect(() => {
    // Initialize theme
    const savedTheme = localStorage.getItem('app-storage')
    if (savedTheme) {
      try {
        const parsed = JSON.parse(savedTheme)
        if (parsed.state?.theme) {
          setTheme(parsed.state.theme)
        }
      } catch (error) {
        console.error('Failed to parse saved theme:', error)
      }
    }

    // Set token in API client if available
    if (token) {
      authApi.setToken(token)
    }
  }, [token, setTheme])

  // Protected Route Component
  const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
    if (!isAuthenticated) {
      return <Navigate to="/login" replace />
    }
    return <>{children}</>
  }

  // Public Route Component (redirect if authenticated)
  const PublicRoute = ({ children }: { children: React.ReactNode }) => {
    if (isAuthenticated) {
      return <Navigate to="/dashboard" replace />
    }
    return <>{children}</>
  }

  return (
    <div className="min-h-screen bg-background">
      <Routes>
        {/* Public Routes */}
        <Route 
          path="/login" 
          element={
            <PublicRoute>
              <LoginPage />
            </PublicRoute>
          } 
        />
        <Route 
          path="/register" 
          element={
            <PublicRoute>
              <RegisterPage />
            </PublicRoute>
          } 
        />
        
        {/* Profile page for auth callback - not protected */}
        <Route path="/profile" element={<ProfilePage />} />

        {/* Protected Routes */}
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <DashboardLayout />
            </ProtectedRoute>
          }
        >
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<DashboardPage />} />
          <Route path="telegram" element={<TelegramPage />} />
          <Route path="groups" element={<GroupsPage />} />
          <Route path="templates" element={<TemplatesPage />} />
          <Route path="settings" element={<SettingsPage />} />
        </Route>

        {/* Catch all route */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </div>
  )
}

export default App