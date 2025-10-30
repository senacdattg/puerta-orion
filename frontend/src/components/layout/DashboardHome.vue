lll<template>
  <div class="dashboard-home">
    <!-- Banner de registro incompleto para usuarios base -->
    <RegistrationBanner v-if="showRegistrationBanner" />

    <!-- Panel principal según rol -->
    <div class="main-dashboard">
      <!-- Panel para Acudiente -->
      <AcudienteDashboard v-if="isAcudiente" />

      <!-- Panel para Entrenador (no para Administradores) -->
      <AdminDashboard v-if="userRole === 'Entrenador'" />

      <!-- Panel básico para usuarios sin rol específico -->
      <BasicDashboard v-if="!isAcudiente && userRole !== 'Entrenador' && !isDeportista" />
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserRole } from '@/composables/useUserRole'
import RegistrationBanner from '@/components/ui/registration-banner.vue'
import AcudienteDashboard from '@/views/AcudienteDashboard.vue'
import AdminDashboard from '@/components/admin/admin-dashboard.vue'
import BasicDashboard from '@/components/ui/basic-dashboard.vue'

// Definir nombre del componente para el linter
defineOptions({
  name: 'DashboardHome'
})

const router = useRouter()
const { userRole, isDeportista, isAcudiente } = useUserRole()

// Determinar si mostrar el banner de registro
const showRegistrationBanner = computed(() => {
  return userRole.value === 'Usuario' || userRole.value === 'usuario'
})

// Redirigir usuarios a sus paneles específicos
onMounted(() => {
  if (isDeportista.value) {
    router.replace('/deportista/dashboard')
  } else if (isAcudiente.value) {
    router.replace('/acudiente/dashboard')
  } else if (userRole.value === 'Administrador' || userRole.value === 'SuperAdmin') {
    router.replace('/admin-manager')
  }
})
</script>

<style scoped>
/* Los estilos están en /assets/css/dashboards.css */
</style>

