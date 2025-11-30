<template>
  <div class="doctor-appointments">
    <!-- Header with Filters -->
    <div class="row mb-4">
      <div class="col-md-4">
        <select class="form-select" v-model="statusFilter" @change="fetchAppointments">
          <option value="">All Status</option>
          <option value="scheduled">Scheduled</option>
          <option value="completed">Completed</option>
          <option value="cancelled">Cancelled</option>
          <option value="no_show">No Show</option>
        </select>
      </div>
      <div class="col-md-4">
        <input type="date" class="form-control" v-model="dateFilter" @change="fetchAppointments">
      </div>
      <div class="col-md-4">
        <button class="btn btn-outline-secondary w-100" @click="clearFilters">
          <i class="fas fa-times me-2"></i>Clear Filters
        </button>
      </div>
    </div>

    <!-- Appointments Table -->
    <div class="card">
      <div class="card-body">
        <div class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>Patient</th>
                <th>Date</th>
                <th>Time</th>
                <th>Reason</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="appointment in doctorStore.appointments" :key="appointment.id">
                <td>
                  <strong>{{ appointment.patient_name }}</strong><br>
                  <small class="text-muted">{{ appointment.patient_phone }}</small>
                </td>
                <td>{{ formatDate(appointment.appointment_date) }}</td>
                <td>{{ appointment.appointment_time }}</td>
                <td>{{ appointment.reason || 'Not specified' }}</td>
                <td>
                  <span class="badge" :class="getStatusBadgeClass(appointment.status)">
                    {{ appointment.status }}
                  </span>
                </td>
                <td>
                  <button 
                    class="btn btn-sm btn-outline-primary me-1"
                    @click="viewAppointment(appointment.id)"
                    title="View Details"
                  >
                    <i class="fas fa-eye"></i>
                  </button>
                  <button 
                    v-if="appointment.status === 'scheduled'"
                    class="btn btn-sm btn-outline-success me-1"
                    @click="updateStatus(appointment.id, 'completed')"
                    title="Mark Completed"
                  >
                    <i class="fas fa-check"></i>
                  </button>
                  <button 
                    v-if="appointment.status === 'scheduled'"
                    class="btn btn-sm btn-outline-warning me-1"
                    @click="updateStatus(appointment.id, 'cancelled')"
                    title="Cancel"
                  >
                    <i class="fas fa-times"></i>
                  </button>
                </td>
              </tr>
              <tr v-if="doctorStore.appointments.length === 0 && !doctorStore.loading">
                <td colspan="6" class="text-center text-muted py-4">
                  No appointments found
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Appointment Detail Modal -->
    <div class="modal fade" :class="{ show: showDetailModal, 'd-block': showDetailModal }" 
         v-if="showDetailModal" tabindex="-1">
      <div class="modal-dialog modal-xl">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Appointment Details</h5>
            <button type="button" class="btn-close" @click="closeDetailModal"></button>
          </div>
          <div class="modal-body" v-if="currentAppointment">
            <!-- Patient Information -->
            <div class="row mb-4">
              <div class="col-12">
                <h6 class="text-primary">Patient Information</h6>
                <div class="row">
                  <div class="col-md-6">
                    <p><strong>Name:</strong> {{ currentAppointment.appointment.patient_name }}</p>
                    <p><strong>Email:</strong> {{ currentAppointment.appointment.patient_email }}</p>
                    <p><strong>Phone:</strong> {{ currentAppointment.appointment.patient_phone }}</p>
                  </div>
                  <div class="col-md-6">
                    <p><strong>Date of Birth:</strong> {{ formatDate(currentAppointment.appointment.date_of_birth) }}</p>
                    <p><strong>Gender:</strong> {{ currentAppointment.appointment.gender }}</p>
                    <p><strong>Blood Group:</strong> {{ currentAppointment.appointment.blood_group || 'Not specified' }}</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Appointment Information -->
            <div class="row mb-4">
              <div class="col-12">
                <h6 class="text-primary">Appointment Information</h6>
                <div class="row">
                  <div class="col-md-6">
                    <p><strong>Date:</strong> {{ formatDate(currentAppointment.appointment.appointment_date) }}</p>
                    <p><strong>Time:</strong> {{ currentAppointment.appointment.appointment_time }}</p>
                  </div>
                  <div class="col-md-6">
                    <p><strong>Status:</strong> 
                      <span class="badge" :class="getStatusBadgeClass(currentAppointment.appointment.status)">
                        {{ currentAppointment.appointment.status }}
                      </span>
                    </p>
                    <p><strong>Reason:</strong> {{ currentAppointment.appointment.reason || 'Not specified' }}</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Treatment Form -->
            <div class="row mb-4" v-if="currentAppointment.appointment.status === 'completed'">
              <div class="col-12">
                <h6 class="text-primary">Treatment Details</h6>
                <form @submit.prevent="saveTreatment">
                  <div class="row">
                    <div class="col-md-6">
                      <div class="mb-3">
                        <label class="form-label">Symptoms</label>
                        <textarea
                          class="form-control"
                          v-model="treatmentForm.symptoms"
                          rows="3"
                          placeholder="Describe patient symptoms..."
                        ></textarea>
                      </div>
                    </div>
                    <div class="col-md-6">
                      <div class="mb-3">
                        <label class="form-label">Diagnosis</label>
                        <textarea
                          class="form-control"
                          v-model="treatmentForm.diagnosis"
                          rows="3"
                          placeholder="Enter diagnosis..."
                        ></textarea>
                      </div>
                    </div>
                  </div>

                  <div class="row">
                    <div class="col-12">
                      <div class="mb-3">
                        <label class="form-label">Prescription</label>
                        <textarea
                          class="form-control"
                          v-model="treatmentForm.prescription"
                          rows="4"
                          placeholder="Enter prescription details..."
                        ></textarea>
                      </div>
                    </div>
                  </div>

                  <div class="row">
                    <div class="col-md-6">
                      <div class="mb-3">
                        <label class="form-label">Notes</label>
                        <textarea
                          class="form-control"
                          v-model="treatmentForm.notes"
                          rows="3"
                          placeholder="Additional notes..."
                        ></textarea>
                      </div>
                    </div>
                    <div class="col-md-6">
                      <div class="mb-3">
                        <label class="form-label">Follow-up Date</label>
                        <input
                          type="date"
                          class="form-control"
                          v-model="treatmentForm.follow_up_date"
                        >
                      </div>
                    </div>
                  </div>

                  <div class="text-end">
                    <button type="submit" class="btn btn-primary" :disabled="savingTreatment">
                      <span v-if="savingTreatment" class="spinner-border spinner-border-sm me-2"></span>
                      {{ savingTreatment ? 'Saving...' : 'Save Treatment Details' }}
                    </button>
                  </div>
                </form>
              </div>
            </div>

            <!-- Patient History -->
            <div class="row" v-if="currentAppointment.patient_history.length > 0">
              <div class="col-12">
                <h6 class="text-primary">Patient History</h6>
                <div class="table-responsive">
                  <table class="table table-sm">
                    <thead>
                      <tr>
                        <th>Date</th>
                        <th>Reason</th>
                        <th>Diagnosis</th>
                        <th>Prescription</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="history in currentAppointment.patient_history" :key="history.appointment_date">
                        <td>{{ formatDate(history.appointment_date) }}</td>
                        <td>{{ history.reason || 'Not specified' }}</td>
                        <td>{{ history.treatment?.diagnosis || 'Not recorded' }}</td>
                        <td>{{ history.treatment?.prescription || 'Not recorded' }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="modal-backdrop fade show" v-if="showDetailModal"></div>
  </div>
</template>

<script>
import { useDoctorStore } from '@/store/doctor'
import { ref, reactive, onMounted } from 'vue'

export default {
  name: 'DoctorAppointments',
  setup() {
    const doctorStore = useDoctorStore()
    const showDetailModal = ref(false)
    const statusFilter = ref('')
    const dateFilter = ref('')
    const savingTreatment = ref(false)

    const treatmentForm = reactive({
      symptoms: '',
      diagnosis: '',
      prescription: '',
      notes: '',
      follow_up_date: ''
    })

    onMounted(() => {
      fetchAppointments()
    })

    const fetchAppointments = () => {
      doctorStore.fetchAppointments(statusFilter.value, dateFilter.value)
    }

    const clearFilters = () => {
      statusFilter.value = ''
      dateFilter.value = ''
      fetchAppointments()
    }

    const viewAppointment = async (appointmentId) => {
      const result = await doctorStore.fetchAppointmentDetail(appointmentId)
      if (result.success) {
        // Populate treatment form if treatment exists
        if (result.data.current_treatment) {
          Object.assign(treatmentForm, result.data.current_treatment)
          if (treatmentForm.follow_up_date) {
            treatmentForm.follow_up_date = treatmentForm.follow_up_date.split('T')[0]
          }
        }
        showDetailModal.value = true
      } else {
        alert('Error: ' + result.error)
      }
    }

    const updateStatus = async (appointmentId, status) => {
      if (confirm(`Are you sure you want to mark this appointment as ${status}?`)) {
        const result = await doctorStore.updateAppointmentStatus(appointmentId, status)
        if (result.success) {
          alert('Appointment status updated successfully')
        } else {
          alert('Error: ' + result.error)
        }
      }
    }

    const saveTreatment = async () => {
      savingTreatment.value = true
      const result = await doctorStore.addTreatment(
        doctorStore.currentAppointment.appointment.id,
        treatmentForm
      )
      
      if (result.success) {
        alert('Treatment details saved successfully')
        closeDetailModal()
      } else {
        alert('Error: ' + result.error)
      }
      savingTreatment.value = false
    }

    const closeDetailModal = () => {
      showDetailModal.value = false
      // Reset treatment form
      Object.keys(treatmentForm).forEach(key => {
        treatmentForm[key] = ''
      })
    }

    const formatDate = (dateString) => {
      if (!dateString) return 'N/A'
      return new Date(dateString).toLocaleDateString()
    }

    const getStatusBadgeClass = (status) => {
      const classes = {
        scheduled: 'bg-primary',
        completed: 'bg-success',
        cancelled: 'bg-danger',
        no_show: 'bg-warning'
      }
      return classes[status] || 'bg-secondary'
    }

    return {
      doctorStore,
      showDetailModal,
      statusFilter,
      dateFilter,
      savingTreatment,
      treatmentForm,
      currentAppointment: () => doctorStore.currentAppointment,
      fetchAppointments,
      clearFilters,
      viewAppointment,
      updateStatus,
      saveTreatment,
      closeDetailModal,
      formatDate,
      getStatusBadgeClass
    }
  }
}
</script>