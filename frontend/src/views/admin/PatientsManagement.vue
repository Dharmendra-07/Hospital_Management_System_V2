<template>
  <div class="patients-management">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h5 class="mb-0">Patients Management</h5>
    </div>

    <!-- Search -->
    <div class="row mb-3">
      <div class="col-md-6">
        <div class="input-group">
          <input
            type="text"
            class="form-control"
            placeholder="Search patients..."
            v-model="searchQuery"
            @input="handleSearch"
          >
          <span class="input-group-text">
            <i class="fas fa-search"></i>
          </span>
        </div>
      </div>
    </div>

    <!-- Patients Table -->
    <div class="card">
      <div class="card-body">
        <div class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>Username</th>
                <th>Email</th>
                <th>Name</th>
                <th>Phone</th>
                <th>Gender</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="patient in adminStore.patients" :key="patient.id">
                <td>{{ patient.username }}</td>
                <td>{{ patient.email }}</td>
                <td>{{ patient.first_name }} {{ patient.last_name }}</td>
                <td>{{ patient.phone || 'N/A' }}</td>
                <td>{{ patient.gender }}</td>
                <td>
                  <span class="badge" :class="patient.is_active ? 'bg-success' : 'bg-danger'">
                    {{ patient.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </td>
                <td>
                  <button 
                    class="btn btn-sm btn-outline-primary"
                    @click="editPatient(patient)"
                    title="Edit"
                  >
                    <i class="fas fa-edit"></i>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Edit Patient Modal (similar to doctor modal) -->
    <!-- Implementation similar to DoctorsManagement -->
  </div>
</template>

<script>
import { useAdminStore } from '@/store/admin'
import { ref, watch } from 'vue'

export default {
  name: 'PatientsManagement',
  setup() {
    const adminStore = useAdminStore()
    const searchQuery = ref('')

    // Load patients on component mount
    adminStore.fetchPatients()

    const handleSearch = () => {
      adminStore.fetchPatients(searchQuery.value)
    }

    // Debounce search
    let searchTimeout
    watch(searchQuery, () => {
      clearTimeout(searchTimeout)
      searchTimeout = setTimeout(handleSearch, 500)
    })

    return {
      adminStore,
      searchQuery,
      handleSearch
    }
  }
}
</script>