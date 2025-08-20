import { apiClient } from './client'
import { 
  AuthResponse, 
  LoginRequest, 
  RegisterRequest, 
  User 
} from '@/types'

class AuthApi {
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    return apiClient.post<AuthResponse>('/auth/login', credentials)
  }

  async register(data: RegisterRequest): Promise<AuthResponse> {
    return apiClient.post<AuthResponse>('/auth/register', data)
  }

  async getCurrentUser(): Promise<User> {
    return apiClient.get<User>('/auth/me')
  }

  async refreshApiToken(): Promise<{ api_token: string }> {
    return apiClient.post<{ api_token: string }>('/auth/refresh-api-token')
  }

  async emergentAuth(sessionId: string): Promise<AuthResponse> {
    return apiClient.post<AuthResponse>('/auth/emergent/callback', { session_id: sessionId })
  }

  setToken(token: string) {
    apiClient.setToken(token)
  }

  clearToken() {
    apiClient.clearToken()
  }
}

export const authApi = new AuthApi()