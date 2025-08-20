import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { AuthState, AuthActions, LoginRequest, RegisterRequest } from '@/types'
import { authApi } from '@/api/auth'

type AuthStore = AuthState & AuthActions

export const useAuthStore = create<AuthStore>()(
  persist(
    (set) => ({
      // State
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,

      // Actions
      login: async (credentials: LoginRequest) => {
        try {
          set({ isLoading: true })
          
          const response = await authApi.login(credentials)
          
          set({
            user: response.user,
            token: response.access_token,
            isAuthenticated: true,
            isLoading: false
          })
        } catch (error) {
          set({ isLoading: false })
          throw error
        }
      },

      register: async (data: RegisterRequest) => {
        try {
          set({ isLoading: true })
          
          const response = await authApi.register(data)
          
          set({
            user: response.user,
            token: response.access_token,
            isAuthenticated: true,
            isLoading: false
          })
        } catch (error) {
          set({ isLoading: false })
          throw error
        }
      },

      emergentAuth: async (sessionId: string) => {
        try {
          set({ isLoading: true })
          
          const response = await authApi.emergentAuth(sessionId)
          
          set({
            user: response.user,
            token: response.access_token,
            isAuthenticated: true,
            isLoading: false
          })
        } catch (error) {
          set({ isLoading: false })
          throw error
        }
      },

      logout: () => {
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          isLoading: false
        })
        // Clear token from API client
        authApi.clearToken()
      },

      updateUser: (user) => {
        set({ user })
      },

      setLoading: (loading) => {
        set({ isLoading: loading })
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
      onRehydrateStorage: () => (state) => {
        // Set token in API client when rehydrating
        if (state?.token) {
          authApi.setToken(state.token)
        }
      },
    }
  )
)