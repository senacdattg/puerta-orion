<template>
  <div class="role-dashboard basic-dashboard">
    <div class="dashboard-header">
      <h2 class="dashboard-title">
        <i class="fas fa-home"></i>
        Bienvenido
      </h2>
      <p class="dashboard-subtitle">Accede a las funcionalidades básicas del club</p>
    </div>

    <div class="dashboard-grid">
      <div class="dashboard-card" @click="navigateTo('/calendario')">
        <div class="card-icon">
          <i class="fas fa-calendar-alt"></i>
        </div>
        <div class="card-content">
          <h3>Calendario</h3>
          <p>Consulta las actividades del club</p>
        </div>
      </div>

      <div class="dashboard-card" @click="navigateTo('/galeria')">
        <div class="card-icon">
          <i class="fas fa-images"></i>
        </div>
        <div class="card-content">
          <h3>Galería</h3>
          <p>Ve las fotos de eventos</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

// Definir nombre del componente para el linter
defineOptions({
  name: 'BasicDashboard'
})

const router = useRouter()

// Función para navegar a rutas
const navigateTo = (route) => {
  router.push(route)
}
</script>

