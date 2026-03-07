import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  {
    path: '/',
    redirect: () => {
      const auth = useAuthStore()
      if (!auth.user) return '/login'
      return auth.user.role === 'employer' ? '/employer/dashboard' : '/employee/dashboard'
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
    path: '/oauth-callback',
    name: 'OAuthCallback',
    component: () => import('../views/auth/OAuthCallback.vue'),
    meta: { guest: true },
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

router.beforeEach(async (to, from, next) => {
  const auth = useAuthStore()

  // Wait for initial auth check
  if (!auth.initialized) {
    await auth.fetchMe()
  }

  // Guest-only routes (login, signup)
  if (to.meta.guest && auth.user) {
    return next(auth.user.role === 'employer' ? '/employer/dashboard' : '/employee/dashboard')
  }

  // Protected routes
  if (to.meta.requiresAuth && !auth.user) {
    return next('/login')
  }

  // Role check
  if (to.meta.role && auth.user && auth.user.role !== to.meta.role) {
    return next(auth.user.role === 'employer' ? '/employer/dashboard' : '/employee/dashboard')
  }

  next()
})

export default router
