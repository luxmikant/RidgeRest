import { defineStore } from 'pinia'
import { computed } from 'vue'
import { useUser, useAuth, useClerk } from '@clerk/vue'

export const useAuthStore = defineStore('auth', () => {
  const { user: clerkUser, isLoaded, isSignedIn } = useUser()
  const { getToken, signOut } = useAuth()
  const clerk = useClerk()

  // Normalize Clerk user shape to match what existing components expect
  const user = computed(() => {
    if (!clerkUser.value) return null
    return {
      id: clerkUser.value.id,
      name: clerkUser.value.fullName ||
            clerkUser.value.firstName ||
            clerkUser.value.primaryEmailAddress?.emailAddress?.split('@')[0] ||
            'User',
      email: clerkUser.value.primaryEmailAddress?.emailAddress || '',
      role: clerkUser.value.publicMetadata?.role || null,
      auth_provider: 'clerk',
    }
  })

  // Alias used in router guards
  const initialized = isLoaded

  async function logout() {
    await signOut()
  }

  function redirectToLogin() {
    clerk.value?.redirectToSignIn({ afterSignInUrl: '/dashboard-redirect' })
  }

  function redirectToSignup() {
    clerk.value?.redirectToSignUp({ afterSignUpUrl: '/setup-role' })
  }

  // Legacy no-op kept so any component that calls fetchMe() doesn't throw
  async function fetchMe() {}

  return {
    user,
    isLoaded,
    isSignedIn,
    initialized,
    getToken,
    logout,
    fetchMe,
    redirectToLogin,
    redirectToSignup,
  }
})

