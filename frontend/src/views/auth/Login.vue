<template>
  <div class="auth-container">
    <div class="row justify-content-center">
      <div class="col-md-6 col-lg-4">
        <div class="card shadow">
          <div class="card-header bg-primary text-white text-center">
            <h4 class="mb-0">Hospital Login</h4>
          </div>
          <div class="card-body p-4">
            <form @submit.prevent="handleLogin">
              <div v-if="error" class="alert alert-danger alert-dismissible fade show" role="alert">
                {{ error }}
                <button type="button" class="btn-close" @click="error = ''"></button>
              </div>

              <div class="mb-3">
                <label for="username" class="form-label">Username</label>
                <input
                  type="text"
                  class="form-control"
                  id="username"
                  v-model="form.username"
                  required
                  :disabled="loading"
                >
              </div>

              <div class="mb-3">
                <label for="password" class="form-label">Password</label>
                <input
                  type="password"
                  class="form-control"
                  id="password"
                  v-model="form.password"
                  required
                  :disabled="loading"
                >
              </div>

              <button 
                type="submit" 
                class="btn btn-primary w-100" 
                :disabled="loading"
              >
                <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                {{ loading ? 'Logging in...' : 'Login' }}
              </button>
            </form>

            <div class="text-center mt-3">
              <p class="mb-0">
                Don't have an account? 
                <router-link to="/register" class="text-decoration-none">Register as Patient</router-link>
              </p>
              <small class="text-muted">
                Doctors and Admins are registered by system administrator
              </small>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useAuthStore } from '@/store/auth'

export default {
  name: 'LoginView',
  data() {
    return {
      form: {
        username: '',
        password: ''
      },
      loading: false,
      error: ''
    }
  },
  methods: {
    async handleLogin() {
      this.loading = true
      this.error = ''

      const authStore = useAuthStore()
      const result = await authStore.login(this.form)

      if (result.success) {
        // Redirect based on role
        const role = authStore.user.role
        switch (role) {
          case 'admin':
            this.$router.push('/admin')
            break
          case 'doctor':
            this.$router.push('/doctor')
            break
          case 'patient':
            this.$router.push('/patient')
            break
          default:
            this.$router.push('/')
        }
      } else {
        this.error = result.error
      }

      this.loading = false
    }
  }
}
</script>

<style scoped>
.auth-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.card {
  border: none;
  border-radius: 15px;
}

.card-header {
  border-radius: 15px 15px 0 0 !important;
  padding: 1.5rem;
}
</style>