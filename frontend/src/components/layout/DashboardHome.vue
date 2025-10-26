<template>
  <div class="dashboard-home">
    <!-- Banner de registro incompleto para usuarios base -->
    <RegistrationBanner v-if="showRegistrationBanner" />

    <!-- Panel principal según rol -->
    <div class="main-dashboard">
      <!-- Panel para Acudiente -->
      <AcudienteDashboard v-if="isAcudiente" />

      <!-- Panel para Deportista -->
      <DeportistaDashboard v-else-if="isDeportista" />

      <!-- Panel para Administrador/Entrenador -->
      <AdminDashboard v-else-if="isAdminOrCoach" />

      <!-- Panel básico para usuarios sin rol específico -->
      <BasicDashboard v-else />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useUserRole } from '@/composables/useUserRole'
import RegistrationBanner from '@/components/ui/registration-banner.vue'
import AcudienteDashboard from '@/components/acudientes/acudiente-dashboard.vue'
import DeportistaDashboard from '@/components/deportistas/deportista-dashboard.vue'
import AdminDashboard from '@/components/admin/admin-dashboard.vue'
import BasicDashboard from '@/components/ui/basic-dashboard.vue'

// Definir nombre del componente para el linter
defineOptions({
  name: 'DashboardHome'
})

const { userRole, isAdminOrCoach, isDeportista, isAcudiente } = useUserRole()

// Determinar si mostrar el banner de registro
const showRegistrationBanner = computed(() => {
  return userRole.value === 'Usuario' || userRole.value === 'usuario'
})
</script>

<style scoped>
/* Los estilos están en /assets/css/dashboards.css */
</style>

