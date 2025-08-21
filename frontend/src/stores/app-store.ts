import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { AppState, AppActions } from '@/types'

type AppStore = AppState & AppActions

export const useAppStore = create<AppStore>()(
  persist(
    (set) => ({
      // State - default to dark theme
      theme: 'dark',
      sidebarCollapsed: false,

      // Actions
      setTheme: (theme) => {
        set({ theme })
        
        // Apply theme to document
        const root = window.document.documentElement
        root.classList.remove('light', 'dark')
        
        if (theme === 'system') {
          const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches
            ? 'dark'
            : 'light'
          root.classList.add(systemTheme)
        } else {
          root.classList.add(theme)
        }
      },

      toggleSidebar: () => {
        set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed }))
      },

      setSidebarCollapsed: (collapsed) => {
        set({ sidebarCollapsed: collapsed })
      },
    }),
    {
      name: 'app-storage',
      onRehydrateStorage: () => (state) => {
        // Always apply dark theme on rehydration
        const root = window.document.documentElement
        root.classList.remove('light', 'dark')
        root.classList.add('dark')
        
        // Set dark theme in state if not already set
        if (state && state.theme !== 'dark') {
          state.theme = 'dark'
        }
      },
    }
  )
)