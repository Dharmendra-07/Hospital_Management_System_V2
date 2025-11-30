<template>
  <div class="patient-doctors">
    <!-- Search and Filter Section -->
    <div class="row mb-4">
      <div class="col-md-4">
        <div class="input-group">
          <input
            type="text"
            class="form-control"
            placeholder="Search doctors..."
            v-model="searchQuery"
            @input="handleSearch"
          >
          <span class="input-group-text">
            <i class="fas fa-search"></i>
          </span>
        </div>
      </div>
      <div class="col-md-4">
        <select class="form-select" v-model="selectedDepartment" @change="handleSearch">
          <option value="">All Departments</option>
          <option v-for="dept in patientStore.departments" :key="dept.id" :value="dept.id">
            {{ dept.name }} ({{ dept.doctor_count }})
          </option>
        </select>
      </div>
      <div class="col-md-4">
        <input
          type="text"
          class="form-control"
          placeholder="Specialization..."
          v-model="specializationFilter"
          @input="handleSearch"
        >
      </div>
    </div>

    <!-- Doctors Grid -->
    <div class="row" v-if="!patientStore.loading">
      <div class="col-lg-4 col-md-6 mb-4" v-for="doctor in patientStore.doctors" :key="doctor.id">
        <div class="card doctor-card h-100">
          <div class="card-body">
            <div class="text-center mb-3">
              <div class="doctor-avatar bg-primary text-white rounded-circle d-inline-flex align-items-center justify-content-center">
                <i class="fas fa-user-md fa-2x"></i>
              </div>
            </div>
            
            <h5 class="card-title text-center">Dr. {{ doctor.name }}</h5>
            <p class="text-muted text-center mb-2">{{ doctor.specialization }}</p>
            <p class="text-center mb-3">
              <span class="badge bg-info">{{ doctor.department }}</span>
            </p>

            <div class="doctor-info">
              <p class="mb-2">
                <i class="fas fa-graduation-cap me-2 text-primary"></i>
                {{ doctor.qualification || 'Medical Degree' }}
              </p>
              <p class="mb-2">
                <i class="fas fa-briefcase me-2 text-primary"></i>
                {{ doctor.experience || 0 }} years experience
              </p>
              <p class="mb-2">
                <i class="fas fa-star me-2 text-warning"></i>
                Rating: {{ doctor.rating }}/5.0
              </p>
              <p class="mb-3">
                <i class="fas fa-money-bill-wave me-2 text-success"></i>
                Fee: ${{ doctor.consultation_fee }}
              </p>
            </div>

            <div class="availability mb-3">
              <small class="text-muted">
                <i class="fas fa-calendar-check me-1"></i>
                Next available: 
                <span v-if="doctor.next_available" class="text-success">
                  {{ formatDate(doctor.next_available) }}
                </span>
                <span v-else class="text-danger">
                  Not available
                </span>
              </small>
            </div>

            <div class="text-center">
              <button 
                class="btn btn-primary btn-sm me-2"
                @click="viewDoctor(doctor.id)"
              >
                <i class="fas fa-eye me-1"></i>View
              </button>
              <button 
                class="btn btn-success btn-sm"
                @click="bookAppointment(doctor)"
                :disabled="!doctor.next_available"
              >
                <i class="fas fa-calendar-plus me-1"></i>Book
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="patientStore.loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2">Loading doctors...</p>
    </div>

    <!-- No Results -->
    <div v-if="patientStore.doctors.length === 0 && !patientStore.loading" class="text-center py-5">
      <i class="fas fa-user-md fa-3x text-muted mb-3"></i>
      <h5 class="text-muted">No doctors found</h5>
      <p class="text-muted">Try adjusting your search criteria</p>
    </div>

    <!-- Doctor Detail Modal -->
    <div class="modal fade" :class="{ show: showDoctorModal, 'd-block': showDoctorModal }" 
         v-if="showDoctorModal" tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Doctor Details</h5>
            <button type="button" class="btn-close" @click="closeDoctorModal"></button>
          </div>
          <div class="modal-body" v-if="currentDoctor">
            <div class="row">
              <div class="col-md-4 text-center">
                <div class="doctor-avatar-large bg-primary text-white rounded-circle d-inline-flex align-items-center justify-content-center mb-3">
                  <i class="fas fa-user-md fa-3x"></i>
                </div>
                <h4>Dr. {{ currentDoctor.doctor.name }}</h4>
                <p class="text-muted">{{ currentDoctor.doctor.specialization }}</p>
                <p class="badge bg-info fs-6">{{ currentDoctor.doctor.department }}</p>
              </div>
              <div class="col-md-8">
                <div class="row mb-3">
                  <div class="col-6">
                    <strong>Qualification:</strong><br>
                    {{ currentDoctor.doctor.qualification || 'Medical Degree' }}
                  </div>
                  <div class="col-6">
                    <strong>Experience:</strong><br>
                    {{ currentDoctor.doctor.experience || 0 }} years
                  </div>
                </div>
                <div class="row mb-3">
                  <div class="col-6">
                    <strong>Consultation Fee:</strong><br>
                    ${{ currentDoctor.doctor.consultation_fee }}
                  </div>
                  <div class="col-6">
                    <strong>Email:</strong><br>
                    {{ currentDoctor.doctor.email }}
                  </div>
                </div>
                <div class="mb-3" v-if="currentDoctor.doctor.bio">
                  <strong>Bio:</strong><br>
                  {{ currentDoctor.doctor.bio }}
                </div>

                <!-- Availability Calendar -->
                <div class="availability-calendar">
                  <h6 class="mb-3">Available Time Slots (Next 7 Days)</h6>
                  <div class="table-responsive">
                    <table class="table table-sm table-bordered">
                      <thead>
                        <tr>
                          <th>Date</th>
                          <th>Time Slot</th>
                          <th>Available</th>
                          <th>Action</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="slot in currentDoctor.availability" :key="slot.date + slot.start_time">
                          <td>{{ formatDate(slot.date) }}</td>
                          <td>{{ slot.start_time }} - {{ slot.end_time }}</td>
                          <td>
                            <span class="badge" :class="slot.available_slots > 0 ? 'bg-success' : 'bg-danger'">
                              {{ slot.available_slots }} slots
                            </span>
                          </td>
                          <td>
                            <button 
                              class="btn btn-success btn-sm"
                              @click="bookSlot(currentDoctor.doctor, slot)"
                              :disabled="slot.available_slots === 0"
                            >
                              Book
                            </button>
                          </td>
                        </tr>
                        <tr v-if="currentDoctor.availability.length === 0">
                          <td colspan="4" class="text-center text-muted">
                            No available slots in the next 7 days
                          </td>
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
    </div>
    <div class="modal-backdrop fade show" v-if="showDoctorModal"></div>

    <!-- Book Appointment Modal -->
    <div class="modal fade" :class="{ show: showBookModal, 'd-block': showBookModal }" 
         v-if="showBookModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Book Appointment</h5>
            <button type="button" class="btn-close" @click="closeBookModal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="confirmBooking">
              <div class="mb-3">
                <label class="form-label">Doctor</label>
                <input type="text" class="form-control" :value="`Dr. ${selectedDoctor.name}`" disabled>
              </div>
              <div class="mb-3">
                <label class="form-label">Date</label>
                <input type="text" class="form-control" :value="formatDate(selectedSlot.date)" disabled>
              </div>
              <div class="mb-3">
                <label class="form-label">Time</label>
                <input type="text" class="form-control" :value="selectedSlot.start_time" disabled>
              </div>
              <div class="mb-3">
                <label class="form-label">Reason for Visit *</label>
                <textarea
                  class="form-control"
                  v-model="bookingForm.reason"
                  rows="3"
                  placeholder="Please describe the reason for your visit..."
                  required
                ></textarea>
              </div>
              <div class="alert alert-info">
                <small>
                  <i class="fas fa-info-circle me-1"></i>
                  Consultation fee: ${{ selectedDoctor.consultation_fee }}<br>
                  You can cancel or reschedule up to 2 hours before the appointment.
                </small>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closeBookModal">Cancel</button>
            <button type="button" class="btn btn-primary" @click="confirmBooking" :disabled="booking">
              <span v-if="booking" class="spinner-border spinner-border-sm me-2"></span>
              {{ booking ? 'Booking...' : 'Confirm Booking' }}
            </button>
          </div>
        </div>
      </div>
    </div>
    <div class="modal-backdrop fade show" v-if="showBookModal"></div>
  </div>
</template>

<script>
import { usePatientStore } from '@/store/patient'
import { ref, watch } from 'vue'

export default {
  name: 'PatientDoctors',
  setup() {
    const patientStore = usePatientStore()
    const searchQuery = ref('')
    const selectedDepartment = ref('')
    const specializationFilter = ref('')
    const showDoctorModal = ref(false)
    const showBookModal = ref(false)
    const selectedDoctor = ref(null)
    const selectedSlot = ref(null)
    const booking = ref(false)

    const bookingForm = ref({
      reason: ''
    })

    // Load doctors on component mount
    patientStore.fetchDoctors()

    const handleSearch = () => {
      patientStore.fetchDoctors(
        searchQuery.value,
        specializationFilter.value,
        selectedDepartment.value || null
      )
    }

    const viewDoctor = async (doctorId) => {
      const result = await patientStore.fetchDoctorDetail(doctorId)
      if (result.success) {
        showDoctorModal.value = true
      } else {
        alert('Error: ' + result.error)
      }
    }

    const bookAppointment = (doctor) => {
      selectedDoctor.value = doctor
      showBookModal.value = true
    }

    const bookSlot = (doctor, slot) => {
      selectedDoctor.value = doctor
      selectedSlot.value = slot
      showBookModal.value = true
    }

    const confirmBooking = async () => {
      if (!bookingForm.value.reason.trim()) {
        alert('Please provide a reason for your visit')
        return
      }

      booking.value = true
      
      const appointmentData = {
        doctor_id: selectedDoctor.value.id,
        appointment_date: selectedSlot.value ? selectedSlot.value.date : new Date().toISOString().split('T')[0],
        appointment_time: selectedSlot.value ? selectedSlot.value.start_time : '09:00',
        reason: bookingForm.value.reason
      }

      const result = await patientStore.bookAppointment(appointmentData)
      
      if (result.success) {
        alert('Appointment booked successfully!')
        closeBookModal()
      } else {
        alert('Error: ' + result.error)
      }
      
      booking.value = false
    }

    const closeDoctorModal = () => {
      showDoctorModal.value = false
      selectedDoctor.value = null
    }

    const closeBookModal = () => {
      showBookModal.value = false
      selectedDoctor.value = null
      selectedSlot.value = null
      bookingForm.value.reason = ''
    }

    const formatDate = (dateString) => {
      if (!dateString) return 'N/A'
      return new Date(dateString).toLocaleDateString('en-US', {
        weekday: 'short',
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    }

    // Debounce search
    let searchTimeout
    watch([searchQuery, specializationFilter], () => {
      clearTimeout(searchTimeout)
      searchTimeout = setTimeout(handleSearch, 500)
    })

    watch(selectedDepartment, handleSearch)

    return {
      patientStore,
      searchQuery,
      selectedDepartment,
      specializationFilter,
      showDoctorModal,
      showBookModal,
      selectedDoctor: () => patientStore.currentDoctor,
      selectedSlot,
      booking,
      bookingForm,
      handleSearch,
      viewDoctor,
      bookAppointment,
      bookSlot,
      confirmBooking,
      closeDoctorModal,
      closeBookModal,
      formatDate
    }
  }
}
</script>

<style scoped>
.doctor-card {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  border: none;
  border-radius: 15px;
}

.doctor-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}

.doctor-avatar {
  width: 80px;
  height: 80px;
}

.doctor-avatar-large {
  width: 120px;
  height: 120px;
}

.availability-calendar {
  max-height: 400px;
  overflow-y: auto;
}

.table th {
  background-color: #f8f9fa;
  border-bottom: 2px solid #dee2e6;
}
</style>