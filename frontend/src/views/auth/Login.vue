<template>
  <div class="min-h-[80vh] flex items-center justify-center">
    <div class="w-full max-w-md bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-8">
      <h1 class="text-2xl font-bold text-center mb-6 text-gray-800 dark:text-white">Sign In</h1>

      <form @submit.prevent="handleLogin" class="space-y-4">
        <div>
          <label class="label">Email</label>
          <input v-model="form.email" type="email" required class="input" placeholder="you@example.com" />
        </div>
        <div>
          <label class="label">Password</label>
          <input v-model="form.password" type="password" required class="input" placeholder="••••••••" />
        </div>

        <p v-if="error" class="text-red-500 text-sm">{{ error }}</p>

        <button type="submit" :disabled="loading" class="btn-primary w-full">
          {{ loading ? 'Signing in...' : 'Sign In' }}
        </button>
      </form>

      <div class="my-6 flex items-center gap-4">
        <hr class="flex-1 border-gray-300 dark:border-gray-600" />
        <span class="text-xs text-gray-400">OR</span>
        <hr class="flex-1 border-gray-300 dark:border-gray-600" />
      </div>

      <div class="space-y-2">
        <button @click="googleLogin('employee')" class="btn-google w-full">
          <img src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg" alt="G" class="w-5 h-5" />
          Continue as Employee with Google
        </button>
        <button @click="googleLogin('employer')" class="btn-google w-full">
          <img src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg" alt="G" class="w-5 h-5" />
          Continue as Employer with Google
        </button>
      </div>

      <p class="text-center text-sm text-gray-500 mt-6">
        Don't have an account?
        <router-link to="/signup" class="text-blue-600 hover:underline">Sign Up</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'

const authStore = useAuthStore()
const router = useRouter()

const form = ref({ email: '', password: '' })
const error = ref('')
const loading = ref(false)

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    await authStore.login(form.value.email, form.value.password)
    const role = authStore.user?.role
    router.push(role === 'employer' ? '/employer/dashboard' : '/employee/dashboard')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Login failed'
  } finally {
    loading.value = false
  }
}

function googleLogin(role) {
  authStore.googleLogin(role)
}
</script>

<style scoped>
.label { @apply block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1; }
.input { @apply w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:outline-none; }
.btn-primary { @apply py-2.5 rounded-lg bg-blue-600 text-white font-medium hover:bg-blue-700 disabled:opacity-50 transition; }
.btn-google { @apply flex items-center justify-center gap-3 py-2.5 rounded-lg border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 text-sm font-medium text-gray-700 dark:text-gray-200 transition; }
</style>
