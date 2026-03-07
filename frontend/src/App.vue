<template>
  <div :class="{ dark: isDark }" class="min-h-screen">
    <Navbar v-if="authStore.user" />
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <router-view />
    </main>
    <Toast />
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useAuthStore } from './stores/auth'
import Navbar from './components/Navbar.vue'
import Toast from './components/Toast.vue'

const authStore = useAuthStore()

const isDark = computed(() => {
  return localStorage.getItem('theme') === 'dark'
})

onMounted(async () => {
  // Apply saved theme
  if (localStorage.getItem('theme') === 'dark') {
    document.documentElement.classList.add('dark')
  }
  // Try to hydrate user from cookie
  await authStore.fetchMe()
})
</script>
