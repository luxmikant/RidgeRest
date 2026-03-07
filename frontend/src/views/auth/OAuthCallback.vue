<template>
  <div class="min-h-[80vh] flex items-center justify-center">
    <div class="text-center">
      <div class="animate-spin h-10 w-10 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-4"></div>
      <p class="text-gray-500 dark:text-gray-400">Completing sign-in...</p>
      <p v-if="error" class="text-red-500 mt-4 text-sm">{{ error }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'

const authStore = useAuthStore()
const router = useRouter()
const error = ref('')

onMounted(async () => {
  try {
    await authStore.fetchMe()
    if (authStore.user) {
      const role = authStore.user.role
      router.replace(role === 'employer' ? '/employer/dashboard' : '/employee/dashboard')
    } else {
      error.value = 'Authentication failed. Please try again.'
    }
  } catch {
    error.value = 'Something went wrong. Redirecting to login...'
    setTimeout(() => router.replace('/login'), 2000)
  }
})
</script>
