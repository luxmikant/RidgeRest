import axios from 'axios'

const api = axios.create({
  baseURL: (import.meta.env.VITE_API_URL || 'http://localhost:8000') + '/api',
  withCredentials: false,
  headers: { 'Content-Type': 'application/json' },
})

// Attach Clerk session token to every request
api.interceptors.request.use(async (config) => {
  try {
    if (window.Clerk?.session) {
      const token = await window.Clerk.session.getToken()
      if (token) config.headers.Authorization = `Bearer ${token}`
    }
  } catch {
    // Clerk not ready yet — request proceeds without auth header
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      if (window.Clerk?.user) {
        // Signed in but no profile — send to onboarding
        window.location.href = '/setup-role'
      } else {
        window.Clerk?.redirectToSignIn()
      }
    }
    return Promise.reject(error)
  }
)

export default api

