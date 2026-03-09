<template>
  <div class="min-h-[80vh] flex items-center justify-center">
    <div class="w-full max-w-sm bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-8 text-center">
      <p v-if="message" class="text-gray-600 dark:text-gray-300">{{ message }}</p>
      <p v-if="errorMsg" class="text-red-500 text-sm mt-4">{{ errorMsg }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUser } from '@clerk/vue'
import api from '../../api'

const router = useRouter()
const { user, isLoaded } = useUser()

const message = ref('Setting up your account...')
const errorMsg = ref('')

onMounted(async () => {
  // Wait for Clerk to be ready
  let attempts = 0
  while (!isLoaded.value && attempts < 30) {
    await new Promise(r => setTimeout(r, 200))
    attempts++
  }

  if (!user.value) {
    router.replace('/login')
    return
  }

  const role = localStorage.getItem('pendingRole')
  if (!role) {
    // Already set up — just redirect
    router.replace('/dashboard-redirect')
    return
  }

  try {
    await api.patch('/auth/me/role', {
      role,
      name: user.value.fullName || `${user.value.firstName || ''} ${user.value.lastName || ''}`.trim(),
      email: user.value.primaryEmailAddress?.emailAddress || '',
    })
    localStorage.removeItem('pendingRole')
    message.value = 'Account ready! Redirecting...'
    router.replace('/dashboard-redirect')
  } catch (e) {
    errorMsg.value = e.response?.data?.detail || 'Setup failed. Please try again.'
  }
})
</script>
