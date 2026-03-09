import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

// Uses window.Clerk (imperative API) so this store is safe to call from
// any context (router guards, Pinia setup) without needing inject().
export const useAuthStore = defineStore('auth', () => {
  const isLoaded = ref(false)
  const isSignedIn = ref(false)
  const _clerkUser = ref(null)

  function _sync(resources) {
    const u = resources?.user ?? window.Clerk?.user ?? null
    isLoaded.value = true
    isSignedIn.value = !!u
    _clerkUser.value = u
  }

  if (typeof window !== 'undefined') {
    function _connect() {
      if (window.Clerk?.loaded) {
        _sync()
        window.Clerk.addListener(_sync)
      } else {
        setTimeout(_connect, 50)
      }
    }
    _connect()
  }

  const initialized = isLoaded

  const user = computed(() => {
    const u = _clerkUser.value
    if (!u) return null
    return {
      id: u.id,
      name: u.fullName ||
            u.firstName ||
            u.primaryEmailAddress?.emailAddress?.split('@')[0] ||
            'User',
      email: u.primaryEmailAddress?.emailAddress || '',
      role: u.publicMetadata?.role || null,
      auth_provider: 'clerk',
    }
  })

  async function logout() {
    await window.Clerk?.signOut()
  }

  function redirectToLogin() {
    window.Clerk?.redirectToSignIn({ afterSignInUrl: '/dashboard-redirect' })
  }

  function redirectToSignup() {
    window.Clerk?.redirectToSignUp({ afterSignUpUrl: '/setup-role' })
  }

  async function fetchMe() {}

  return {
    user,
    isLoaded,
    isSignedIn,
    initialized,
    logout,
    fetchMe,
    redirectToLogin,
    redirectToSignup,
  }
})

