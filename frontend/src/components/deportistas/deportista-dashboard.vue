<template>
  <div class="role-dashboard deportista-dashboard">
    <div class="dashboard-header">
      <h2 class="dashboard-title">
        <i class="fas fa-running"></i>
        Panel de Deportista
      </h2>
      <p class="dashboard-subtitle">Gestiona tu información deportiva</p>
    </div>

    <div class="dashboard-grid">
      <div class="dashboard-card" @click="navigateTo('/perfil')">
        <div class="card-icon">
          <i class="fas fa-user"></i>
        </div>
        <div class="card-content">
          <h3>Ver Perfil</h3>
          <p>Consulta tu información personal</p>
        </div>
      </div>

      <div class="dashboard-card" @click="navigateTo('/actualizar-info')">
        <div class="card-icon">
          <i class="fas fa-edit"></i>
        </div>
        <div class="card-content">
          <h3>Actualizar Información</h3>
          <p>Modifica tus datos deportivos</p>
        </div>
      </div>

      <div class="dashboard-card" @click="navigateTo('/asignar-acudiente')">
        <div class="card-icon">
          <i class="fas fa-user-friends"></i>
        </div>
        <div class="card-content">
          <h3>Asignar Acudiente</h3>
          <p>Vincula un acudiente a tu cuenta</p>
        </div>
      </div>

      <div class="dashboard-card" @click="navigateTo('/mensualidades')">
        <div class="card-icon">
          <i class="fas fa-money-bill-wave"></i>
        </div>
        <div class="card-content">
          <h3>Mensualidades</h3>
          <p>Consulta el estado de pagos</p>
        </div>
      </div>

      <div class="dashboard-card" @click="navigateTo('/eventos')">
        <div class="card-icon">
          <i class="fas fa-calendar-check"></i>
        </div>
        <div class="card-content">
          <h3>Eventos</h3>
          <p>Participa en actividades deportivas</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

// Definir nombre del componente para el linter
defineOptions({
  name: 'DeportistaDashboard'
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
