import { defineStore } from 'pinia'
import { api } from '@/services/api'

export const useTaskStore = defineStore('tasks', {
  state: () => ({
    exports: [],
    currentTask: null,
    loading: false
  }),

  actions: {
    async exportPatientHistory() {
      try {
        this.loading = true
        const response = await api.post('/tasks/export/patient-history')
        this.currentTask = response.data
        return { success: true, data: response.data }
      } catch (error) {
        return { 
          success: false, 
          error: error.response?.data?.error || 'Failed to start export' 
        }
      } finally {
        this.loading = false
      }
    },

    async exportDoctorAppointments(startDate, endDate) {
      try {
        this.loading = true
        const response = await api.post('/tasks/export/doctor-appointments', {
          start_date: startDate,
          end_date: endDate
        })
        this.currentTask = response.data
        return { success: true, data: response.data }
      } catch (error) {
        return { 
          success: false, 
          error: error.response?.data?.error || 'Failed to start export' 
        }
      } finally {
        this.loading = false
      }
    },

    async generateCustomReport(startDate, endDate, email = null) {
      try {
        this.loading = true
        const response = await api.post('/tasks/reports/custom', {
          start_date: startDate,
          end_date: endDate,
          email: email
        })
        this.currentTask = response.data
        return { success: true, data: response.data }
      } catch (error) {
        return { 
          success: false, 
          error: error.response?.data?.error || 'Failed to generate report' 
        }
      } finally {
        this.loading = false
      }
    },

    async getTaskStatus(taskId) {
      try {
        const response = await api.get(`/tasks/status/${taskId}`)
        return { success: true, data: response.data }
      } catch (error) {
        return { 
          success: false, 
          error: error.response?.data?.error || 'Failed to get task status' 
        }
      }
    },

    async pollTaskStatus(taskId, interval = 2000, maxAttempts = 30) {
      let attempts = 0
      
      const poll = async () => {
        attempts++
        const result = await this.getTaskStatus(taskId)
        
        if (result.success) {
          const status = result.data.status
          
          if (status === 'SUCCESS' || status === 'FAILURE' || attempts >= maxAttempts) {
            return result
          } else {
            // Continue polling
            await new Promise(resolve => setTimeout(resolve, interval))
            return await poll()
          }
        } else {
          return result
        }
      }
      
      return await poll()
    },

    async downloadExport(exportId) {
      try {
        const response = await api.get(`/tasks/download/${exportId}`, {
          responseType: 'blob'
        })
        
        // Create download link
        const blob = new Blob([response.data], { type: 'text/csv' })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `export-${exportId}.csv`)
        document.body.appendChild(link)
        link.click()
        link.remove()
        window.URL.revokeObjectURL(url)
        
        return { success: true }
      } catch (error) {
        return { 
          success: false, 
          error: error.response?.data?.error || 'Failed to download export' 
        }
      }
    }
  }
})