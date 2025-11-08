<template>
  <div class="role-dashboard admin-dashboard">
    <div class="dashboard-header">
      <h2 class="dashboard-title">
        <i class="fas fa-cog"></i>
        Panel de Administración
      </h2>
      <p class="dashboard-subtitle">Gestiona el club deportivo</p>
    </div>

    <div class="dashboard-grid">
      <div class="dashboard-card" @click="navigateTo('/deportistas')">
        <div class="card-icon">
          <i class="fas fa-users"></i>
        </div>
        <div class="card-content">
          <h3>Gestionar Deportistas</h3>
          <p>Administra la información de deportistas</p>
        </div>
      </div>

      <div class="dashboard-card" @click="navigateTo('/calendario')">
        <div class="card-icon">
          <i class="fas fa-calendar-alt"></i>
        </div>
        <div class="card-content">
          <h3>Calendario</h3>
          <p>Gestiona eventos y actividades del club</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

// Definir nombre del componente para el linter
defineOptions({
  name: 'AdminDashboard'
})

const router = useRouter()

// Función para navegar a rutas
const navigateTo = (route) => {
  router.push(route)
}
</script>

<style scoped>
/* Los estilos están en /assets/css/dashboards.css */
</style>
