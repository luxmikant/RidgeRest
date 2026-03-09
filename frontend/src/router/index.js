import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  {
    path: '/',
    redirect: () => {
      const auth = useAuthStore()
      if (!auth.isSignedIn) return '/login'
      return auth.user?.role === 'employer' ? '/employer/dashboard' : '/employee/dashboard'
    },
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/auth/Login.vue'),
    meta: { guest: true },
  },
  {
    path: '/signup',
    name: 'Signup',
    component: () => import('../views/auth/Signup.vue'),
    meta: { guest: true },
  },
  {
    path: '/setup-role',
    name: 'SetupRole',
    component: () => import('../views/auth/SetupRole.vue'),
  },
  {
    path: '/dashboard-redirect',
    name: 'DashboardRedirect',
    component: () => import('../views/auth/DashboardRedirect.vue'),
  },
  // Employee routes
  {
    path: '/employee/dashboard',
    name: 'EmployeeDashboard',
    component: () => import('../views/employee/Dashboard.vue'),
    meta: { requiresAuth: true, role: 'employee' },
  },
  {
    path: '/employee/apply',
    name: 'ApplyLeave',
    component: () => import('../views/employee/ApplyLeave.vue'),
    meta: { requiresAuth: true, role: 'employee' },
  },
  {
    path: '/employee/history',
    name: 'LeaveHistory',
    component: () => import('../views/employee/LeaveHistory.vue'),
    meta: { requiresAuth: true, role: 'employee' },
  },
  // Employer routes
  {
    path: '/employer/dashboard',
    name: 'EmployerDashboard',
    component: () => import('../views/employer/Dashboard.vue'),
    meta: { requiresAuth: true, role: 'employer' },
  },
  {
    path: '/employer/requests',
    name: 'LeaveRequests',
    component: () => import('../views/employer/Requests.vue'),
    meta: { requiresAuth: true, role: 'employer' },
  },
  {
    path: '/employer/calendar',
    name: 'TeamCalendar',
    component: () => import('../views/employer/Calendar.vue'),
    meta: { requiresAuth: true, role: 'employer' },
  },
  {
    path: '/employer/analytics',
    name: 'Analytics',
    component: () => import('../views/employer/Analytics.vue'),
    meta: { requiresAuth: true, role: 'employer' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()

  // Wait for Clerk to finish loading (max 3 seconds)
  let waited = 0
  while (!auth.isLoaded && waited < 30) {
    await new Promise((r) => setTimeout(r, 100))
    waited++
  }

  // Guest-only routes: redirect signed-in users away
  if (to.meta.guest && auth.isSignedIn) {
    return '/dashboard-redirect'
  }

  // Protected routes: redirect unauthenticated users to login
  if (to.meta.requiresAuth && !auth.isSignedIn) {
    return '/login'
  }

  // Signed in but no role set yet: send to onboarding
  if (to.meta.requiresAuth && auth.isSignedIn && !auth.user?.role) {
    return '/setup-role'
  }

  // Role mismatch: redirect to correct dashboard
  if (to.meta.role && auth.user?.role && auth.user.role !== to.meta.role) {
    return auth.user.role === 'employer' ? '/employer/dashboard' : '/employee/dashboard'
  }
})

export default router

