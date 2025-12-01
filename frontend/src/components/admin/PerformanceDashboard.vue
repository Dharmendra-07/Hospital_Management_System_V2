<template>
  <div class="performance-dashboard">
    <div class="row">
      <div class="col-12">
        <h4 class="mb-4">System Performance Dashboard</h4>
      </div>
    </div>

    <!-- Key Metrics -->
    <div class="row mb-4">
      <div class="col-xl-3 col-md-6 mb-4">
        <div class="card border-left-primary shadow h-100 py-2">
          <div class="card-body">
            <div class="row no-gutters align-items-center">
              <div class="col mr-2">
                <div class="text-xs font-weight-bold text-primary text-uppercase mb-1">
                  Cache Hit Rate
                </div>
                <div class="h5 mb-0 font-weight-bold text-gray-800">
                  {{ hitRate }}%
                </div>
              </div>
              <div class="col-auto">
                <i class="fas fa-bolt fa-2x text-gray-300"></i>
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
                  Avg Response Time
                </div>
                <div class="h5 mb-0 font-weight-bold text-gray-800">
                  {{ avgResponseTime }}ms
                </div>
              </div>
              <div class="col-auto">
                <i class="fas fa-tachometer-alt fa-2x text-gray-300"></i>
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
                  Memory Usage
                </div>
                <div class="h5 mb-0 font-weight-bold text-gray-800">
                  {{ memoryUsage }}
                </div>
              </div>
              <div class="col-auto">
                <i class="fas fa-memory fa-2x text-gray-300"></i>
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
                  Active Connections
                </div>
                <div class="h5 mb-0 font-weight-bold text-gray-800">
                  {{ activeConnections }}
                </div>
              </div>
              <div class="col-auto">
                <i class="fas fa-plug fa-2x text-gray-300"></i>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Cache Statistics -->
    <div class="row">
      <div class="col-lg-8">
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">Cache Performance Over Time</h5>
          </div>
          <div class="card-body">
            <div class="chart-container">
              <canvas ref="cacheChart"></canvas>
            </div>
          </div>
        </div>
      </div>

      <div class="col-lg-4">
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">Cache Distribution</h5>
          </div>
          <div class="card-body">
            <div class="chart-container">
              <canvas ref="distributionChart"></canvas>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Endpoint Performance -->
    <div class="row mt-4">
      <div class="col-12">
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">Endpoint Performance</h5>
          </div>
          <div class="card-body">
            <div class="table-responsive">
              <table class="table table-sm table-hover">
                <thead>
                  <tr>
                    <th>Endpoint</th>
                    <th>Avg Response Time</th>
                    <th>Requests</th>
                    <th>Cache Hit Rate</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="endpoint in endpointPerformance" :key="endpoint.name">
                    <td>
                      <code>{{ endpoint.name }}</code>
                    </td>
                    <td>
                      <span class="badge" :class="getResponseTimeClass(endpoint.avgTime)">
                        {{ endpoint.avgTime }}ms
                      </span>
                    </td>
                    <td>{{ endpoint.requests }}</td>
                    <td>
                      <div class="progress" style="height: 8px;">
                        <div 
                          class="progress-bar" 
                          :class="getHitRateClass(endpoint.hitRate)"
                          :style="{ width: endpoint.hitRate + '%' }"
                        ></div>
                      </div>
                      <small>{{ endpoint.hitRate }}%</small>
                    </td>
                    <td>
                      <span class="badge" :class="endpoint.healthy ? 'bg-success' : 'bg-warning'">
                        {{ endpoint.healthy ? 'Healthy' : 'Slow' }}
                      </span>
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
import { ref, onMounted, computed } from 'vue'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

export default {
  name: 'PerformanceDashboard',
  setup() {
    const cacheChart = ref(null)
    const distributionChart = ref(null)
    
    const cacheStats = ref({
      hits: 1250,
      misses: 250,
      memory: '45.2 MB',
      connections: 3
    })

    const endpointPerformance = ref([
      { name: 'GET /cached/doctors', avgTime: 45, requests: 1200, hitRate: 85, healthy: true },
      { name: 'GET /cached/doctors/{id}', avgTime: 23, requests: 800, hitRate: 92, healthy: true },
      { name: 'GET /cached/departments', avgTime: 38, requests: 450, hitRate: 78, healthy: true },
      { name: 'GET /cached/patient/appointments', avgTime: 67, requests: 600, hitRate: 65, healthy: true },
      { name: 'POST /appointments', avgTime: 120, requests: 150, hitRate: 0, healthy: false }
    ])

    const hitRate = computed(() => {
      const total = cacheStats.value.hits + cacheStats.value.misses
      return total > 0 ? ((cacheStats.value.hits / total) * 100).toFixed(1) : 0
    })

    const avgResponseTime = computed(() => {
      const times = endpointPerformance.value.map(e => e.avgTime)
      return times.length > 0 ? Math.round(times.reduce((a, b) => a + b) / times.length) : 0
    })

    const memoryUsage = computed(() => cacheStats.value.memory)
    const activeConnections = computed(() => cacheStats.value.connections)

    const getResponseTimeClass = (time) => {
      if (time < 50) return 'bg-success'
      if (time < 100) return 'bg-warning'
      return 'bg-danger'
    }

    const getHitRateClass = (rate) => {
      if (rate >= 80) return 'bg-success'
      if (rate >= 60) return 'bg-warning'
      return 'bg-danger'
    }

    const initCharts = () => {
      // Cache Performance Chart
      if (cacheChart.value) {
        new Chart(cacheChart.value, {
          type: 'line',
          data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            datasets: [
              {
                label: 'Cache Hits',
                data: [65, 75, 80, 85, 82, 88],
                borderColor: '#28a745',
                backgroundColor: 'rgba(40, 167, 69, 0.1)',
                tension: 0.4
              },
              {
                label: 'Cache Misses',
                data: [35, 25, 20, 15, 18, 12],
                borderColor: '#dc3545',
                backgroundColor: 'rgba(220, 53, 69, 0.1)',
                tension: 0.4
              }
            ]
          },
          options: {
            responsive: true,
            plugins: {
              title: {
                display: true,
                text: 'Cache Performance Trends'
              }
            }
          }
        })
      }

      // Cache Distribution Chart
      if (distributionChart.value) {
        new Chart(distributionChart.value, {
          type: 'doughnut',
          data: {
            labels: ['Doctors', 'Patients', 'Appointments', 'Statistics', 'Other'],
            datasets: [{
              data: [35, 25, 20, 15, 5],
              backgroundColor: [
                '#007bff',
                '#28a745',
                '#ffc107',
                '#dc3545',
                '#6c757d'
              ]
            }]
          },
          options: {
            responsive: true,
            plugins: {
              legend: {
                position: 'bottom'
              },
              title: {
                display: true,
                text: 'Cache Key Distribution'
              }
            }
          }
        })
      }
    }

    onMounted(() => {
      initCharts()
    })

    return {
      cacheChart,
      distributionChart,
      cacheStats,
      endpointPerformance,
      hitRate,
      avgResponseTime,
      memoryUsage,
      activeConnections,
      getResponseTimeClass,
      getHitRateClass
    }
  }
}
</script>

<style scoped>
.performance-dashboard {
  padding: 20px;
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

.chart-container {
  position: relative;
  height: 300px;
}

.table code {
  background: #f8f9fa;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 0.85em;
}

.progress {
  background-color: #e9ecef;
}
</style>