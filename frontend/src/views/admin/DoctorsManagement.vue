<template>
  <div class="doctors-management">
    <!-- Header with Add Button -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h5 class="mb-0">Doctors Management</h5>
      <button class="btn btn-primary" @click="showAddModal = true">
        <i class="fas fa-plus me-2"></i>Add Doctor
      </button>
    </div>

    <!-- Search and Filter -->
    <div class="row mb-3">
      <div class="col-md-6">
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
      <div class="col-md-6">
        <select class="form-select" v-model="selectedDepartment" @change="handleSearch">
          <option value="">All Departments</option>
          <option v-for="dept in adminStore.departments" :key="dept.id" :value="dept.id">
            {{ dept.name }}
          </option>
        </select>
      </div>
    </div>

    <!-- Doctors Table -->
    <div class="card">
      <div class="card-body">
        <div class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>Username</th>
                <th>Email</th>
                <th>Specialization</th>
                <th>Department</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="doctor in adminStore.doctors" :key="doctor.id">
                <td>{{ doctor.username }}</td>
                <td>{{ doctor.email }}</td>
                <td>{{ doctor.specialization }}</td>
                <td>{{ doctor.department }}</td>
                <td>
                  <span class="badge" :class="doctor.is_available ? 'bg-success' : 'bg-danger'">
                    {{ doctor.is_available ? 'Available' : 'Unavailable' }}
                  </span>
                </td>
                <td>
                  <button 
                    class="btn btn-sm btn-outline-primary me-1"
                    @click="editDoctor(doctor)"
                    title="Edit"
                  >
                    <i class="fas fa-edit"></i>
                  </button>
                  <button 
                    class="btn btn-sm btn-outline-danger"
                    @click="deleteDoctor(doctor.id)"
                    title="Delete"
                  >
                    <i class="fas fa-trash"></i>
                  </button>
                </td>
              </tr>
              <tr v-if="adminStore.doctors.length === 0 && !adminStore.loading">
                <td colspan="6" class="text-center text-muted py-4">
                  No doctors found
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Add/Edit Doctor Modal -->
    <div class="modal fade" :class="{ show: showAddModal, 'd-block': showAddModal }" 
         v-if="showAddModal" tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              {{ editingDoctor ? 'Edit Doctor' : 'Add New Doctor' }}
            </h5>
            <button type="button" class="btn-close" @click="closeModal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveDoctor">
              <div class="row">
                <div class="col-md-6">
                  <div class="mb-3">
                    <label class="form-label">Username *</label>
                    <input
                      type="text"
                      class="form-control"
                      v-model="doctorForm.username"
                      required
                    >
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="mb-3">
                    <label class="form-label">Email *</label>
                    <input
                      type="email"
                      class="form-control"
                      v-model="doctorForm.email"
                      required
                    >
                  </div>
                </div>
              </div>

              <div class="row">
                <div class="col-md-6">
                  <div class="mb-3">
                    <label class="form-label">Password {{ editingDoctor ? '' : '*' }}</label>
                    <input
                      type="password"
                      class="form-control"
                      v-model="doctorForm.password"
                      :required="!editingDoctor"
                    >
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="mb-3">
                    <label class="form-label">Specialization *</label>
                    <input
                      type="text"
                      class="form-control"
                      v-model="doctorForm.specialization"
                      required
                    >
                  </div>
                </div>
              </div>

              <div class="row">
                <div class="col-md-6">
                  <div class="mb-3">
                    <label class="form-label">Department *</label>
                    <select class="form-select" v-model="doctorForm.department_id" required>
                      <option value="">Select Department</option>
                      <option v-for="dept in adminStore.departments" 
                              :key="dept.id" 
                              :value="dept.id">
                        {{ dept.name }}
                      </option>
                    </select>
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="mb-3">
                    <label class="form-label">Consultation Fee</label>
                    <input
                      type="number"
                      class="form-control"
                      v-model="doctorForm.consultation_fee"
                      step="0.01"
                    >
                  </div>
                </div>
              </div>

              <div class="row">
                <div class="col-md-6">
                  <div class="mb-3">
                    <label class="form-label">Qualification</label>
                    <input
                      type="text"
                      class="form-control"
                      v-model="doctorForm.qualification"
                    >
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="mb-3">
                    <label class="form-label">Experience (years)</label>
                    <input
                      type="number"
                      class="form-control"
                      v-model="doctorForm.experience"
                    >
                  </div>
                </div>
              </div>

              <div class="mb-3">
                <label class="form-label">Bio</label>
                <textarea
                  class="form-control"
                  v-model="doctorForm.bio"
                  rows="3"
                ></textarea>
              </div>

              <div class="mb-3 form-check">
                <input
                  type="checkbox"
                  class="form-check-input"
                  v-model="doctorForm.is_available"
                >
                <label class="form-check-label">Available for appointments</label>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closeModal">
              Cancel
            </button>
            <button type="button" class="btn btn-primary" @click="saveDoctor" :disabled="saving">
              <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
              {{ saving ? 'Saving...' : 'Save' }}
            </button>
          </div>
        </div>
      </div>
    </div>
    <div class="modal-backdrop fade show" v-if="showAddModal"></div>
  </div>
</template>

<script>
import { useAdminStore } from '@/store/admin'
import { ref, reactive, watch } from 'vue'

export default {
  name: 'DoctorsManagement',
  setup() {
    const adminStore = useAdminStore()
    const showAddModal = ref(false)
    const editingDoctor = ref(null)
    const saving = ref(false)
    const searchQuery = ref('')
    const selectedDepartment = ref('')

    const doctorForm = reactive({
      username: '',
      email: '',
      password: '',
      specialization: '',
      department_id: '',
      qualification: '',
      experience: 0,
      consultation_fee: 0,
      bio: '',
      is_available: true
    })

    // Load doctors on component mount
    adminStore.fetchDoctors()

    const handleSearch = () => {
      adminStore.fetchDoctors(searchQuery.value, selectedDepartment.value || null)
    }

    const editDoctor = (doctor) => {
      editingDoctor.value = doctor
      Object.assign(doctorForm, {
        username: doctor.username,
        email: doctor.email,
        password: '',
        specialization: doctor.specialization,
        department_id: adminStore.departments.find(d => d.name === doctor.department)?.id || '',
        qualification: doctor.qualification || '',
        experience: doctor.experience || 0,
        consultation_fee: doctor.consultation_fee || 0,
        bio: doctor.bio || '',
        is_available: doctor.is_available
      })
      showAddModal.value = true
    }

    const deleteDoctor = async (doctorId) => {
      if (confirm('Are you sure you want to delete this doctor?')) {
        const result = await adminStore.deleteDoctor(doctorId)
        if (result.success) {
          alert('Doctor deleted successfully')
        } else {
          alert('Error: ' + result.error)
        }
      }
    }

    const saveDoctor = async () => {
      saving.value = true
      
      try {
        let result
        if (editingDoctor.value) {
          result = await adminStore.updateDoctor(editingDoctor.value.id, doctorForm)
        } else {
          result = await adminStore.addDoctor(doctorForm)
        }

        if (result.success) {
          closeModal()
          alert(editingDoctor.value ? 'Doctor updated successfully' : 'Doctor added successfully')
        } else {
          alert('Error: ' + result.error)
        }
      } finally {
        saving.value = false
      }
    }

    const closeModal = () => {
      showAddModal.value = false
      editingDoctor.value = null
      // Reset form
      Object.keys(doctorForm).forEach(key => {
        if (key !== 'is_available') {
          doctorForm[key] = ''
        } else {
          doctorForm[key] = true
        }
      })
    }

    // Debounce search
    let searchTimeout
    watch(searchQuery, () => {
      clearTimeout(searchTimeout)
      searchTimeout = setTimeout(handleSearch, 500)
    })

    watch(selectedDepartment, handleSearch)

    return {
      adminStore,
      showAddModal,
      editingDoctor,
      saving,
      searchQuery,
      selectedDepartment,
      doctorForm,
      editDoctor,
      deleteDoctor,
      saveDoctor,
      closeModal,
      handleSearch
    }
  }
}
</script>