<template>
  <div class="deportista-dashboard-page">
    <Encabezado />

    <TituloClub />

    <div class="dashboard-layout">
      <div class="dashboard-main">
        <div class="main-content">
          <div class="role-dashboard deportista-dashboard">
            <div class="dashboard-header">
              <h2 class="dashboard-title">
                <i class="fas fa-user"></i>
                Panel del Deportista
              </h2>
              <p class="dashboard-subtitle">Gestiona tu información deportiva y mantente al día con las actividades del club</p>
            </div>

            <div class="dashboard-grid">
              <div class="dashboard-card" @click="navigateTo('/perfil')">
                <div class="card-icon">
                  <i class="fas fa-user"></i>
                </div>
                <div class="card-content">
                  <h3>Mi Perfil</h3>
                  <p>Gestiona tu información personal y deportiva</p>
                </div>
          </div>

              <div class="dashboard-card" @click="navigateTo('/mensualidades')">
                <div class="card-icon">
                  <i class="fas fa-money-bill-wave"></i>
                </div>
                <div class="card-content">
                  <h3>Mis Mensualidades</h3>
                  <p>Consulta el estado de tus pagos y mensualidades pendientes</p>
                </div>
              </div>

              <div class="dashboard-card" @click="navigateTo('/eventos')">
                <div class="card-icon">
                  <i class="fas fa-calendar-check"></i>
                </div>
                <div class="card-content">
                  <h3>Eventos Próximos</h3>
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

    <PerfilModal
      :visible="showPerfilModal"
      @close="showPerfilModal = false"
      @update="handlePerfilUpdate"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import Encabezado from '@/components/layout/encabezado.vue'
import PerfilModal from '@/components/deportistas/PerfilModal.vue'
import TituloClub from '@/components/ui/titulo-club.vue'
import FooterEnhanced from '@/components/layout/pie.vue'

defineOptions({
  name: 'DeportistaDashboard'
})

const router = useRouter()
const showPerfilModal = ref(false)

const navigateTo = (route) => {
  router.push(route)
}

const handlePerfilUpdate = () => {
  // Recargar datos del usuario si es necesario
  console.log('Perfil actualizado')
}
</script>


