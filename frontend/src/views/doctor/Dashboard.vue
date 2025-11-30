<template>
  <div class="doctor-dashboard">
    <div class="container-fluid">
      <!-- Header -->
      <div class="row mb-4">
        <div class="col">
          <h1 class="h3 mb-0">Doctor Dashboard</h1>
          <p class="text-muted" v-if="stats">
            Welcome, Dr. {{ stats.doctor.name }} - {{ stats.doctor.specialization }}
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
                    Upcoming (7 days)
                  </div>
                  <div class="h5 mb-0 font-weight-bold text-gray-800">
                    {{ stats.stats.upcoming_appointments }}
                  </div>
                </div>
                <div class="col-auto">
                  <i class="fas fa-calendar-week fa-2x text-gray-300"></i>
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
                    Total Patients
                  </div>
                  <div class="h5 mb-0 font-weight-bold text-gray-800">
                    {{ stats.stats.total_patients }}
                  </div>
                </div>
                <div class="col-auto">
                  <i class="fas fa-users fa-2x text-gray-300"></i>
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
                    Monthly Appointments
                  </div>
                  <div class="h5 mb-0 font-weight-bold text-gray-800">
                    {{ stats.stats.monthly_appointments }}
                  </div>
                </div>
                <div class="col-auto">
                  <i class="fas fa-calendar-alt fa-2x text-gray-300"></i>
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
                  <a class="nav-link" :class="{ active: activeTab === 'appointments' }" 
                     @click="activeTab = 'appointments'">
                    <i class="fas fa-calendar-alt me-2"></i>Appointments
                  </a>
                </li>
                <li class="nav-item">
                  <a class="nav-link" :class="{ active: activeTab === 'patients' }" 
                     @click="activeTab = 'patients'">
                    <i class="fas fa-users me-2"></i>Patients
                  </a>
                </li>
                <li class="nav-item">
                  <a class="nav-link" :class="{ active: activeTab === 'availability' }" 
                     @click="activeTab = 'availability'">
                    <i class="fas fa-clock me-2"></i>Availability
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
              <!-- Appointments Tab -->
              <div v-if="activeTab === 'appointments'">
                <DoctorAppointments />
              </div>

              <!-- Patients Tab -->
              <div v-if="activeTab === 'patients'">
                <DoctorPatients />
              </div>

              <!-- Availability Tab -->
              <div v-if="activeTab === 'availability'">
                <DoctorAvailability />
              </div>

              <!-- Profile Tab -->
              <div v-if="activeTab === 'profile'">
                <DoctorProfile />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useDoctorStore } from '@/store/doctor'
import DoctorAppointments from '@/components/doctor/DoctorAppointments.vue'
import DoctorPatients from '@/components/doctor/DoctorPatients.vue'
import DoctorAvailability from '@/components/doctor/DoctorAvailability.vue'
import DoctorProfile from '@/components/doctor/DoctorProfile.vue'

export default {
  name: 'DoctorDashboard',
  components: {
    DoctorAppointments,
    DoctorPatients,
    DoctorAvailability,
    DoctorProfile
  },
  data() {
    return {
      activeTab: 'appointments',
      loading: false
    }
  },
  setup() {
    const doctorStore = useDoctorStore()
    return { doctorStore }
  },
  computed: {
    stats() {
      return this.doctorStore.stats
    }
  },
  async mounted() {
    this.loading = true
    await this.doctorStore.fetchDashboardStats()
    this.loading = false
  }
}
</script>

<style scoped>
.doctor-dashboard {
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
</style>