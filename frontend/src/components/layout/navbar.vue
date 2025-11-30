<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
    <div class="container">
      <router-link to="/" class="navbar-brand">
        🏥 Hospital Management System
      </router-link>
      
      <button 
        class="navbar-toggler" 
        type="button" 
        data-bs-toggle="collapse" 
        data-bs-target="#navbarNav"
      >
        <span class="navbar-toggler-icon"></span>
      </button>
      
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav me-auto" v-if="isAuthenticated">
          <li class="nav-item" v-if="isAdmin">
            <router-link to="/admin" class="nav-link">Admin Dashboard</router-link>
          </li>
          <li class="nav-item" v-if="isDoctor">
            <router-link to="/doctor" class="nav-link">Doctor Dashboard</router-link>
          </li>
          <li class="nav-item" v-if="isPatient">
            <router-link to="/patient" class="nav-link">Patient Dashboard</router-link>
          </li>
        </ul>
        
        <ul class="navbar-nav" v-if="isAuthenticated">
          <li class="nav-item dropdown">
            <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
              👤 {{ user.username }} ({{ user.role }})
            </a>
            <ul class="dropdown-menu">
              <li>
                <router-link to="/profile" class="dropdown-item">Profile</router-link>
              </li>
              <li><hr class="dropdown-divider"></li>
              <li>
                <button class="dropdown-item text-danger" @click="handleLogout">
                  Logout
                </button>
              </li>
            </ul>
          </li>
        </ul>
        
        <ul class="navbar-nav" v-else>
          <li class="nav-item">
            <router-link to="/login" class="nav-link">Login</router-link>
          </li>
          <li class="nav-item">
            <router-link to="/register" class="nav-link">Register</router-link>
          </li>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script>
import { useAuthStore } from '@/store/auth'
import { computed } from 'vue'

export default {
  name: 'Navbar',
  setup() {
    const authStore = useAuthStore()
    
    const handleLogout = async () => {
      await authStore.logout()
      window.location.href = '/login'
    }
    
    return {
      isAuthenticated: computed(() => authStore.isAuthenticated),
      user: computed(() => authStore.user || {}),
      isAdmin: computed(() => authStore.isAdmin),
      isDoctor: computed(() => authStore.isDoctor),
      isPatient: computed(() => authStore.isPatient),
      handleLogout
    }
  }
}
</script>