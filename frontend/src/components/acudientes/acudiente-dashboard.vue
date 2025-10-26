<template>
  <div class="role-dashboard acudiente-dashboard">
    <div class="dashboard-header">
      <h2 class="dashboard-title">
        <i class="fas fa-user-friends"></i>
        Panel de Acudiente
      </h2>
      <p class="dashboard-subtitle">Gestiona la información de tus acudidos</p>
    </div>

    <div class="dashboard-grid">
      <div class="dashboard-card" @click="navigateTo('/ver-acudidos')">
        <div class="card-icon">
          <i class="fas fa-users"></i>
        </div>
        <div class="card-content">
          <h3>Ver Acudidos</h3>
          <p>Consulta la información de tus deportistas</p>
        </div>
      </div>

      <div class="dashboard-card" @click="navigateTo('/asignar-acudido')">
        <div class="card-icon">
          <i class="fas fa-user-plus"></i>
        </div>
        <div class="card-content">
          <h3>Asignar Acudido</h3>
          <p>Vincula un deportista a tu cuenta</p>
        </div>
      </div>

      <div class="dashboard-card" @click="navigateTo('/actualizar-info')">
        <div class="card-icon">
          <i class="fas fa-edit"></i>
        </div>
        <div class="card-content">
          <h3>Actualizar Información</h3>
          <p>Modifica tus datos personales</p>
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

      <div class="dashboard-card" @click="navigateTo('/perfil')">
        <div class="card-icon">
          <i class="fas fa-user"></i>
        </div>
        <div class="card-content">
          <h3>Ver Perfil</h3>
          <p>Revisa tu información personal</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

// Definir nombre del componente para el linter
defineOptions({
  name: 'AcudienteDashboard'
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
