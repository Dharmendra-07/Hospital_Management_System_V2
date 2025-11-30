<template>
  <div class="patient-dashboard">
    <div class="container-fluid">
      <!-- Header -->
      <div class="row mb-4">
        <div class="col">
          <h1 class="h3 mb-0">Patient Dashboard</h1>
          <p class="text-muted" v-if="stats">
            Welcome, {{ stats.patient.name }}
          </p>
        </div>
      </div>

      <!-- Statistics Cards -->
      <div class="row mb-4" v-if="stats">
        <div class="col-xl-3 col-md-6 mb-4">
          <div class="card border-left-primary shadow h-100 py-2">
            <div class="card-body">
              <div class="row no-gutters align-items-center">
                <div class="col mr-2">
                  <div class="text-xs font-weight-bold text-primary text-uppercase mb-1">
                    Today's Appointments
                  </div>
                  <div class="h5 mb-0 font-weight-bold text-gray-800">
                    {{ stats.stats.today_appointments }}
                  </div>
                </div>
                <div class="col-auto">
                  <i class="fas fa-calendar-day fa-2x text-gray-300"></i>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="col-xl-3 col-md-6 mb-4">
          <div class="card border-left-success shadow h-100 py-2">
            <div class="card-body">
              <div class="row no-gutters align-items-center">
                <div class="col mr-2">
                  <div class="text-xs font-weight-bold text-success text-uppercase mb-1">
                    Upcoming Appointments
                  </div>
                  <div class="h5 mb-0 font-weight-bold text-gray-800">
                    {{ stats.stats.upcoming_appointments }}
                  </div>
                </div>
                <div class="col-auto">
                  <i class="fas fa-calendar-check fa-2x text-gray-300"></i>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="col-xl-3 col-md-6 mb-4">
          <div class="card border-left-info shadow h-100 py-2">
            <div class="card-body">
              <div class="row no-gutters align-items-center">
                <div class="col mr-2">
                  <div class="text-xs font-weight-bold text-info text-uppercase mb-1">
                    Total Appointments
                  </div>
                  <div class="h5 mb-0 font-weight-bold text-gray-800">
                    {{ stats.stats.total_appointments }}
                  </div>
                </div>
                <div class="col-auto">
                  <i class="fas fa-calendar-alt fa-2x text-gray-300"></i>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="col-xl-3 col-md-6 mb-4">
          <div class="card border-left-warning shadow h-100 py-2">
            <div class="card-body">
              <div class="row no-gutters align-items-center">
                <div class="col mr-2">
                  <div class="text-xs font-weight-bold text-warning text-uppercase mb-1">
                    Completed
                  </div>
                  <div class="h5 mb-0 font-weight-bold text-gray-800">
                    {{ stats.stats.completed_appointments }}
                  </div>
                </div>
                <div class="col-auto">
                  <i class="fas fa-check-circle fa-2x text-gray-300"></i>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="row mb-4">
        <div class="col-12">
          <div class="card">
            <div class="card-header">
              <h6 class="mb-0">Quick Actions</h6>
            </div>
            <div class="card-body">
              <div class="row">
                <div class="col-md-3 mb-3">
                  <button class="btn btn-primary w-100 h-100 py-3" @click="activeTab = 'doctors'">
                    <i class="fas fa-search fa-2x mb-2"></i><br>
                    Find Doctors
                  </button>
                </div>
                <div class="col-md-3 mb-3">
                  <button class="btn btn-success w-100 h-100 py-3" @click="activeTab = 'appointments'">
                    <i class="fas fa-calendar-plus fa-2x mb-2"></i><br>
                    Book Appointment
                  </button>
                </div>
                <div class="col-md-3 mb-3">
                  <button class="btn btn-info w-100 h-100 py-3" @click="activeTab = 'appointments'">
                    <i class="fas fa-list fa-2x mb-2"></i><br>
                    My Appointments
                  </button>
                </div>
                <div class="col-md-3 mb-3">
                  <button class="btn btn-warning w-100 h-100 py-3" @click="activeTab = 'medical-history'">
                    <i class="fas fa-file-medical fa-2x mb-2"></i><br>
                    Medical History
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Navigation Tabs -->
      <div class="row">
        <div class="col-12">
          <div class="card">
            <div class="card-header">
              <ul class="nav nav-tabs card-header-tabs">
                <li class="nav-item">
                  <a class="nav-link" :class="{ active: activeTab === 'doctors' }" 
                     @click="activeTab = 'doctors'">
                    <i class="fas fa-user-md me-2"></i>Find Doctors
                  </a>
                </li>
                <li class="nav-item">
                  <a class="nav-link" :class="{ active: activeTab === 'appointments' }" 
                     @click="activeTab = 'appointments'">
                    <i class="fas fa-calendar-alt me-2"></i>My Appointments
                  </a>
                </li>
                <li class="nav-item">
                  <a class="nav-link" :class="{ active: activeTab === 'medical-history' }" 
                     @click="activeTab = 'medical-history'">
                    <i class="fas fa-file-medical me-2"></i>Medical History
                  </a>
                </li>
                <li class="nav-item">
                  <a class="nav-link" :class="{ active: activeTab === 'profile' }" 
                     @click="activeTab = 'profile'">
                    <i class="fas fa-user me-2"></i>Profile
                  </a>
                </li>
              </ul>
            </div>
            <div class="card-body">
              <!-- Doctors Tab -->
              <div v-if="activeTab === 'doctors'">
                <PatientDoctors />
              </div>

              <!-- Appointments Tab -->
              <div v-if="activeTab === 'appointments'">
                <PatientAppointments />
              </div>

              <!-- Medical History Tab -->
              <div v-if="activeTab === 'medical-history'">
                <PatientMedicalHistory />
              </div>

              <!-- Profile Tab -->
              <div v-if="activeTab === 'profile'">
                <PatientProfile />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { usePatientStore } from '@/store/patient'
import PatientDoctors from '@/components/patient/PatientDoctors.vue'
import PatientAppointments from '@/components/patient/PatientAppointments.vue'
import PatientMedicalHistory from '@/components/patient/PatientMedicalHistory.vue'
import PatientProfile from '@/components/patient/PatientProfile.vue'

export default {
  name: 'PatientDashboard',
  components: {
    PatientDoctors,
    PatientAppointments,
    PatientMedicalHistory,
    PatientProfile
  },
  data() {
    return {
      activeTab: 'doctors',
      loading: false
    }
  },
  setup() {
    const patientStore = usePatientStore()
    return { patientStore }
  },
  computed: {
    stats() {
      return this.patientStore.stats
    }
  },
  async mounted() {
    this.loading = true
    await this.patientStore.fetchDashboardStats()
    await this.patientStore.fetchDepartments()
    this.loading = false
  }
}
</script>

<style scoped>
.patient-dashboard {
  padding: 20px;
  background-color: #f8f9fc;
  min-height: 100vh;
}

.card {
  border: none;
  border-radius: 0.5rem;
  box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15);
}

.border-left-primary {
  border-left: 0.25rem solid #4e73df !important;
}

.border-left-success {
  border-left: 0.25rem solid #1cc88a !important;
}

.border-left-info {
  border-left: 0.25rem solid #36b9cc !important;
}

.border-left-warning {
  border-left: 0.25rem solid #f6c23e !important;
}

.nav-tabs .nav-link {
  color: #6e707e;
  border: none;
  padding: 1rem 1.5rem;
}

.nav-tabs .nav-link.active {
  color: #4e73df;
  background: none;
  border-bottom: 2px solid #4e73df;
}

.nav-tabs .nav-link:hover {
  border: none;
  border-bottom: 2px solid #dddfeb;
}

.btn {
  transition: all 0.3s ease;
}

.btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}
</style>