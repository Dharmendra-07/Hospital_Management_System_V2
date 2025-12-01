import { defineStore } from 'pinia'
import { cachedApi } from '@/services/cached_api'

export const useCachedDoctorStore = defineStore('cachedDoctor', {
  state: () => ({
    doctors: [],
    currentDoctor: null,
    departments: [],
    loading: false,
    lastFetch: null
  }),

  getters: {
    shouldRefresh: (state) => {
      if (!state.lastFetch) return true
      const now = Date.now()
      return (now - state.lastFetch) > 300000 // 5 minutes
    }
  },

  actions: {
    async fetchDoctors(search = '', departmentId = null, forceRefresh = false) {
      try {
        this.loading = true
        
        // Use cache unless forceRefresh is true or data is stale
        const useCache = !forceRefresh && !this.shouldRefresh
        
        const data = await cachedApi.getDoctors(search, departmentId, !useCache)
        
        this.doctors = data.doctors
        this.lastFetch = Date.now()
        
        return { 
          success: true, 
          data,
          cached: data.cached || false
        }
      } catch (error) {
        return { 
          success: false, 
          error: error.response?.data?.error || 'Failed to fetch doctors' 
        }
      } finally {
        this.loading = false
      }
    },

    async fetchDoctorDetail(doctorId, forceRefresh = false) {
      try {
        const data = await cachedApi.getDoctorDetail(doctorId, forceRefresh)
        this.currentDoctor = data
        return { 
          success: true, 
          data,
          cached: data.cached || false
        }
      } catch (error) {
        return { 
          success: false, 
          error: error.response?.data?.error || 'Failed to fetch doctor details' 
        }
      }
    },

    async fetchDepartments(forceRefresh = false) {
      try {
        const data = await cachedApi.getDepartments(forceRefresh)
        this.departments = data.departments
        return { 
          success: true, 
          data,
          cached: data.cached || false
        }
      } catch (error) {
        return { 
          success: false, 
          error: error.response?.data?.error || 'Failed to fetch departments' 
        }
      }
    },

    invalidateCache() {
      cachedApi.clearMemoryCache()
      this.lastFetch = null
    }
  }
})