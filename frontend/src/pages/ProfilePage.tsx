import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { toast } from 'sonner'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { useAuthStore } from '@/stores/auth-store'

export default function ProfilePage() {
  const navigate = useNavigate()
  const { emergentAuth, isLoading, isAuthenticated } = useAuthStore()

  useEffect(() => {
    const handleAuth = async () => {
      const hash = window.location.hash
      if (hash && hash.includes('session_id=')) {
        const sessionId = hash.split('session_id=')[1].split('&')[0]
        if (sessionId) {
          try {
            await emergentAuth(sessionId)
            toast.success('Successfully authenticated!')
            navigate('/dashboard')
          } catch (error: any) {
            toast.error(error.message || 'Authentication failed')
            navigate('/login')
          }
        }
      } else if (isAuthenticated) {
        // User is already authenticated, redirect to dashboard
        navigate('/dashboard')
      } else {
        // No session ID in URL and not authenticated, redirect to login
        navigate('/login')
      }
    }
    
    handleAuth()
  }, [emergentAuth, navigate, isAuthenticated])

  if (isLoading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <Card className="w-full max-w-md bg-gray-900 border-gray-700">
          <CardHeader>
            <CardTitle className="text-center text-white">
              Authenticating...
            </CardTitle>
          </CardHeader>
          <CardContent className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white mx-auto"></div>
            <p className="text-gray-400 mt-4">Please wait while we log you in.</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-black flex items-center justify-center">
      <Card className="w-full max-w-md bg-gray-900 border-gray-700">
        <CardHeader>
          <CardTitle className="text-center text-white">
            Processing Authentication
          </CardTitle>
        </CardHeader>
        <CardContent className="text-center">
          <p className="text-gray-400">Redirecting...</p>
        </CardContent>
      </Card>
    </div>
  )
}