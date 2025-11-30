<template>
  <div class="enhanced-appointment-booking">
    <!-- Conflict Check Modal -->
    <div class="modal fade" :class="{ show: showConflictModal, 'd-block': showConflictModal }" 
         v-if="showConflictModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Scheduling Conflict</h5>
            <button type="button" class="btn-close" @click="closeConflictModal"></button>
          </div>
          <div class="modal-body">
            <div class="alert alert-warning">
              <i class="fas fa-exclamation-triangle me-2"></i>
              {{ conflictMessage }}
            </div>
            
            <div v-if="suggestedSlots.length > 0" class="suggested-slots">
              <h6 class="mb-3">Suggested Alternative Slots:</h6>
              <div class="list-group">
                <button
                  v-for="slot in suggestedSlots"
                  :key="slot.date + slot.start_time"
                  class="list-group-item list-group-item-action"
                  @click="useSuggestedSlot(slot)"
                >
                  <div class="d-flex justify-content-between align-items-center">
                    <div>
                      <strong>{{ formatDate(slot.date) }}</strong><br>
                      <small>{{ slot.start_time }} - {{ slot.end_time }}</small>
                    </div>
                    <span class="badge bg-success">{{ slot.available_slots }} available</span>
                  </div>
                </button>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closeConflictModal">
              Cancel
            </button>
            <button v-if="suggestedSlots.length === 0" type="button" class="btn btn-primary" @click="closeConflictModal">
              OK
            </button>
          </div>
        </div>
      </div>
    </div>
    <div class="modal-backdrop fade show" v-if="showConflictModal"></div>

    <!-- Enhanced Booking Form -->
    <div class="card">
      <div class="card-header">
        <h5 class="mb-0">Book Appointment with Conflict Prevention</h5>
      </div>
      <div class="card-body">
        <form @submit.prevent="checkConflictsBeforeBooking">
          <div class="row">
            <div class="col-md-6">
              <div class="mb-3">
                <label class="form-label">Select Doctor</label>
                <select class="form-select" v-model="bookingForm.doctor_id" required>
                  <option value="">Choose a doctor...</option>
                  <option v-for="doctor in availableDoctors" :key="doctor.id" :value="doctor.id">
                    Dr. {{ doctor.name }} - {{ doctor.specialization }}
                  </option>
                </select>
              </div>
            </div>
            <div class="col-md-6">
              <div class="mb-3">
                <label class="form-label">Appointment Date</label>
                <input
                  type="date"
                  class="form-control"
                  v-model="bookingForm.appointment_date"
                  :min="minDate"
                  :max="maxDate"
                  required
                >
              </div>
            </div>
          </div>

          <div class="row">
            <div class="col-md-6">
              <div class="mb-3">
                <label class="form-label">Preferred Time</label>
                <select class="form-select" v-model="bookingForm.appointment_time" required>
                  <option value="">Select time...</option>
                  <option v-for="time in timeSlots" :key="time" :value="time">
                    {{ time }}
                  </option>
                </select>
              </div>
            </div>
            <div class="col-md-6">
              <div class="mb-3">
                <label class="form-label">Reason for Visit</label>
                <textarea
                  class="form-control"
                  v-model="bookingForm.reason"
                  rows="2"
                  placeholder="Briefly describe the reason for your visit..."
                  required
                ></textarea>
              </div>
            </div>
          </div>

          <!-- Real-time Availability Indicator -->
          <div v-if="availabilityChecked" class="mb-3">
            <div class="alert" :class="availabilityStatusClass">
              <i class="fas me-2" :class="availabilityIcon"></i>
              {{ availabilityMessage }}
            </div>
          </div>

          <div class="d-grid gap-2 d-md-flex justify-content-md-end">
            <button 
              type="button" 
              class="btn btn-outline-primary me-md-2"
              @click="checkAvailability"
              :disabled="!canCheckAvailability"
            >
              <i class="fas fa-search me-1"></i>Check Availability
            </button>
            <button 
              type="submit" 
              class="btn btn-primary"
              :disabled="!canBook"
            >
              <i class="fas fa-calendar-plus me-1"></i>Book Appointment
            </button>
          </div>
        </form>

        <!-- Available Time Slots -->
        <div v-if="availableSlots.length > 0" class="mt-4">
          <h6>Available Time Slots for Dr. {{ selectedDoctorName }}</h6>
          <div class="row">
            <div class="col-md-3 mb-2" v-for="slot in availableSlots" :key="slot.date + slot.start_time">
              <div class="card slot-card" :class="{ 'border-primary': isSelectedSlot(slot) }">
                <div class="card-body text-center p-2">
                  <small class="d-block">{{ formatDate(slot.date) }}</small>
                  <strong class="d-block">{{ slot.start_time }}</strong>
                  <small class="text-muted">{{ slot.available_slots }} slots left</small>
                  <button 
                    class="btn btn-sm btn-outline-primary mt-1"
                    @click="selectSlot(slot)"
                  >
                    Select
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Appointment History -->
    <div class="card mt-4">
      <div class="card-header">
        <h5 class="mb-0">Recent Appointment History</h5>
      </div>
      <div class="card-body">
        <div class="table-responsive">
          <table class="table table-sm">
            <thead>
              <tr>
                <th>Date</th>
                <th>Doctor</th>
                <th>Time</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="appointment in recentAppointments" :key="appointment.id">
                <td>{{ formatDate(appointment.appointment_date) }}</td>
                <td>Dr. {{ appointment.doctor_name }}</td>
                <td>{{ appointment.appointment_time }}</td>
                <td>
                  <span class="badge" :class="getStatusBadgeClass(appointment.status)">
                    {{ appointment.status }}
                  </span>
                </td>
                <td>
                  <button 
                    class="btn btn-sm btn-outline-info"
                    @click="viewAppointmentHistory(appointment.id)"
                  >
                    <i class="fas fa-history"></i> History
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Appointment History Modal -->
    <div class="modal fade" :class="{ show: showHistoryModal, 'd-block': showHistoryModal }" 
         v-if="showHistoryModal" tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Appointment History</h5>
            <button type="button" class="btn-close" @click="closeHistoryModal"></button>
          </div>
          <div class="modal-body">
            <div v-if="appointmentHistory.length > 0">
              <div class="timeline">
                <div v-for="history in appointmentHistory" :key="history.id" class="timeline-item">
                  <div class="timeline-marker"></div>
                  <div class="timeline-content">
                    <div class="d-flex justify-content-between">
                      <strong>{{ history.change_type.replace('_', ' ').toUpperCase() }}</strong>
                      <small class="text-muted">{{ formatDateTime(history.changed_at) }}</small>
                    </div>
                    <small class="text-muted">By: {{ history.changed_by }}</small>
                    
                    <div v-if="history.previous_data || history.new_data" class="mt-2">
                      <div v-if="history.previous_data" class="change-diff">
                        <small class="text-danger">
                          <strong>Before:</strong> {{ formatHistoryData(history.previous_data) }}
                        </small>
                      </div>
                      <div v-if="history.new_data" class="change-diff">
                        <small class="text-success">
                          <strong>After:</strong> {{ formatHistoryData(history.new_data) }}
                        </small>
                      </div>
                    </div>
                    
                    <div v-if="history.change_reason" class="mt-1">
                      <small class="text-muted">
                        <strong>Reason:</strong> {{ history.change_reason }}
                      </small>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="text-center text-muted py-4">
              No history available for this appointment
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="modal-backdrop fade show" v-if="showHistoryModal"></div>
  </div>
</template>

<script>
import { usePatientStore } from '@/store/patient'
import { ref, computed, watch } from 'vue'

export default {
  name: 'EnhancedAppointmentBooking',
  setup() {
    const patientStore = usePatientStore()
    
    const showConflictModal = ref(false)
    const showHistoryModal = ref(false)
    const conflictMessage = ref('')
    const suggestedSlots = ref([])
    const availabilityChecked = ref(false)
    const availableSlots = ref([])
    const appointmentHistory = ref([])
    
    const bookingForm = ref({
      doctor_id: '',
      appointment_date: '',
      appointment_time: '',
      reason: ''
    })

    const timeSlots = [
      '09:00', '09:30', '10:00', '10:30', '11:00', '11:30',
      '14:00', '14:30', '15:00', '15:30', '16:00', '16:30'
    ]

    // Computed properties
    const canCheckAvailability = computed(() => {
      return bookingForm.value.doctor_id && bookingForm.value.appointment_date
    })

    const canBook = computed(() => {
      return bookingForm.value.doctor_id && 
             bookingForm.value.appointment_date && 
             bookingForm.value.appointment_time && 
             bookingForm.value.reason
    })

    const availabilityStatusClass = computed(() => {
      return availabilityChecked.value ? 'alert-success' : 'alert-warning'
    })

    const availabilityIcon = computed(() => {
      return availabilityChecked.value ? 'fa-check-circle' : 'fa-clock'
    })

    const availabilityMessage = computed(() => {
      return availabilityChecked.value 
        ? 'Time slot is available for booking'
        : 'Check availability before booking'
    })

    const selectedDoctorName = computed(() => {
      const doctor = patientStore.doctors.find(d => d.id == bookingForm.value.doctor_id)
      return doctor ? doctor.name : ''
    })

    const recentAppointments = computed(() => {
      return patientStore.appointments.slice(0, 5) // Last 5 appointments
    })

    const minDate = new Date().toISOString().split('T')[0]
    const maxDate = new Date(Date.now() + 90 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]

    // Methods
    const checkAvailability = async () => {
      if (!canCheckAvailability.value) return

      const result = await patientStore.checkAppointmentConflicts({
        doctor_id: bookingForm.value.doctor_id,
        appointment_date: bookingForm.value.appointment_date,
        appointment_time: bookingForm.value.appointment_time
      })

      if (result.success) {
        availabilityChecked.value = true
        if (!result.data.available) {
          showConflictModal.value = true
          conflictMessage.value = result.data.message
          // In a real app, you would fetch suggested slots from the backend
          suggestAlternativeSlots()
        }
      } else {
        alert('Error checking availability: ' + result.error)
      }
    }

    const checkConflictsBeforeBooking = async () => {
      const conflictCheck = await patientStore.checkAppointmentConflicts(bookingForm.value)
      
      if (conflictCheck.success && conflictCheck.data.available) {
        // No conflicts, proceed with booking
        const bookingResult = await patientStore.bookAppointment(bookingForm.value)
        if (bookingResult.success) {
          alert('Appointment booked successfully!')
          resetForm()
        } else {
          alert('Error booking appointment: ' + bookingResult.error)
        }
      } else {
        showConflictModal.value = true
        conflictMessage.value = conflictCheck.data?.message || 'Scheduling conflict detected'
        suggestAlternativeSlots()
      }
    }

    const suggestAlternativeSlots = async () => {
      // Fetch alternative slots from backend
      const result = await patientStore.fetchBulkAvailability(
        [bookingForm.value.doctor_id],
        bookingForm.value.appointment_date,
        new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
      )
      
      if (result.success) {
        const doctorAvailability = result.data.availability[bookingForm.value.doctor_id]
        suggestedSlots.value = doctorAvailability?.available_slots || []
      }
    }

    const useSuggestedSlot = (slot) => {
      bookingForm.value.appointment_date = slot.date
      bookingForm.value.appointment_time = slot.start_time
      closeConflictModal()
      checkAvailability()
    }

    const viewAppointmentHistory = async (appointmentId) => {
      const result = await patientStore.fetchAppointmentHistory(appointmentId)
      if (result.success) {
        appointmentHistory.value = result.data.history
        showHistoryModal.value = true
      } else {
        alert('Error fetching appointment history: ' + result.error)
      }
    }

    const selectSlot = (slot) => {
      bookingForm.value.appointment_date = slot.date
      bookingForm.value.appointment_time = slot.start_time
      checkAvailability()
    }

    const isSelectedSlot = (slot) => {
      return bookingForm.value.appointment_date === slot.date && 
             bookingForm.value.appointment_time === slot.start_time
    }

    const closeConflictModal = () => {
      showConflictModal.value = false
      conflictMessage.value = ''
      suggestedSlots.value = []
    }

    const closeHistoryModal = () => {
      showHistoryModal.value = false
      appointmentHistory.value = []
    }

    const resetForm = () => {
      bookingForm.value = {
        doctor_id: '',
        appointment_date: '',
        appointment_time: '',
        reason: ''
      }
      availabilityChecked.value = false
      availableSlots.value = []
    }

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString('en-US', {
        weekday: 'short',
        month: 'short',
        day: 'numeric'
      })
    }

    const formatDateTime = (dateTimeString) => {
      return new Date(dateTimeString).toLocaleString('en-US')
    }

    const formatHistoryData = (data) => {
      if (typeof data === 'object') {
        return Object.entries(data).map(([key, value]) => 
          `${key}: ${value}`
        ).join(', ')
      }
      return data
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

    // Watch for date changes to fetch available slots
    watch(() => bookingForm.value.appointment_date, (newDate) => {
      if (newDate && bookingForm.value.doctor_id) {
        fetchAvailableSlots()
      }
    })

    watch(() => bookingForm.value.doctor_id, (newDoctorId) => {
      if (newDoctorId && bookingForm.value.appointment_date) {
        fetchAvailableSlots()
      }
    })

    const fetchAvailableSlots = async () => {
      if (!bookingForm.value.doctor_id || !bookingForm.value.appointment_date) return

      const result = await patientStore.fetchDoctorDetail(bookingForm.value.doctor_id)
      if (result.success) {
        availableSlots.value = result.data.availability.filter(slot => 
          slot.date === bookingForm.value.appointment_date
        )
      }
    }

    return {
      showConflictModal,
      showHistoryModal,
      conflictMessage,
      suggestedSlots,
      availabilityChecked,
      availableSlots,
      appointmentHistory,
      bookingForm,
      timeSlots,
      canCheckAvailability,
      canBook,
      availabilityStatusClass,
      availabilityIcon,
      availabilityMessage,
      selectedDoctorName,
      recentAppointments,
      minDate,
      maxDate,
      checkAvailability,
      checkConflictsBeforeBooking,
      useSuggestedSlot,
      viewAppointmentHistory,
      selectSlot,
      isSelectedSlot,
      closeConflictModal,
      closeHistoryModal,
      resetForm,
      formatDate,
      formatDateTime,
      formatHistoryData,
      getStatusBadgeClass
    }
  }
}
</script>

<style scoped>
.slot-card {
  cursor: pointer;
  transition: all 0.3s ease;
}

.slot-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.slot-card.border-primary {
  border-width: 2px;
}

.timeline {
  position: relative;
  padding-left: 20px;
}

.timeline-item {
  position: relative;
  padding-bottom: 20px;
  border-left: 2px solid #e9ecef;
}

.timeline-marker {
  position: absolute;
  left: -7px;
  top: 0;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #007bff;
}

.timeline-content {
  margin-left: 15px;
}

.change-diff {
  padding: 5px;
  background: #f8f9fa;
  border-radius: 4px;
  border-left: 3px solid #dee2e6;
}
</style>