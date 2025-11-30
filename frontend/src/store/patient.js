import { defineStore } from 'pinia'
import { api } from '@/services/api'

export const usePatientStore = defineStore('patient', {
  state: () => ({
    stats: null,
    doctors: [],
    appointments: [],
    departments: [],
    medicalHistory: [],
    currentDoctor: null,
    currentAppointment: null,
    loading: false
  }),

  actions: {
    async fetchDashboardStats() {
      try {
        const response = await api.get('/patient/dashboard/stats')
        this.stats = response.data
        return { success: true, data: response.data }
      } catch (error) {
        return { 
          success: false, 
          error: error.response?.data?.error || 'Failed to fetch dashboard stats' 
        }
      }
    },

    async fetchDoctors(search = '', specialization = '', departmentId = null) {
      try {
        this.loading = true
        const params = {}
        if (search) params.search = search
        if (specialization) params.specialization = specialization
        if (departmentId) params.department_id = departmentId

        const response = await api.get('/patient/doctors', { params })
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

    async fetchDoctorDetail(doctorId) {
      try {
        const response = await api.get(`/patient/doctors/${doctorId}`)
        this.currentDoctor = response.data
        return { success: true, data: response.data }
      } catch (error) {
        return { 
          success: false, 
          error: error.response?.data?.error || 'Failed to fetch doctor details' 
        }
      }
    },

    async fetchAppointments(status = '') {
      try {
        this.loading = true
        const params = {}
        if (status) params.status = status

        const response = await api.get('/patient/appointments', { params })
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

    async bookAppointment(appointmentData) {
      try {
        const response = await api.post('/patient/appointments', appointmentData)
        await this.fetchAppointments() // Refresh appointments list
        return { success: true, data: response.data }
      } catch (error) {
        return { 
          success: false, 
          error: error.response?.data?.error || 'Failed to book appointment' 
        }
      }
    },

    async updateAppointment(appointmentId, appointmentData) {
      try {
        const response = await api.put(`/patient/appointments/${appointmentId}`, appointmentData)
        await this.fetchAppointments() // Refresh appointments list
        return { success: true, data: response.data }
      } catch (error) {
        return { 
          success: false, 
          error: error.response?.data?.error || 'Failed to update appointment' 
        }
      }
    },

    async cancelAppointment(appointmentId) {
      try {
        const response = await api.delete(`/patient/appointments/${appointmentId}`)
        await this.fetchAppointments() // Refresh appointments list
        return { success: true, data: response.data }
      } catch (error) {
        return { 
          success: false, 
          error: error.response?.data?.error || 'Failed to cancel appointment' 
        }
      }
    },

    async fetchAppointmentDetail(appointmentId) {
      try {
        const response = await api.get(`/patient/appointments/${appointmentId}`)
        this.currentAppointment = response.data
        return { success: true, data: response.data }
      } catch (error) {
        return { 
          success: false, 
          error: error.response?.data?.error || 'Failed to fetch appointment details' 
        }
      }
    },

    async fetchMedicalHistory() {
      try {
        const response = await api.get('/patient/medical-history')
        this.medicalHistory = response.data.medical_history
        return { success: true, data: response.data }
      } catch (error) {
        return { 
          success: false, 
          error: error.response?.data?.error || 'Failed to fetch medical history' 
        }
      }
    },

    async fetchDepartments() {
      try {
        const response = await api.get('/patient/departments')
        this.departments = response.data.departments
        return { success: true, data: response.data }
      } catch (error) {
        return { 
          success: false, 
          error: error.response?.data?.error || 'Failed to fetch departments' 
        }
      }
    },

    async fetchProfile() {
      try {
        const response = await api.get('/patient/profile')
        return { success: true, data: response.data }
      } catch (error) {
        return { 
          success: false, 
          error: error.response?.data?.error || 'Failed to fetch profile' 
        }
      }
    },

    async updateProfile(profileData) {
      try {
        const response = await api.put('/patient/profile', profileData)
        return { success: true, data: response.data }
      } catch (error) {
        return { 
          success: false, 
          error: error.response?.data?.error || 'Failed to update profile' 
        }
      }
    }
  }
})