<template>
  <div class="acudiente-dashboard-page">
    <Encabezado />

    <TituloClub />

    <div class="dashboard-layout">
      <div class="dashboard-main">
        <div class="main-content">
          <div class="role-dashboard acudiente-dashboard">
            <div class="dashboard-header">
              <h2 class="dashboard-title">
                <i class="fas fa-user-friends"></i>
                Panel del Acudiente
              </h2>
              <p class="dashboard-subtitle">Gestiona la información de tus acudidos y mantente al día con las actividades del club</p>
            </div>

            <div class="dashboard-grid">
              <div class="dashboard-card" @click="navigateTo('/acudiente/ver-acudidos')">
                <div class="card-icon">
                  <i class="fas fa-users"></i>
                </div>
                <div class="card-content">
                  <h3>Mis Acudidos</h3>
                  <p>Consulta y gestiona los deportistas asociados a tu cuenta</p>
                </div>
              </div>

              <div class="dashboard-card" @click="navigateTo('/mensualidades')">
                <div class="card-icon">
                  <i class="fas fa-money-bill-wave"></i>
                </div>
                <div class="card-content">
                  <h3>Mensualidades</h3>
                  <p>Consulta el estado de pagos y mensualidades</p>
                </div>
              </div>

              <div class="dashboard-card" @click="navigateTo('/eventos')">
                <div class="card-icon">
                  <i class="fas fa-calendar-check"></i>
                </div>
                <div class="card-content">
                  <h3>Eventos</h3>
                  <p>Participa en los próximos eventos y actividades deportivas</p>
                </div>
              </div>

              <div class="dashboard-card" @click="navigateTo('/calendario')">
                <div class="card-icon">
                  <i class="fas fa-calendar-alt"></i>
                </div>
                <div class="card-content">
                  <h3>Calendario</h3>
                  <p>Consulta el calendario completo de actividades</p>
                </div>
              </div>

              <div class="dashboard-card" @click="navigateTo('/galeria')">
                <div class="card-icon">
                  <i class="fas fa-images"></i>
                </div>
                <div class="card-content">
                  <h3>Galería</h3>
                  <p>Explora las últimas imágenes y momentos del club</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <FooterEnhanced />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import Encabezado from '@/components/layout/encabezado.vue'
import TituloClub from '@/components/ui/titulo-club.vue'
import FooterEnhanced from '@/components/layout/pie.vue'

defineOptions({
  name: 'AcudienteDashboard'
})

const router = useRouter()

const navigateTo = (route) => {
  router.push(route)
}

onMounted(() => {
  console.log('✅ AcudienteDashboard montado')
})
</script>

<style scoped>
.acudiente-dashboard-page {
  min-height: 100vh;
  background: var(--color-gris-claro);
  display: flex;
  flex-direction: column;
  padding-top: 70px;
}

.dashboard-layout {
  display: flex;
  flex: 1;
  position: relative;
}

.dashboard-main {
  flex: 1;
  min-height: calc(100vh - 70px);
}

.main-content {
  padding: var(--espaciado-xl);
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}

@media (max-width: 768px) {
  .main-content {
    padding: var(--espaciado-md);
  }
}
</style>

