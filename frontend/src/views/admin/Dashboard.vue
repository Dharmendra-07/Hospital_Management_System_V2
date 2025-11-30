<template>
  <div class="admin-dashboard">
    <div class="container-fluid">
      <!-- Header -->
      <div class="row mb-4">
        <div class="col">
          <h1 class="h3 mb-0">Admin Dashboard</h1>
          <p class="text-muted">Manage hospital operations and users</p>
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
          <div class="card border-left-success shadow h-100 py-2">
            <div class="card-body">
              <div class="row no-gutters align-items-center">
                <div class="col mr-2">
                  <div class="text-xs font-weight-bold text-success text-uppercase mb-1">
                    Total Doctors
                  </div>
                  <div class="h5 mb-0 font-weight-bold text-gray-800">
                    {{ stats.stats.total_doctors }}
                  </div>
                </div>
                <div class="col-auto">
                  <i class="fas fa-user-md fa-2x text-gray-300"></i>
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
          <div class="card border-left-warning shadow h-100 py-2">
            <div class="card-body">
              <div class="row no-gutters align-items-center">
                <div class="col mr-2">
                  <div class="text-xs font-weight-bold text-warning text-uppercase mb-1">
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
                    <i class="fas fa-user-md me-2"></i>Doctors
                  </a>
                </li>
                <li class="nav-item">
                  <a class="nav-link" :class="{ active: activeTab === 'patients' }" 
                     @click="activeTab = 'patients'">
                    <i class="fas fa-users me-2"></i>Patients
                  </a>
                </li>
                <li class="nav-item">
                  <a class="nav-link" :class="{ active: activeTab === 'appointments' }" 
                     @click="activeTab = 'appointments'">
                    <i class="fas fa-calendar-alt me-2"></i>Appointments
                  </a>
                </li>
                <li class="nav-item">
                  <a class="nav-link" :class="{ active: activeTab === 'departments' }" 
                     @click="activeTab = 'departments'">
                    <i class="fas fa-building me-2"></i>Departments
                  </a>
                </li>
              </ul>
            </div>
            <div class="card-body">
              <!-- Doctors Tab -->
              <div v-if="activeTab === 'doctors'">
                <DoctorsManagement />
              </div>

              <!-- Patients Tab -->
              <div v-if="activeTab === 'patients'">
                <PatientsManagement />
              </div>

              <!-- Appointments Tab -->
              <div v-if="activeTab === 'appointments'">
                <AppointmentsManagement />
              </div>

              <!-- Departments Tab -->
              <div v-if="activeTab === 'departments'">
                <DepartmentsManagement />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useAdminStore } from '@/store/admin'
import DoctorsManagement from '@/components/admin/DoctorsManagement.vue'
import PatientsManagement from '@/components/admin/PatientsManagement.vue'
import AppointmentsManagement from '@/components/admin/AppointmentsManagement.vue'
import DepartmentsManagement from '@/components/admin/DepartmentsManagement.vue'

export default {
  name: 'AdminDashboard',
  components: {
    DoctorsManagement,
    PatientsManagement,
    AppointmentsManagement,
    DepartmentsManagement
  },
  data() {
    return {
      activeTab: 'doctors',
      loading: false
    }
  },
  setup() {
    const adminStore = useAdminStore()
    return { adminStore }
  },
  computed: {
    stats() {
      return this.adminStore.stats
    }
  },
  async mounted() {
    this.loading = true
    await this.adminStore.fetchDashboardStats()
    await this.adminStore.fetchDepartments()
    this.loading = false
  }
}
</script>

<style scoped>
.admin-dashboard {
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