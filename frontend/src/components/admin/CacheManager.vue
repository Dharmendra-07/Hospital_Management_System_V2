<template>
  <div class="cache-manager">
    <div class="row">
      <div class="col-12">
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">Redis Cache Management</h5>
          </div>
          <div class="card-body">
            <!-- Cache Status -->
            <div class="row mb-4">
              <div class="col-md-6">
                <div class="card bg-light">
                  <div class="card-body">
                    <h6 class="card-title">Cache Status</h6>
                    <div class="d-flex justify-content-between align-items-center">
                      <span>Redis Connection:</span>
                      <span class="badge" :class="cacheHealth.status === 'healthy' ? 'bg-success' : 'bg-danger'">
                        {{ cacheHealth.status }}
                      </span>
                    </div>
                    <div v-if="cacheHealth.redis_connected" class="mt-2">
                      <small class="text-muted">
                        Memory: {{ cacheHealth.stats?.used_memory_human }}<br>
                        Connected Clients: {{ cacheHealth.stats?.connected_clients }}<br>
                        Total Keys: {{ cacheHealth.stats?.keys_count }}
                      </small>
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="col-md-6">
                <div class="card bg-light">
                  <div class="card-body">
                    <h6 class="card-title">Cache Performance</h6>
                    <div v-if="cacheStats">
                      <div class="d-flex justify-content-between">
                        <span>Hit Rate:</span>
                        <span>{{ calculateHitRate() }}%</span>
                      </div>
                      <div class="d-flex justify-content-between">
                        <span>Total Commands:</span>
                        <span>{{ cacheStats.total_commands_processed }}</span>
                      </div>
                      <div class="progress mt-2" style="height: 8px;">
                        <div 
                          class="progress-bar bg-success" 
                          :style="{ width: calculateHitRate() + '%' }"
                        ></div>
                      </div>
                    </div>
                    <div v-else>
                      <small class="text-muted">No performance data available</small>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Cache Controls -->
            <div class="row mb-4">
              <div class="col-12">
                <h6>Cache Controls</h6>
                <div class="btn-group" role="group">
                  <button 
                    class="btn btn-outline-primary"
                    @click="clearCache('doctors::*')"
                    :disabled="clearingCache"
                  >
                    Clear Doctors Cache
                  </button>
                  <button 
                    class="btn btn-outline-primary"
                    @click="clearCache('patients::*')"
                    :disabled="clearingCache"
                  >
                    Clear Patients Cache
                  </button>
                  <button 
                    class="btn btn-outline-primary"
                    @click="clearCache('appointments::*')"
                    :disabled="clearingCache"
                  >
                    Clear Appointments Cache
                  </button>
                  <button 
                    class="btn btn-outline-warning"
                    @click="clearCache('*')"
                    :disabled="clearingCache"
                  >
                    Clear All Cache
                  </button>
                </div>
              </div>
            </div>

            <!-- Cache Patterns -->
            <div class="row">
              <div class="col-12">
                <h6>Common Cache Patterns</h6>
                <div class="table-responsive">
                  <table class="table table-sm table-bordered">
                    <thead>
                      <tr>
                        <th>Pattern</th>
                        <th>Description</th>
                        <th>Estimated Keys</th>
                        <th>Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td><code>doctors::*</code></td>
                        <td>All doctor-related cache</td>
                        <td>{{ estimateKeys('doctors::*') }}</td>
                        <td>
                          <button 
                            class="btn btn-sm btn-outline-primary"
                            @click="clearCache('doctors::*')"
                          >
                            Clear
                          </button>
                        </td>
                      </tr>
                      <tr>
                        <td><code>patients::*</code></td>
                        <td>All patient-related cache</td>
                        <td>{{ estimateKeys('patients::*') }}</td>
                        <td>
                          <button 
                            class="btn btn-sm btn-outline-primary"
                            @click="clearCache('patients::*')"
                          >
                            Clear
                          </button>
                        </td>
                      </tr>
                      <tr>
                        <td><code>appointments::*</code></td>
                        <td>All appointment-related cache</td>
                        <td>{{ estimateKeys('appointments::*') }}</td>
                        <td>
                          <button 
                            class="btn btn-sm btn-outline-primary"
                            @click="clearCache('appointments::*')"
                          >
                            Clear
                          </button>
                        </td>
                      </tr>
                      <tr>
                        <td><code>stats::*</code></td>
                        <td>All statistics cache</td>
                        <td>{{ estimateKeys('stats::*') }}</td>
                        <td>
                          <button 
                            class="btn btn-sm btn-outline-primary"
                            @click="clearCache('stats::*')"
                          >
                            Clear
                          </button>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>

            <!-- Custom Pattern -->
            <div class="row mt-3">
              <div class="col-md-8">
                <div class="input-group">
                  <input
                    type="text"
                    class="form-control"
                    placeholder="Enter cache pattern (e.g., doctors::detail::*)"
                    v-model="customPattern"
                  >
                  <button 
                    class="btn btn-outline-secondary"
                    @click="clearCache(customPattern)"
                    :disabled="!customPattern || clearingCache"
                  >
                    Clear Pattern
                  </button>
                </div>
                <small class="form-text text-muted">
                  Use * as wildcard. Example: <code>doctors::*</code> clears all doctor cache
                </small>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Performance Metrics -->
    <div class="row mt-4">
      <div class="col-12">
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">Performance Metrics</h5>
          </div>
          <div class="card-body">
            <div class="row">
              <div class="col-md-3" v-for="metric in performanceMetrics" :key="metric.name">
                <div class="card text-center">
                  <div class="card-body">
                    <h3 class="text-primary">{{ metric.value }}</h3>
                    <p class="card-text">{{ metric.name }}</p>
                    <small class="text-muted">{{ metric.description }}</small>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { cachedApi } from '@/services/cached_api'
import { ref, onMounted, computed } from 'vue'

export default {
  name: 'CacheManager',
  setup() {
    const cacheHealth = ref({})
    const cacheStats = ref(null)
    const clearingCache = ref(false)
    const customPattern = ref('')
    const performanceData = ref([])

    const performanceMetrics = computed(() => {
      if (!cacheStats.value) return []
      
      const hits = cacheStats.value.keyspace_hits || 0
      const misses = cacheStats.value.keyspace_misses || 0
      const total = hits + misses
      const hitRate = total > 0 ? ((hits / total) * 100).toFixed(1) : 0
      
      return [
        {
          name: 'Cache Hit Rate',
          value: `${hitRate}%`,
          description: 'Percentage of cache hits'
        },
        {
          name: 'Total Commands',
          value: cacheStats.value.total_commands_processed?.toLocaleString() || '0',
          description: 'Total Redis commands processed'
        },
        {
          name: 'Memory Usage',
          value: cacheStats.value.used_memory_human || '0',
          description: 'Current memory usage'
        },
        {
          name: 'Connected Clients',
          value: cacheStats.value.connected_clients || '0',
          description: 'Active Redis connections'
        }
      ]
    })

    const loadCacheHealth = async () => {
      try {
        const response = await cachedApi.get('/cached/cache/health')
        cacheHealth.value = response.data
      } catch (error) {
        console.error('Failed to load cache health:', error)
        cacheHealth.value = { status: 'unhealthy' }
      }
    }

    const loadCacheStats = async () => {
      try {
        const result = await cachedApi.getCacheStats()
        if (result.success) {
          cacheStats.value = result.data.cache_stats
        }
      } catch (error) {
        console.error('Failed to load cache stats:', error)
      }
    }

    const clearCache = async (pattern) => {
      try {
        clearingCache.value = true
        const result = await cachedApi.clearCache(pattern)
        
        if (result.success) {
          alert(`Cache cleared for pattern: ${pattern}`)
          // Reload stats
          await loadCacheStats()
          await loadCacheHealth()
        } else {
          alert('Failed to clear cache: ' + result.error)
        }
      } catch (error) {
        alert('Error clearing cache: ' + error.message)
      } finally {
        clearingCache.value = false
      }
    }

    const calculateHitRate = () => {
      if (!cacheStats.value) return 0
      
      const hits = cacheStats.value.keyspace_hits || 0
      const misses = cacheStats.value.keyspace_misses || 0
      const total = hits + misses
      
      return total > 0 ? ((hits / total) * 100).toFixed(1) : 0
    }

    const estimateKeys = (pattern) => {
      // This would typically call an API endpoint to get key counts
      // For now, return estimated values
      const estimates = {
        'doctors::*': '50-100',
        'patients::*': '100-200',
        'appointments::*': '200-500',
        'stats::*': '10-20'
      }
      return estimates[pattern] || 'N/A'
    }

    onMounted(async () => {
      await loadCacheHealth()
      await loadCacheStats()
      
      // Refresh stats every 30 seconds
      setInterval(async () => {
        await loadCacheStats()
      }, 30000)
    })

    return {
      cacheHealth,
      cacheStats,
      clearingCache,
      customPattern,
      performanceMetrics,
      clearCache,
      calculateHitRate,
      estimateKeys
    }
  }
}
</script>

<style scoped>
.cache-manager {
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

.btn-group .btn {
  border-radius: 5px;
  margin-right: 5px;
  margin-bottom: 5px;
}

code {
  background: #f8f9fa;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 0.9em;
}

.progress {
  background-color: #e9ecef;
  border-radius: 4px;
}
</style>