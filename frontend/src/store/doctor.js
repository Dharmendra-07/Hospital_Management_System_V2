import { defineStore } from 'pinia'
import { api } from '@/services/api'

export const useDoctorStore = defineStore('doctor', {
  state: () => ({
    stats: null,
    appointments: [],
    patients: [],
    availability: [],
    currentAppointment: null,
    currentPatient: null,
    loading: false
  }),

  actions: {
    async fetchDashboardStats() {
      try {
        const response = await api.get('/doctor/dashboard/stats')
        this.stats = response.data
        return { success: true, data: response.data }
      } catch (error) {
        return { 
          success: false, 
          error: error.response?.data?.error || 'Failed to fetch dashboard stats' 
        }
      }
    },

    async fetchAppointments(status = '', date = '') {
      try {
        this.loading = true
        const params = {}
        if (status) params.status = status
        if (date) params.date = date

        const response = await api.get('/doctor/appointments', { params })
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

    async fetchAppointmentDetail(appointmentId) {
      try {
        const response = await api.get(`/doctor/appointments/${appointmentId}`)
        this.currentAppointment = response.data
        return { success: true, data: response.data }
      } catch (error) {
        return { 
          success: false, 
          error: error.response?.data?.error || 'Failed to fetch appointment details' 
        }
      }
    },

    async updateAppointmentStatus(appointmentId, status) {
      try {
        const response = await api.put(`/doctor/appointments/${appointmentId}/status`, { status })
        await this.fetchAppointments() // Refresh list
        return { success: true, data: response.data }
      } catch (error) {
        return { 
          success: false, 
          error: error.response?.data?.error || 'Failed to update appointment status' 
        }
      }
    },

    async addTreatment(appointmentId, treatmentData) {
      try {
        const response = await api.post(`/doctor/appointments/${appointmentId}/treatment`, treatmentData)
        return { success: true, data: response.data }
      } catch (error) {
        return { 
          success: false, 
          error: error.response?.data?.error || 'Failed to save treatment details' 
        }
      }
    },

    async fetchPatients(search = '') {
      try {
        this.loading = true
        const params = {}
        if (search) params.search = search

        const response = await api.get('/doctor/patients', { params })
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

    async fetchPatientHistory(patientId) {
      try {
        const response = await api.get(`/doctor/patients/${patientId}/history`)
        this.currentPatient = response.data
        return { success: true, data: response.data }
      } catch (error) {
        return { 
          success: false, 
          error: error.response?.data?.error || 'Failed to fetch patient history' 
        }
      }
    },

    async fetchAvailability(startDate = null, endDate = null) {
      try {
        const params = {}
        if (startDate) params.start_date = startDate
        if (endDate) params.end_date = endDate

        const response = await api.get('/doctor/availability', { params })
        this.availability = response.data.availability
        return { success: true, data: response.data }
      } catch (error) {
        return { 
          success: false, 
          error: error.response?.data?.error || 'Failed to fetch availability' 
        }
      }
    },

    async setAvailability(availabilityData) {
      try {
        const response = await api.post('/doctor/availability', availabilityData)
        await this.fetchAvailability() // Refresh list
        return { success: true, data: response.data }
      } catch (error) {
        return { 
          success: false, 
          error: error.response?.data?.error || 'Failed to set availability' 
        }
      }
    },

    async deleteAvailability(slotId) {
      try {
        const response = await api.delete(`/doctor/availability/${slotId}`)
        await this.fetchAvailability() // Refresh list
        return { success: true, data: response.data }
      } catch (error) {
        return { 
          success: false, 
          error: error.response?.data?.error || 'Failed to delete availability slot' 
        }
      }
    },

    async fetchProfile() {
      try {
        const response = await api.get('/doctor/profile')
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
        const response = await api.put('/doctor/profile', profileData)
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