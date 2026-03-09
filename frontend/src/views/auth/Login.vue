<template>
  <div class="min-h-[80vh] flex items-center justify-center">
    <div class="w-full max-w-md bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-8 text-center">
      <h1 class="text-2xl font-bold mb-2 text-gray-800 dark:text-white">Welcome to RidgeRest</h1>
      <p class="text-gray-500 dark:text-gray-400 mb-8">Sign in to manage your leaves</p>

      <button @click="signIn" class="btn-primary w-full">
        Sign In
      </button>

      <p class="text-center text-sm text-gray-500 mt-6">
        Don't have an account?
        <router-link to="/signup" class="text-blue-600 hover:underline">Sign Up</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { useClerk } from '@clerk/vue'

const clerk = useClerk()

function signIn() {
  clerk.value?.redirectToSignIn({ afterSignInUrl: '/dashboard-redirect' })
}
</script>

<style scoped>
.btn-primary { @apply py-2.5 px-6 rounded-lg bg-blue-600 text-white font-medium hover:bg-blue-700 transition; }
</style>

