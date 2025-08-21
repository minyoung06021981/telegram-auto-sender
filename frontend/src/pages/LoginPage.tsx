import { useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { toast } from 'sonner'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useAuthStore } from '@/stores/auth-store'

// Emergent logo component (simplified SVG)
const EmergentLogo = () => (
  <div className="flex items-center justify-center mb-8">
    <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
      <div className="w-8 h-8 border-2 border-white rounded-full opacity-80"></div>
    </div>
  </div>
)

export default function LoginPage() {
  const navigate = useNavigate()
  const { isAuthenticated, emergentAuth, isLoading } = useAuthStore()

  // Check if user is already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard')
    }
  }, [isAuthenticated, navigate])

  // Handle URL fragment authentication (from emergent auth callback)
  useEffect(() => {
    const handleAuth = async () => {
      const hash = window.location.hash
      if (hash && hash.includes('session_id=')) {
        const sessionId = hash.split('session_id=')[1].split('&')[0]
        if (sessionId) {
          try {
            await emergentAuth(sessionId)
            navigate('/profile')
          } catch (error: any) {
            toast.error(error.message || 'Authentication failed')
          }
        }
      }
    }
    
    handleAuth()
  }, [emergentAuth, navigate])

  const handleEmergentLogin = () => {
    const previewUrl = window.location.origin
    const redirectUrl = `${previewUrl}/profile`
    const authUrl = `https://auth.emergentagent.com/?redirect=${encodeURIComponent(redirectUrl)}`
    window.location.href = authUrl
  }

  return (
    <div className="min-h-screen bg-black flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-gray-900 border border-gray-700 rounded-lg shadow-sm">
        <div className="flex flex-col space-y-1.5 p-6 text-center pb-8">
          <EmergentLogo />
          <h1 className="text-4xl font-bold text-white mb-2">Sign In</h1>
          <p className="text-gray-400">Already have an account? 
            <Link to="/register" className="text-blue-400 hover:underline ml-1">Log In</Link>
          </p>
        </div>

        <div className="p-6 pt-0 space-y-6">
          {/* Google OAuth Button */}
          <button
            onClick={handleEmergentLogin}
            disabled={isLoading}
            className="w-full h-12 bg-transparent border border-gray-600 text-white hover:bg-gray-800 flex items-center justify-center space-x-3 rounded-md transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-gray-400 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
          >
            <div className="w-5 h-5 bg-gradient-to-r from-blue-500 via-green-500 to-yellow-500 rounded-full"></div>
            <span>Continue with Google</span>
          </button>

          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <span className="w-full border-t border-gray-600"></span>
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-gray-900 px-2 text-gray-400">or sign in with email</span>
            </div>
          </div>

          {/* Email Form */}
          <div className="space-y-4">
            <div className="space-y-2">
              <label htmlFor="email" className="text-gray-300 text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                <div className="flex items-center space-x-2">
                  <div className="w-5 h-5 flex items-center justify-center">
                    <div className="w-3 h-3 border border-gray-400 rounded"></div>
                  </div>
                  <span>Enter your email</span>
                </div>
              </label>
              <input
                id="email"
                type="email"
                placeholder=""
                className="flex h-12 w-full rounded-md border border-gray-600 bg-gray-800 px-3 py-2 text-sm text-white ring-offset-black file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-gray-400 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-gray-400 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              />
            </div>

            <div className="space-y-2">
              <label htmlFor="password" className="text-gray-300 text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                <div className="flex items-center space-x-2">
                  <div className="w-5 h-5 flex items-center justify-center">
                    <div className="w-3 h-3 border border-gray-400 rounded"></div>
                  </div>
                  <span>Enter your password</span>
                </div>
              </label>
              <input
                id="password"
                type="password"
                placeholder=""
                className="flex h-12 w-full rounded-md border border-gray-600 bg-gray-800 px-3 py-2 text-sm text-white ring-offset-black file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-gray-400 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-gray-400 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              />
            </div>

            <button className="w-full h-12 bg-white text-black hover:bg-gray-200 font-semibold rounded-md transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-gray-400 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50">
              Sign In
            </button>
          </div>

          <div className="text-center">
            <p className="text-sm text-gray-400">
              By clicking Sign In, you agree to our{' '}
              <a href="#" className="text-blue-400 hover:underline">Terms of Service</a>
              {' '}and{' '}
              <a href="#" className="text-blue-400 hover:underline">Privacy Policy</a>.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}