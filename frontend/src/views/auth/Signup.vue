<template>
  <div class="min-h-[80vh] flex items-center justify-center">
    <div class="w-full max-w-md bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-8">
      <h1 class="text-2xl font-bold text-center mb-2 text-gray-800 dark:text-white">Create Account</h1>
      <p class="text-center text-gray-500 dark:text-gray-400 mb-8">Choose your role to get started</p>

      <div class="grid grid-cols-2 gap-4 mb-8">
        <button
          @click="selectedRole = 'employee'"
          :class="['role-card', selectedRole === 'employee' && 'selected']"
        >
          <span class="text-3xl mb-2">&#x1F464;</span>
          <span class="font-medium text-gray-800 dark:text-white">Employee</span>
          <span class="text-xs text-gray-500 dark:text-gray-400">Apply for leaves</span>
        </button>
        <button
          @click="selectedRole = 'employer'"
          :class="['role-card', selectedRole === 'employer' && 'selected']"
        >
          <span class="text-3xl mb-2">&#x1F3E2;</span>
          <span class="font-medium text-gray-800 dark:text-white">Employer</span>
          <span class="text-xs text-gray-500 dark:text-gray-400">Manage team leaves</span>
        </button>
      </div>

      <button @click="proceed" :disabled="!selectedRole" class="btn-primary w-full">
        Continue as {{ selectedRole || '...' }}
      </button>

      <p class="text-center text-sm text-gray-500 mt-6">
        Already have an account?
        <router-link to="/login" class="text-blue-600 hover:underline">Sign In</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useClerk } from '@clerk/vue'

const clerk = useClerk()
const selectedRole = ref('')

function proceed() {
  if (!selectedRole.value) return
  localStorage.setItem('pendingRole', selectedRole.value)
  clerk.value?.redirectToSignUp({ afterSignUpUrl: '/setup-role' })
}
</script>

<style scoped>
.role-card {
  @apply flex flex-col items-center p-6 border-2 border-gray-200 dark:border-gray-600 rounded-xl cursor-pointer hover:border-blue-400 dark:hover:border-blue-500 transition-all;
}
.role-card.selected {
  @apply border-blue-500 bg-blue-50 dark:bg-blue-900/20;
}
.btn-primary { @apply py-2.5 rounded-lg bg-blue-600 text-white font-medium hover:bg-blue-700 disabled:opacity-50 transition; }
</style>
