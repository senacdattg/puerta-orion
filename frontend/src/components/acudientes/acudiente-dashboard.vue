<template>
  <div class="role-dashboard acudiente-dashboard">
    <div class="dashboard-header">
      <h2 class="dashboard-title">
        <i class="fas fa-user-friends"></i>
        Panel de Acudiente
      </h2>
      <p class="dashboard-subtitle">Gestiona la información de tus acudidos</p>
    </div>

    <!-- Sección: Gestión de Acudidos -->
    <section class="dashboard-section">
      <h3 class="section-title">
        <i class="fas fa-users"></i>
        Gestión de Acudidos
      </h3>
      <div class="dashboard-grid section-grid">
        <div class="dashboard-card card-primary" @click="navigateTo('/ver-acudidos')">
          <div class="card-icon primary">
            <i class="fas fa-users"></i>
          </div>
          <div class="card-content">
            <h3>Gestión de Acudidos</h3>
            <p>Consulta y asigna deportistas a tu cuenta</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Sección: Información del Club -->
    <section class="dashboard-section">
      <h3 class="section-title">
        <i class="fas fa-club"></i>
        Información del Club
      </h3>
      <div class="dashboard-grid section-grid">
        <div class="dashboard-card card-secondary" @click="navigateTo('/mensualidades')">
          <div class="card-icon secondary">
            <i class="fas fa-money-bill-wave"></i>
          </div>
          <div class="card-content">
            <h3>Mensualidades</h3>
            <p>Consulta el estado de pagos</p>
          </div>
        </div>

        <div class="dashboard-card card-secondary" @click="navigateTo('/calendario')">
          <div class="card-icon secondary">
            <i class="fas fa-calendar-alt"></i>
          </div>
          <div class="card-content">
            <h3>Calendario</h3>
            <p>Ver actividades y eventos del club</p>
          </div>
        </div>

        <div class="dashboard-card card-secondary" @click="navigateTo('/galeria')">
          <div class="card-icon secondary">
            <i class="fas fa-images"></i>
          </div>
          <div class="card-content">
            <h3>Galería</h3>
            <p>Fotos de eventos y actividades</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Sección: Mi Perfil -->
    <section class="dashboard-section">
      <h3 class="section-title">
        <i class="fas fa-user"></i>
        Mi Perfil
      </h3>
      <div class="dashboard-grid section-grid">
        <div class="dashboard-card card-primary" @click="navigateTo('/perfil')">
          <div class="card-icon primary">
            <i class="fas fa-user-circle"></i>
          </div>
          <div class="card-content">
            <h3>Mi Perfil</h3>
            <p>Revisa y actualiza tu información personal</p>
          </div>
        </div>
      </div>
    </section>
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
/* Estilos específicos para el dashboard de acudiente */

.dashboard-section {
  margin-bottom: 2.5rem;
}

.dashboard-section:last-child {
  margin-bottom: 0;
}

.section-title {
  font-size: 1.3rem;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 1.25rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding-bottom: 0.75rem;
  border-bottom: 2px solid #e2e8f0;
}

.section-title i {
  color: #0047ab;
  font-size: 1.4rem;
}

.section-grid {
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
}

.dashboard-card {
  cursor: pointer;
  transition: all 0.3s ease;
  border-radius: 12px;
  overflow: hidden;
  position: relative;
}

.dashboard-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

.card-primary {
  border-left: 4px solid #f7d600;
}

.card-primary .card-icon.primary {
  background: #f7d600;
  color: #0047ab;
  font-weight: bold;
}

.card-secondary {
  border-left: 4px solid #0047ab;
}

.card-secondary .card-icon.secondary {
  background: #0047ab;
  color: white;
}

.card-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.75rem;
  margin-bottom: 1rem;
}

.card-content h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1a202c;
  margin-bottom: 0.5rem;
}

.card-content p {
  color: #718096;
  font-size: 0.95rem;
  line-height: 1.5;
}


/* Responsive */
@media (max-width: 768px) {
  .section-grid {
    grid-template-columns: 1fr;
  }
}
</style>
