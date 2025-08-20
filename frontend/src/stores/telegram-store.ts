import { create } from 'zustand'
import { TelegramState, TelegramActions } from '@/types'

type TelegramStore = TelegramState & TelegramActions

export const useTelegramStore = create<TelegramStore>()((set) => ({
  // State
  sessions: [],
  activeSession: null,
  isLoading: false,

  // Actions
  setSessions: (sessions) => {
    set({ sessions })
  },

  addSession: (session) => {
    set((state) => ({
      sessions: [...state.sessions, session]
    }))
  },

  updateSession: (sessionId, updates) => {
    set((state) => ({
      sessions: state.sessions.map((session) =>
        session.session_id === sessionId
          ? { ...session, ...updates }
          : session
      ),
      activeSession:
        state.activeSession?.session_id === sessionId
          ? { ...state.activeSession, ...updates }
          : state.activeSession
    }))
  },

  removeSession: (sessionId) => {
    set((state) => ({
      sessions: state.sessions.filter((session) => session.session_id !== sessionId),
      activeSession:
        state.activeSession?.session_id === sessionId
          ? null
          : state.activeSession
    }))
  },

  setActiveSession: (session) => {
    set({ activeSession: session })
  },

  setLoading: (loading) => {
    set({ isLoading: loading })
  },
}))