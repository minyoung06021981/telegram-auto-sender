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
    <div style={{ backgroundColor: '#000000', minHeight: '100vh', color: '#ffffff' }} className="flex items-center justify-center p-4">
      <div style={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '0.5rem', padding: '1.5rem', maxWidth: '28rem', width: '100%' }}>
        <div className="text-center pb-8">
          <EmergentLogo />
          <h1 style={{ color: '#ffffff', fontSize: '2.25rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>Sign In</h1>
          <p style={{ color: '#9ca3af' }}>Already have an account? 
            <Link to="/register" style={{ color: '#60a5fa', textDecoration: 'none', marginLeft: '0.25rem' }} 
                  onMouseOver={(e) => e.target.style.textDecoration = 'underline'}
                  onMouseOut={(e) => e.target.style.textDecoration = 'none'}>
              Log In
            </Link>
          </p>
        </div>

        <div className="space-y-6">
          {/* Google OAuth Button */}
          <button
            onClick={handleEmergentLogin}
            disabled={isLoading}
            style={{ 
              width: '100%', 
              height: '3rem', 
              backgroundColor: 'transparent', 
              border: '1px solid #4b5563', 
              color: '#ffffff',
              borderRadius: '0.375rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '0.75rem',
              cursor: 'pointer',
              fontSize: '0.875rem'
            }}
            onMouseOver={(e) => e.target.style.backgroundColor = '#374151'}
            onMouseOut={(e) => e.target.style.backgroundColor = 'transparent'}
          >
            <div className="w-5 h-5 bg-gradient-to-r from-blue-500 via-green-500 to-yellow-500 rounded-full"></div>
            <span>Continue with Google</span>
          </button>

          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <span style={{ width: '100%', borderTop: '1px solid #4b5563' }}></span>
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span style={{ backgroundColor: '#1f2937', padding: '0 0.5rem', color: '#9ca3af' }}>or sign in with email</span>
            </div>
          </div>

          {/* Email Form */}
          <div className="space-y-4">
            <div className="space-y-2">
              <label htmlFor="email" style={{ color: '#d1d5db', fontSize: '0.875rem', fontWeight: '500' }}>
                <div className="flex items-center space-x-2">
                  <div className="w-5 h-5 flex items-center justify-center">
                    <div style={{ width: '0.75rem', height: '0.75rem', border: '1px solid #9ca3af', borderRadius: '0.125rem' }}></div>
                  </div>
                  <span>Enter your email</span>
                </div>
              </label>
              <input
                id="email"
                type="email"
                placeholder=""
                style={{ 
                  width: '100%', 
                  height: '3rem', 
                  borderRadius: '0.375rem', 
                  border: '1px solid #4b5563', 
                  backgroundColor: '#374151', 
                  padding: '0.5rem 0.75rem', 
                  fontSize: '0.875rem', 
                  color: '#ffffff',
                  outline: 'none'
                }}
              />
            </div>

            <div className="space-y-2">
              <label htmlFor="password" style={{ color: '#d1d5db', fontSize: '0.875rem', fontWeight: '500' }}>
                <div className="flex items-center space-x-2">
                  <div className="w-5 h-5 flex items-center justify-center">
                    <div style={{ width: '0.75rem', height: '0.75rem', border: '1px solid #9ca3af', borderRadius: '0.125rem' }}></div>
                  </div>
                  <span>Enter your password</span>
                </div>
              </label>
              <input
                id="password"
                type="password"
                placeholder=""
                style={{ 
                  width: '100%', 
                  height: '3rem', 
                  borderRadius: '0.375rem', 
                  border: '1px solid #4b5563', 
                  backgroundColor: '#374151', 
                  padding: '0.5rem 0.75rem', 
                  fontSize: '0.875rem', 
                  color: '#ffffff',
                  outline: 'none'
                }}
              />
            </div>

            <button 
              style={{ 
                width: '100%', 
                height: '3rem', 
                backgroundColor: '#ffffff', 
                color: '#000000', 
                fontWeight: '600',
                borderRadius: '0.375rem',
                border: 'none',
                cursor: 'pointer',
                fontSize: '0.875rem'
              }}
              onMouseOver={(e) => e.target.style.backgroundColor = '#f3f4f6'}
              onMouseOut={(e) => e.target.style.backgroundColor = '#ffffff'}
            >
              Sign In
            </button>
          </div>

          <div className="text-center">
            <p style={{ fontSize: '0.875rem', color: '#9ca3af' }}>
              By clicking Sign In, you agree to our{' '}
              <a href="#" style={{ color: '#60a5fa', textDecoration: 'none' }}
                 onMouseOver={(e) => e.target.style.textDecoration = 'underline'}
                 onMouseOut={(e) => e.target.style.textDecoration = 'none'}>
                Terms of Service
              </a>
              {' '}and{' '}
              <a href="#" style={{ color: '#60a5fa', textDecoration: 'none' }}
                 onMouseOver={(e) => e.target.style.textDecoration = 'underline'}
                 onMouseOut={(e) => e.target.style.textDecoration = 'none'}>
                Privacy Policy
              </a>.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}