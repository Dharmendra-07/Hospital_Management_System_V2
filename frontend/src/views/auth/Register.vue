<template>
  <div class="auth-container">
    <div class="row justify-content-center">
      <div class="col-md-8 col-lg-6">
        <div class="card shadow">
          <div class="card-header bg-success text-white text-center">
            <h4 class="mb-0">Patient Registration</h4>
          </div>
          <div class="card-body p-4">
            <form @submit.prevent="handleRegister">
              <div v-if="error" class="alert alert-danger alert-dismissible fade show" role="alert">
                {{ error }}
                <button type="button" class="btn-close" @click="error = ''"></button>
              </div>

              <div class="row">
                <div class="col-md-6">
                  <div class="mb-3">
                    <label for="first_name" class="form-label">First Name *</label>
                    <input
                      type="text"
                      class="form-control"
                      id="first_name"
                      v-model="form.first_name"
                      required
                      :disabled="loading"
                    >
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="mb-3">
                    <label for="last_name" class="form-label">Last Name *</label>
                    <input
                      type="text"
                      class="form-control"
                      id="last_name"
                      v-model="form.last_name"
                      required
                      :disabled="loading"
                    >
                  </div>
                </div>
              </div>

              <div class="row">
                <div class="col-md-6">
                  <div class="mb-3">
                    <label for="username" class="form-label">Username *</label>
                    <input
                      type="text"
                      class="form-control"
                      id="username"
                      v-model="form.username"
                      required
                      :disabled="loading"
                    >
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="mb-3">
                    <label for="email" class="form-label">Email *</label>
                    <input
                      type="email"
                      class="form-control"
                      id="email"
                      v-model="form.email"
                      required
                      :disabled="loading"
                    >
                  </div>
                </div>
              </div>

              <div class="row">
                <div class="col-md-6">
                  <div class="mb-3">
                    <label for="password" class="form-label">Password *</label>
                    <input
                      type="password"
                      class="form-control"
                      id="password"
                      v-model="form.password"
                      required
                      :disabled="loading"
                    >
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="mb-3">
                    <label for="confirm_password" class="form-label">Confirm Password *</label>
                    <input
                      type="password"
                      class="form-control"
                      id="confirm_password"
                      v-model="form.confirm_password"
                      required
                      :disabled="loading"
                    >
                  </div>
                </div>
              </div>

              <div class="row">
                <div class="col-md-4">
                  <div class="mb-3">
                    <label for="date_of_birth" class="form-label">Date of Birth *</label>
                    <input
                      type="date"
                      class="form-control"
                      id="date_of_birth"
                      v-model="form.date_of_birth"
                      required
                      :disabled="loading"
                    >
                  </div>
                </div>
                <div class="col-md-4">
                  <div class="mb-3">
                    <label for="gender" class="form-label">Gender *</label>
                    <select
                      class="form-select"
                      id="gender"
                      v-model="form.gender"
                      required
                      :disabled="loading"
                    >
                      <option value="">Select Gender</option>
                      <option value="male">Male</option>
                      <option value="female">Female</option>
                      <option value="other">Other</option>
                    </select>
                  </div>
                </div>
                <div class="col-md-4">
                  <div class="mb-3">
                    <label for="blood_group" class="form-label">Blood Group</label>
                    <select
                      class="form-select"
                      id="blood_group"
                      v-model="form.blood_group"
                      :disabled="loading"
                    >
                      <option value="">Select Blood Group</option>
                      <option value="A+">A+</option>
                      <option value="A-">A-</option>
                      <option value="B+">B+</option>
                      <option value="B-">B-</option>
                      <option value="AB+">AB+</option>
                      <option value="AB-">AB-</option>
                      <option value="O+">O+</option>
                      <option value="O-">O-</option>
                    </select>
                  </div>
                </div>
              </div>

              <div class="mb-3">
                <label for="phone" class="form-label">Phone</label>
                <input
                  type="tel"
                  class="form-control"
                  id="phone"
                  v-model="form.phone"
                  :disabled="loading"
                >
              </div>

              <div class="mb-3">
                <label for="address" class="form-label">Address</label>
                <textarea
                  class="form-control"
                  id="address"
                  v-model="form.address"
                  rows="2"
                  :disabled="loading"
                ></textarea>
              </div>

              <button 
                type="submit" 
                class="btn btn-success w-100" 
                :disabled="loading || !passwordsMatch"
              >
                <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                {{ loading ? 'Registering...' : 'Register' }}
              </button>
            </form>

            <div class="text-center mt-3">
              <p class="mb-0">
                Already have an account? 
                <router-link to="/login" class="text-decoration-none">Login here</router-link>
              </p>
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
  name: 'RegisterView',
  data() {
    return {
      form: {
        first_name: '',
        last_name: '',
        username: '',
        email: '',
        password: '',
        confirm_password: '',
        date_of_birth: '',
        gender: '',
        blood_group: '',
        phone: '',
        address: ''
      },
      loading: false,
      error: ''
    }
  },
  computed: {
    passwordsMatch() {
      return this.form.password === this.form.confirm_password && this.form.password.length >= 6
    }
  },
  methods: {
    async handleRegister() {
      if (!this.passwordsMatch) {
        this.error = 'Passwords do not match or are too short (min 6 characters)'
        return
      }

      this.loading = true
      this.error = ''

      const authStore = useAuthStore()
      const result = await authStore.register(this.form)

      if (result.success) {
        this.$router.push('/patient')
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
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
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