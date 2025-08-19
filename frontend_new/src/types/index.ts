// Core types for the application

export interface User {
  id: string
  username: string
  email: string
  full_name: string
  subscription_type: 'free' | 'premium' | 'enterprise'
  subscription_active: boolean
  api_token?: string
  is_admin: boolean
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: User
}

export interface TelegramSession {
  session_id: string
  phone_number: string
  is_authenticated: boolean
  telegram_user?: {
    id: number
    first_name: string
    last_name?: string
    username?: string
  }
  requires_code?: boolean
  requires_password?: boolean
}

export interface Group {
  id: string
  telegram_id: string
  name: string
  username?: string
  invite_link?: string
  status: 'active' | 'inactive' | 'blacklisted_temp' | 'blacklisted_perm'
  message_count: number
  last_message_sent?: string
  created_at: string
}

export interface GroupStats {
  total: number
  active: number
  inactive: number
  temp_blacklisted: number
  perm_blacklisted: number
}

export interface MessageTemplate {
  id: string
  name: string
  content: string
  is_default: boolean
  usage_count: number
  last_used_at?: string
  created_at: string
}

export interface ApiError {
  detail: string
  errors?: Array<{
    loc: (string | number)[]
    msg: string
    type: string
  }>
}

// Request types
export interface LoginRequest {
  username: string
  password: string
}

export interface RegisterRequest {
  username: string
  email: string
  password: string
  full_name: string
}

export interface CreateSessionRequest {
  api_id: number
  api_hash: string
  phone_number: string
}

export interface AuthenticateSessionRequest {
  session_id: string
  phone_code?: string
  password?: string
}

export interface AddGroupRequest {
  session_id: string
  identifier: string
}

export interface BulkAddGroupsRequest {
  session_id: string
  identifiers: string[]
}

// Response types
export interface BulkAddGroupsResponse {
  added: Array<{
    identifier: string
    name: string
    group_id: string
  }>
  skipped: Array<{
    identifier: string
    name: string
    reason: string
  }>
  errors: Array<{
    identifier: string
    error: string
  }>
}

// Store types
export interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
}

export interface AuthActions {
  login: (credentials: LoginRequest) => Promise<void>
  register: (data: RegisterRequest) => Promise<void>
  logout: () => void
  updateUser: (user: User) => void
  setLoading: (loading: boolean) => void
}

export interface TelegramState {
  sessions: TelegramSession[]
  activeSession: TelegramSession | null
  isLoading: boolean
}

export interface TelegramActions {
  setSessions: (sessions: TelegramSession[]) => void
  addSession: (session: TelegramSession) => void
  updateSession: (sessionId: string, updates: Partial<TelegramSession>) => void
  removeSession: (sessionId: string) => void
  setActiveSession: (session: TelegramSession | null) => void
  setLoading: (loading: boolean) => void
}

export interface AppState {
  theme: 'light' | 'dark' | 'system'
  sidebarCollapsed: boolean
}

export interface AppActions {
  setTheme: (theme: 'light' | 'dark' | 'system') => void
  toggleSidebar: () => void
  setSidebarCollapsed: (collapsed: boolean) => void
}