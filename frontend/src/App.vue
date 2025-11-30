<template>
  <div id="app">
    <Navbar v-if="!$route.meta.hideNavbar" />
    <main class="container-fluid p-0">
      <router-view />
    </main>
  </div>
</template>

<script>
import Navbar from '@/components/layout/Navbar.vue'
import { useAuthStore } from '@/store/auth'

export default {
  name: 'App',
  components: {
    Navbar
  },
  async created() {
    // Check authentication status on app start
    const authStore = useAuthStore()
    await authStore.checkAuth()
  }
}
</script>

<style>
#app {
  min-height: 100vh;
  background-color: #f8f9fa;
}
</style>