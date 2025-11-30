import { defineStore } from 'pinia'
import { api } from '@/services/api'

export const useAuthStore = defineStore('auth', {
state: () => ({
  user: null,
  token: localStorage.getItem('token') || null,
  isAuthenticated: !!localStorage.getItem('token')
}),

getters: {
  isAdmin: (state) => state.user?.role === 'admin',
  isDoctor: (state) => state.user?.role === 'doctor',
  isPatient: (state) => state.user?.role === 'patient',
  userProfile: (state) => state.user?.profile || {}
},

actions: {
  async login(credentials) {
    try {
      const response = await api.post('/auth/login', credentials)
      
      this.user = response.data.user
      this.token = response.data.token
      this.isAuthenticated = true
      
      // Store token in localStorage
      localStorage.setItem('token', this.token)
      
      // Set default authorization header
      api.defaults.headers.common['Authorization'] = `Bearer ${this.token}`
      
      return { success: true, data: response.data }
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Login failed' 
      }
    }
  },

  async register(userData) {
    try {
      const response = await api.post('/auth/register', userData)
      
      this.user = response.data.user
      this.token = response.data.token
      this.isAuthenticated = true
      
      localStorage.setItem('token', this.token)
      api.defaults.headers.common['Authorization'] = `Bearer ${this.token}`
      
      return { success: true, data: response.data }
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Registration failed' 
      }
    }
  },

  async logout() {
    try {
      await api.post('/auth/logout')
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      this.user = null
      this.token = null
      this.isAuthenticated = false
      
      localStorage.removeItem('token')
      delete api.defaults.headers.common['Authorization']
    }
  },

  async checkAuth() {
    if (!this.token) return false

    try {
      api.defaults.headers.common['Authorization'] = `Bearer ${this.token}`
      const response = await api.get('/auth/me')
      
      this.user = response.data.user
      this.isAuthenticated = true
      
      return true
    } catch (error) {
      this.logout()
      return false
    }
  }
}
})