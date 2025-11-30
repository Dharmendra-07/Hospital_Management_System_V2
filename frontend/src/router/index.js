import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/store/auth'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/Login.vue'),
    meta: { requiresAuth: false, hideNavbar: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/auth/Register.vue'),
    meta: { requiresAuth: false, hideNavbar: true }
  },
  // Admin Routes
  {
    path: '/admin',
    name: 'AdminDashboard',
    component: () => import('@/views/admin/Dashboard.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  // Doctor Routes
  {
  path: '/doctor',
  name: 'DoctorDashboard',
  component: () => import('@/views/doctor/Dashboard.vue'),
  meta: { requiresAuth: true, requiresDoctor: true }
  },
  // Patient Routes
  {
    path: '/patient',
    name: 'PatientDashboard',
    component: () => import('@/views/patient/Dashboard.vue'),
    meta: { requiresAuth: true, requiresPatient: true }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Route guards
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // Check if route requires authentication
  if (to.meta.requiresAuth) {
    if (!authStore.isAuthenticated) {
      // Try to check authentication status
      const isAuthenticated = await authStore.checkAuth()
      if (!isAuthenticated) {
        return next('/login')
      }
    }

    // Check role-based access
    if (to.meta.requiresAdmin && !authStore.isAdmin) {
      return next('/unauthorized')
    }
    if (to.meta.requiresDoctor && !authStore.isDoctor) {
      return next('/unauthorized')
    }
    if (to.meta.requiresPatient && !authStore.isPatient) {
      return next('/unauthorized')
    }
  }

  // Redirect authenticated users away from auth pages
  if ((to.name === 'Login' || to.name === 'Register') && authStore.isAuthenticated) {
    // Redirect to appropriate dashboard based on role
    if (authStore.isAdmin) return next('/admin')
    if (authStore.isDoctor) return next('/doctor')
    if (authStore.isPatient) return next('/patient')
  }

  next()
})

export default router