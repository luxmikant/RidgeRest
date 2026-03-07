<template>
  <div class="min-h-[80vh] flex items-center justify-center">
    <div class="w-full max-w-md bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-8">
      <h1 class="text-2xl font-bold text-center mb-6 text-gray-800 dark:text-white">Create Account</h1>

      <form @submit.prevent="handleSignup" class="space-y-4">
        <div>
          <label class="label">Full Name</label>
          <input v-model="form.name" type="text" required minlength="2" class="input" placeholder="John Doe" />
        </div>
        <div>
          <label class="label">Email</label>
          <input v-model="form.email" type="email" required class="input" placeholder="you@example.com" />
        </div>
        <div>
          <label class="label">Password</label>
          <input v-model="form.password" type="password" required minlength="8" class="input" placeholder="Min 8 characters" />
        </div>
        <div>
          <label class="label">Role</label>
          <select v-model="form.role" class="input">
            <option value="employee">Employee</option>
            <option value="employer">Employer</option>
          </select>
        </div>

        <p v-if="error" class="text-red-500 text-sm">{{ error }}</p>

        <button type="submit" :disabled="loading" class="btn-primary w-full">
          {{ loading ? 'Creating account...' : 'Sign Up' }}
        </button>
      </form>

      <p class="text-center text-sm text-gray-500 mt-6">
        Already have an account?
        <router-link to="/login" class="text-blue-600 hover:underline">Sign In</router-link>
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

const form = ref({ name: '', email: '', password: '', role: 'employee' })
const error = ref('')
const loading = ref(false)

async function handleSignup() {
  error.value = ''
  loading.value = true
  try {
    await authStore.signup(form.value)
    const role = authStore.user?.role
    router.push(role === 'employer' ? '/employer/dashboard' : '/employee/dashboard')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Signup failed'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.label { @apply block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1; }
.input { @apply w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:outline-none; }
.btn-primary { @apply py-2.5 rounded-lg bg-blue-600 text-white font-medium hover:bg-blue-700 disabled:opacity-50 transition; }
</style>
