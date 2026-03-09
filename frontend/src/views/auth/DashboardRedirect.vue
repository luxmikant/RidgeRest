<template>
  <div class="min-h-[80vh] flex items-center justify-center">
    <p class="text-gray-500 dark:text-gray-400">Redirecting...</p>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUser } from '@clerk/vue'
import api from '../../api'

const router = useRouter()
const { user, isLoaded } = useUser()

onMounted(async () => {
  let attempts = 0
  while (!isLoaded.value && attempts < 30) {
    await new Promise(r => setTimeout(r, 200))
    attempts++
  }

  if (!user.value) {
    router.replace('/login')
    return
  }

  // Try publicMetadata first (fast, no network)
  let role = user.value.publicMetadata?.role

  if (!role) {
    // Fallback: fetch from backend (creates profile if missing)
    try {
      const { data } = await api.get('/auth/me')
      role = data.role
    } catch {
      router.replace('/setup-role')
      return
    }
  }

  if (!role) {
    router.replace('/setup-role')
    return
  }

  router.replace(role === 'employer' ? '/employer/dashboard' : '/employee/dashboard')
})
</script>
