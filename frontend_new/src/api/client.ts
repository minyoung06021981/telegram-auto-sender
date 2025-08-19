import axios, { AxiosInstance, AxiosError } from 'axios'
import { ApiError } from '@/types'

class ApiClient {
  private instance: AxiosInstance
  private token: string | null = null

  constructor() {
    this.instance = axios.create({
      baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8001/api',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Request interceptor to add auth token
    this.instance.interceptors.request.use(
      (config) => {
        if (this.token && config.headers) {
          config.headers.Authorization = `Bearer ${this.token}`
        }
        return config
      },
      (error) => {
        return Promise.reject(error)
      }
    )

    // Response interceptor for error handling
    this.instance.interceptors.response.use(
      (response) => response,
      (error: AxiosError<ApiError>) => {
        // Handle specific error cases
        if (error.response?.status === 401) {
          // Token expired or invalid - redirect to login
          this.clearToken()
          window.location.href = '/login'
        }

        // Transform error to our ApiError format
        const apiError: ApiError = {
          detail: error.response?.data?.detail || error.message || 'An error occurred',
          errors: error.response?.data?.errors,
        }

        return Promise.reject(apiError)
      }
    )
  }

  setToken(token: string) {
    this.token = token
  }

  clearToken() {
    this.token = null
  }

  getToken() {
    return this.token
  }

  // HTTP methods
  async get<T>(url: string, config?: any): Promise<T> {
    const response = await this.instance.get(url, config)
    return response.data
  }

  async post<T>(url: string, data?: any, config?: any): Promise<T> {
    const response = await this.instance.post(url, data, config)
    return response.data
  }

  async put<T>(url: string, data?: any, config?: any): Promise<T> {
    const response = await this.instance.put(url, data, config)
    return response.data
  }

  async patch<T>(url: string, data?: any, config?: any): Promise<T> {
    const response = await this.instance.patch(url, data, config)
    return response.data
  }

  async delete<T>(url: string, config?: any): Promise<T> {
    const response = await this.instance.delete(url, config)
    return response.data
  }
}

export const apiClient = new ApiClient()