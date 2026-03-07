import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const initialized = ref(false)
  const loading = ref(false)

  async function fetchMe() {
    try {
      const res = await api.get('/api/auth/me')
      user.value = res.data
      // Set Datadog RUM user
      if (window.DD_RUM) {
        window.DD_RUM.setUser({
          id: res.data.id,
          name: res.data.name,
          email: res.data.email,
          role: res.data.role,
        })
      }
    } catch {
      user.value = null
    } finally {
      initialized.value = true
    }
  }

  async function login(email, password) {
    loading.value = true
    try {
      const res = await api.post('/api/auth/login', { email, password })
      user.value = res.data.user
      return res.data
    } finally {
      loading.value = false
    }
  }

  async function signup(name, email, password, role, department = '') {
    loading.value = true
    try {
      const res = await api.post('/api/auth/signup', {
        name, email, password, role, department,
      })
      user.value = res.data.user
      return res.data
    } finally {
      loading.value = false
    }
  }

  async function logout() {
    try {
      await api.post('/api/auth/logout')
    } catch {
      // Ignore errors
    }
    clearUser()
  }

  function clearUser() {
    user.value = null
    initialized.value = true
  }

  function googleLogin(role) {
    const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
    window.location.href = `${baseUrl}/api/auth/google?role=${role}`
  }

  return { user, initialized, loading, fetchMe, login, signup, logout, clearUser, googleLogin }
})
