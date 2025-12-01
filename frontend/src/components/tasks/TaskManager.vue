<template>
  <div class="task-manager">
    <div class="row">
      <!-- Patient Export Section -->
      <div class="col-md-6" v-if="isPatient">
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">Export Medical History</h5>
          </div>
          <div class="card-body">
            <p>Export your complete treatment history to CSV format.</p>
            <button 
              class="btn btn-primary"
              @click="exportPatientHistory"
              :disabled="taskStore.loading"
            >
              <span v-if="taskStore.loading" class="spinner-border spinner-border-sm me-2"></span>
              {{ taskStore.loading ? 'Exporting...' : 'Export to CSV' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Doctor Export Section -->
      <div class="col-md-6" v-if="isDoctor">
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">Export Appointments</h5>
          </div>
          <div class="card-body">
            <form @submit.prevent="exportDoctorAppointments">
              <div class="row">
                <div class="col-md-6">
                  <div class="mb-3">
                    <label class="form-label">Start Date</label>
                    <input
                      type="date"
                      class="form-control"
                      v-model="doctorExportForm.startDate"
                      required
                    >
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="mb-3">
                    <label class="form-label">End Date</label>
                    <input
                      type="date"
                      class="form-control"
                      v-model="doctorExportForm.endDate"
                      required
                    >
                  </div>
                </div>
              </div>
              <button 
                type="submit" 
                class="btn btn-primary"
                :disabled="taskStore.loading"
              >
                <span v-if="taskStore.loading" class="spinner-border spinner-border-sm me-2"></span>
                {{ taskStore.loading ? 'Exporting...' : 'Export to CSV' }}
              </button>
            </form>
          </div>
        </div>
      </div>

      <!-- Doctor Report Section -->
      <div class="col-md-6" v-if="isDoctor">
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">Generate Custom Report</h5>
          </div>
          <div class="card-body">
            <form @submit.prevent="generateCustomReport">
              <div class="row">
                <div class="col-md-6">
                  <div class="mb-3">
                    <label class="form-label">Start Date</label>
                    <input
                      type="date"
                      class="form-control"
                      v-model="reportForm.startDate"
                      required
                    >
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="mb-3">
                    <label class="form-label">End Date</label>
                    <input
                      type="date"
                      class="form-control"
                      v-model="reportForm.endDate"
                      required
                    >
                  </div>
                </div>
              </div>
              <div class="mb-3">
                <label class="form-label">Email Address</label>
                <input
                  type="email"
                  class="form-control"
                  v-model="reportForm.email"
                  :placeholder="userEmail"
                >
              </div>
              <button 
                type="submit" 
                class="btn btn-success"
                :disabled="taskStore.loading"
              >
                <span v-if="taskStore.loading" class="spinner-border spinner-border-sm me-2"></span>
                {{ taskStore.loading ? 'Generating...' : 'Generate PDF Report' }}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>

    <!-- Task Status Monitor -->
    <div class="row mt-4" v-if="currentTask">
      <div class="col-12">
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">Task Status</h5>
          </div>
          <div class="card-body">
            <div class="alert" :class="statusAlertClass">
              <div class="d-flex justify-content-between align-items-center">
                <div>
                  <strong>Task ID:</strong> {{ currentTask.task_id }}<br>
                  <strong>Status:</strong> {{ taskStatus || 'Pending' }}
                </div>
                <button 
                  class="btn btn-sm btn-outline-secondary"
                  @click="checkTaskStatus"
                  :disabled="checkingStatus"
                >
                  <span v-if="checkingStatus" class="spinner-border spinner-border-sm me-1"></span>
                  Refresh
                </button>
              </div>
            </div>

            <div v-if="taskResult" class="mt-3">
              <h6>Task Result:</h6>
              <pre class="bg-light p-3 rounded">{{ JSON.stringify(taskResult, null, 2) }}</pre>
              
              <div v-if="taskResult.status === 'completed' && taskResult.csv_content" class="mt-3">
                <button class="btn btn-success btn-sm" @click="downloadCSV">
                  <i class="fas fa-download me-1"></i>Download CSV
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Export History -->
    <div class="row mt-4">
      <div class="col-12">
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">Export History</h5>
          </div>
          <div class="card-body">
            <div class="table-responsive">
              <table class="table table-sm">
                <thead>
                  <tr>
                    <th>Type</th>
                    <th>Date</th>
                    <th>Status</th>
                    <th>Records</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="exportItem in exportHistory" :key="exportItem.id">
                    <td>{{ exportItem.type }}</td>
                    <td>{{ formatDate(exportItem.created_at) }}</td>
                    <td>
                      <span class="badge" :class="getStatusBadgeClass(exportItem.status)">
                        {{ exportItem.status }}
                      </span>
                    </td>
                    <td>{{ exportItem.record_count }}</td>
                    <td>
                      <button 
                        v-if="exportItem.status === 'completed'"
                        class="btn btn-sm btn-outline-primary"
                        @click="downloadExport(exportItem.id)"
                      >
                        <i class="fas fa-download"></i>
                      </button>
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
</template>

<script>
import { useTaskStore } from '@/store/tasks'
import { useAuthStore } from '@/store/auth'
import { ref, computed, onMounted } from 'vue'

export default {
  name: 'TaskManager',
  setup() {
    const taskStore = useTaskStore()
    const authStore = useAuthStore()
    
    const currentTask = ref(null)
    const taskStatus = ref('')
    const taskResult = ref(null)
    const checkingStatus = ref(false)
    
    const doctorExportForm = ref({
      startDate: '',
      endDate: ''
    })
    
    const reportForm = ref({
      startDate: '',
      endDate: '',
      email: ''
    })

    const exportHistory = ref([])

    // Computed properties
    const isPatient = computed(() => authStore.isPatient)
    const isDoctor = computed(() => authStore.isDoctor)
    const isAdmin = computed(() => authStore.isAdmin)
    const userEmail = computed(() => authStore.user?.email || '')

    const statusAlertClass = computed(() => {
      switch (taskStatus.value) {
        case 'SUCCESS':
          return 'alert-success'
        case 'FAILURE':
          return 'alert-danger'
        case 'STARTED':
        case 'PENDING':
          return 'alert-warning'
        default:
          return 'alert-info'
      }
    })

    // Methods
    const exportPatientHistory = async () => {
      const result = await taskStore.exportPatientHistory()
      if (result.success) {
        currentTask.value = result.data
        startStatusPolling(result.data.task_id)
      } else {
        alert('Error: ' + result.error)
      }
    }

    const exportDoctorAppointments = async () => {
      const result = await taskStore.exportDoctorAppointments(
        doctorExportForm.value.startDate,
        doctorExportForm.value.endDate
      )
      if (result.success) {
        currentTask.value = result.data
        startStatusPolling(result.data.task_id)
      } else {
        alert('Error: ' + result.error)
      }
    }

    const generateCustomReport = async () => {
      const email = reportForm.value.email || userEmail.value
      const result = await taskStore.generateCustomReport(
        reportForm.value.startDate,
        reportForm.value.endDate,
        email
      )
      if (result.success) {
        currentTask.value = result.data
        startStatusPolling(result.data.task_id)
      } else {
        alert('Error: ' + result.error)
      }
    }

    const startStatusPolling = async (taskId) => {
      const result = await taskStore.pollTaskStatus(taskId)
      if (result.success) {
        taskStatus.value = result.data.status
        taskResult.value = result.data.result
      } else {
        alert('Error polling task status: ' + result.error)
      }
    }

    const checkTaskStatus = async () => {
      if (!currentTask.value) return
      
      checkingStatus.value = true
      const result = await taskStore.getTaskStatus(currentTask.value.task_id)
      if (result.success) {
        taskStatus.value = result.data.status
        taskResult.value = result.data.result
      }
      checkingStatus.value = false
    }

    const downloadCSV = () => {
      if (taskResult.value && taskResult.value.csv_content) {
        const blob = new Blob([taskResult.value.csv_content], { type: 'text/csv' })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `export-${currentTask.value.task_id}.csv`)
        document.body.appendChild(link)
        link.click()
        link.remove()
        window.URL.revokeObjectURL(url)
      }
    }

    const downloadExport = async (exportId) => {
      const result = await taskStore.downloadExport(exportId)
      if (!result.success) {
        alert('Error downloading export: ' + result.error)
      }
    }

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString()
    }

    const getStatusBadgeClass = (status) => {
      const classes = {
        completed: 'bg-success',
        failed: 'bg-danger',
        pending: 'bg-warning',
        processing: 'bg-info'
      }
      return classes[status] || 'bg-secondary'
    }

    const loadExportHistory = async () => {
      // This would typically call an API endpoint
      // For now, use mock data
      exportHistory.value = [
        {
          id: 1,
          type: 'patient_history',
          status: 'completed',
          created_at: new Date().toISOString(),
          record_count: 15
        }
      ]
    }

    onMounted(() => {
      loadExportHistory()
      
      // Set default dates for forms
      const today = new Date()
      const oneMonthAgo = new Date(today.getFullYear(), today.getMonth() - 1, today.getDate())
      
      doctorExportForm.value.startDate = oneMonthAgo.toISOString().split('T')[0]
      doctorExportForm.value.endDate = today.toISOString().split('T')[0]
      
      reportForm.value.startDate = oneMonthAgo.toISOString().split('T')[0]
      reportForm.value.endDate = today.toISOString().split('T')[0]
      reportForm.value.email = userEmail.value
    })

    return {
      taskStore,
      currentTask,
      taskStatus,
      taskResult,
      checkingStatus,
      doctorExportForm,
      reportForm,
      exportHistory,
      isPatient,
      isDoctor,
      isAdmin,
      userEmail,
      statusAlertClass,
      exportPatientHistory,
      exportDoctorAppointments,
      generateCustomReport,
      checkTaskStatus,
      downloadCSV,
      downloadExport,
      formatDate,
      getStatusBadgeClass
    }
  }
}
</script>

<style scoped>
.task-manager {
  padding: 20px;
}

.card {
  margin-bottom: 20px;
  border: none;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.card-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 10px 10px 0 0 !important;
}

.alert {
  border: none;
  border-radius: 8px;
}

pre {
  font-size: 12px;
  max-height: 200px;
  overflow-y: auto;
}
</style>