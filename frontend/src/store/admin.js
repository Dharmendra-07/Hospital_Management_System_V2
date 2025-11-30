import { defineStore } from 'pinia'
import { api } from '@/services/api'

export const useAdminStore = defineStore('admin', {
  state: () => ({
    stats: null,
    doctors: [],
    patients: [],
    appointments: [],
    departments: [],
    loading: false
  }),

  actions: {
    async fetchDashboardStats() {
      try {
        const response = await api.get('/admin/dashboard/stats')
        this.stats = response.data
        return { success: true, data: response.data }
      } catch (error) {
        return { 
          success: false, 
          error: error.response?.data?.error || 'Failed to fetch dashboard stats' 
        }
      }
    },

    async fetchDoctors(search = '', departmentId = null) {
      try {
        this.loading = true
        const params = {}
        if (search) params.search = search
        if (departmentId) params.department_id = departmentId

        const response = await api.get('/admin/doctors', { params })
        this.doctors = response.data.doctors
        return { success: true, data: response.data }
      } catch (error) {
        return { 
          success: false, 
          error: error.response?.data?.error || 'Failed to fetch doctors' 
        }
      } finally {
        this.loading = false
      }
    },

    async addDoctor(doctorData) {
      try {
        const response = await api.post('/admin/doctors', doctorData)
        await this.fetchDoctors() // Refresh list
        return { success: true, data: response.data }
      } catch (error) {
        return { 
          success: false, 
          error: error.response?.data?.error || 'Failed to add doctor' 
        }
      }
    },

    async updateDoctor(doctorId, doctorData) {
      try {
        const response = await api.put(`/admin/doctors/${doctorId}`, doctorData)
        await this.fetchDoctors() // Refresh list
        return { success: true, data: response.data }
      } catch (error) {
        return { 
          success: false, 
          error: error.response?.data?.error || 'Failed to update doctor' 
        }
      }
    },

    async deleteDoctor(doctorId) {
      try {
        const response = await api.delete(`/admin/doctors/${doctorId}`)
        await this.fetchDoctors() // Refresh list
        return { success: true, data: response.data }
      } catch (error) {
        return { 
          success: false, 
          error: error.response?.data?.error || 'Failed to delete doctor' 
        }
      }
    },

    async fetchPatients(search = '') {
      try {
        this.loading = true
        const params = {}
        if (search) params.search = search

        const response = await api.get('/admin/patients', { params })
        this.patients = response.data.patients
        return { success: true, data: response.data }
      } catch (error) {
        return { 
          success: false, 
          error: error.response?.data?.error || 'Failed to fetch patients' 
        }
      } finally {
        this.loading = false
      }
    },

    async updatePatient(patientId, patientData) {
      try {
        const response = await api.put(`/admin/patients/${patientId}`, patientData)
        await this.fetchPatients() // Refresh list
        return { success: true, data: response.data }
      } catch (error) {
        return { 
          success: false, 
          error: error.response?.data?.error || 'Failed to update patient' 
        }
      }
    },

    async fetchAppointments(status = '', dateFrom = '', dateTo = '') {
      try {
        this.loading = true
        const params = {}
        if (status) params.status = status
        if (dateFrom) params.date_from = dateFrom
        if (dateTo) params.date_to = dateTo

        const response = await api.get('/admin/appointments', { params })
        this.appointments = response.data.appointments
        return { success: true, data: response.data }
      } catch (error) {
        return { 
          success: false, 
          error: error.response?.data?.error || 'Failed to fetch appointments' 
        }
      } finally {
        this.loading = false
      }
    },

    async fetchDepartments() {
      try {
        const response = await api.get('/admin/departments')
        this.departments = response.data.departments
        return { success: true, data: response.data }
      } catch (error) {
        return { 
          success: false, 
          error: error.response?.data?.error || 'Failed to fetch departments' 
        }
      }
    },

    async addDepartment(departmentData) {
      try {
        const response = await api.post('/admin/departments', departmentData)
        await this.fetchDepartments() // Refresh list
        return { success: true, data: response.data }
      } catch (error) {
        return { 
          success: false, 
          error: error.response?.data?.error || 'Failed to add department' 
        }
      }
    }
  }
})