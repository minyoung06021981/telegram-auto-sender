import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { AppState, AppActions } from '@/types'

type AppStore = AppState & AppActions

export const useAppStore = create<AppStore>()(
  persist(
    (set) => ({
      // State
      theme: 'system',
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
        // Apply theme on rehydration
        if (state?.theme) {
          const root = window.document.documentElement
          root.classList.remove('light', 'dark')
          
          if (state.theme === 'system') {
            const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches
              ? 'dark'
              : 'light'
            root.classList.add(systemTheme)
          } else {
            root.classList.add(state.theme)
          }
        }
      },
    }
  )
)