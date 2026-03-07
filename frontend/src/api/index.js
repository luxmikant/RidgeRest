import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  withCredentials: true, // Send httpOnly cookies
  headers: { 'Content-Type': 'application/json' },
})

// Response interceptor: auto-logout on 401
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      const { useAuthStore } = await import('../stores/auth')
      const authStore = useAuthStore()
      authStore.clearUser()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api
