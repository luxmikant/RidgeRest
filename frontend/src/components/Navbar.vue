<template>
  <nav class="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700 mb-6">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between h-14 items-center">
        <!-- Logo -->
        <router-link to="/" class="text-xl font-bold text-blue-600 dark:text-blue-400">
          RidgeRest
        </router-link>

        <!-- Nav Links -->
        <div class="flex items-center gap-4">
          <template v-if="authStore.user?.role === 'employee'">
            <router-link to="/employee/dashboard" class="nav-link">Dashboard</router-link>
            <router-link to="/employee/apply" class="nav-link">Apply Leave</router-link>
            <router-link to="/employee/history" class="nav-link">History</router-link>
          </template>
          <template v-else-if="authStore.user?.role === 'employer'">
            <router-link to="/employer/dashboard" class="nav-link">Dashboard</router-link>
            <router-link to="/employer/requests" class="nav-link">Requests</router-link>
            <router-link to="/employer/calendar" class="nav-link">Calendar</router-link>
            <router-link to="/employer/analytics" class="nav-link">Analytics</router-link>
          </template>

          <!-- Dark mode toggle -->
          <button @click="toggleDark" class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700">
            <span v-if="isDark">☀️</span>
            <span v-else>🌙</span>
          </button>

          <!-- User info + logout -->
          <span class="text-sm text-gray-500 dark:text-gray-400">
            {{ authStore.user?.name }}
            <span class="text-xs px-2 py-0.5 rounded-full ml-1"
              :class="authStore.user?.role === 'employer' ? 'bg-purple-100 text-purple-700 dark:bg-purple-900 dark:text-purple-300' : 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300'">
              {{ authStore.user?.role }}
            </span>
          </span>

          <button @click="handleLogout" class="text-sm text-red-500 hover:text-red-700">
            Logout
          </button>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useSocketStore } from '../stores/socket'

const authStore = useAuthStore()
const socketStore = useSocketStore()
const router = useRouter()

const isDark = ref(localStorage.getItem('theme') === 'dark')

function toggleDark() {
  isDark.value = !isDark.value
  if (isDark.value) {
    document.documentElement.classList.add('dark')
    localStorage.setItem('theme', 'dark')
  } else {
    document.documentElement.classList.remove('dark')
    localStorage.setItem('theme', 'light')
  }
}

async function handleLogout() {
  socketStore.disconnect()
  await authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.nav-link {
  @apply text-sm text-gray-600 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 transition-colors;
}
.router-link-active {
  @apply text-blue-600 dark:text-blue-400 font-medium;
}
</style>
