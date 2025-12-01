import { api } from './api'

class CachedAPI {
  constructor() {
    this.cache = new Map()
    this.cacheTimeout = 5 * 60 * 1000 // 5 minutes
  }

  // Memory cache for frequently accessed data
  setMemoryCache(key, data) {
    this.cache.set(key, {
      data,
      timestamp: Date.now()
    })
  }

  getMemoryCache(key) {
    const cached = this.cache.get(key)
    if (cached && (Date.now() - cached.timestamp) < this.cacheTimeout) {
      return cached.data
    }
    this.cache.delete(key)
    return null
  }

  clearMemoryCache(pattern = null) {
    if (pattern) {
      for (const key of this.cache.keys()) {
        if (key.includes(pattern)) {
          this.cache.delete(key)
        }
      }
    } else {
      this.cache.clear()
    }
  }

  // Enhanced GET with caching headers support
  async get(url, config = {}) {
    const cacheKey = `GET:${url}`
    
    // Check memory cache first
    const cachedData = this.getMemoryCache(cacheKey)
    if (cachedData && !config.forceRefresh) {
      return {
        ...cachedData,
        cached: true
      }
    }

    const response = await api.get(url, config)
    
    // Cache the response if it's cacheable
    if (this.shouldCache(response, config)) {
      this.setMemoryCache(cacheKey, response.data)
    }

    return response.data
  }

  shouldCache(response, config) {
    // Don't cache if explicitly disabled
    if (config.noCache) return false
    
    // Only cache successful responses
    if (response.status !== 200) return false
    
    // Don't cache large responses
    const contentLength = response.headers['content-length']
    if (contentLength && parseInt(contentLength) > 100000) return false
    
    return true
  }

  // Cache-aware methods for common endpoints
  async getDoctors(search = '', departmentId = null, forceRefresh = false) {
    let url = '/cached/doctors'
    const params = new URLSearchParams()
    
    if (search) params.append('search', search)
    if (departmentId) params.append('department_id', departmentId)
    
    if (params.toString()) {
      url += `?${params.toString()}`
    }

    return this.get(url, { forceRefresh })
  }

  async getDoctorDetail(doctorId, forceRefresh = false) {
    return this.get(`/cached/doctors/${doctorId}`, { forceRefresh })
  }

  async getDepartments(forceRefresh = false) {
    return this.get('/cached/departments', { forceRefresh })
  }

  async getPatientAppointments(status = '', forceRefresh = false) {
    let url = '/cached/patient/appointments'
    if (status) {
      url += `?status=${status}`
    }
    return this.get(url, { forceRefresh })
  }

  async getDashboardStats(role, forceRefresh = false) {
    switch (role) {
      case 'admin':
        return this.get('/cached/admin/dashboard/stats', { forceRefresh })
      case 'doctor':
        return this.get('/cached/doctor/dashboard/stats', { forceRefresh })
      case 'patient':
        return this.get('/cached/patient/dashboard/stats', { forceRefresh })
      default:
        throw new Error('Invalid role for dashboard stats')
    }
  }

  // Cache management
  async clearCache(pattern = null) {
    try {
      await api.post('/cached/cache/clear', { pattern })
      this.clearMemoryCache(pattern)
      return { success: true }
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Failed to clear cache' 
      }
    }
  }

  async getCacheStats() {
    try {
      const response = await api.get('/cached/cache/stats')
      return { success: true, data: response.data }
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Failed to get cache stats' 
      }
    }
  }
}

export const cachedApi = new CachedAPI()