<template>
  <div class="deportista-dashboard-page">
    <Encabezado />

    <TituloClub />

    <div class="dashboard-layout">
      <SidebarDeportista
        :isOpen="sidebarOpen"
        @close="sidebarOpen = false"
      />

      <button
        class="mobile-sidebar-toggle"
        @click="sidebarOpen = !sidebarOpen"
        v-if="isMobile"
      >
        <i class="fas fa-bars"></i>
      </button>

      <div
        class="dashboard-main"
        :class="{ 'sidebar-open': sidebarOpen && isMobile }"
        @click="handleMainClick"
      >
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
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import Encabezado from '@/components/layout/encabezado.vue'
import SidebarDeportista from '@/components/deportistas/SidebarDeportista.vue'
import PerfilModal from '@/components/deportistas/PerfilModal.vue'
import TituloClub from '@/components/ui/titulo-club.vue'
import FooterEnhanced from '@/components/layout/pie.vue'

defineOptions({
  name: 'DeportistaDashboard'
})

const router = useRouter()
const sidebarOpen = ref(false)
const isMobile = ref(false)
const showPerfilModal = ref(false)

const navigateTo = (route) => {
  router.push(route)
}

const handleMainClick = () => {
  if (isMobile.value && sidebarOpen.value) {
    sidebarOpen.value = false
  }
}

const handlePerfilUpdate = () => {
  // Recargar datos del usuario si es necesario
  console.log('Perfil actualizado')
}

const checkMobile = () => {
  isMobile.value = window.innerWidth < 768
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', checkMobile)
})
</script>

<style scoped>
.deportista-dashboard-page {
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
  margin-left: 250px;
  transition: margin-left var(--transicion);
  min-height: calc(100vh - 70px);
}

.main-content {
  padding: var(--espaciado-xl);
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}

.mobile-sidebar-toggle {
  display: none;
  position: fixed;
  top: 80px;
  left: var(--espaciado-md);
  z-index: calc(var(--z-fixed) + 1);
  background: #004AAD;
  color: var(--color-blanco);
  border: none;
  border-radius: var(--radio-borde);
  padding: var(--espaciado-sm) var(--espaciado-md);
  cursor: pointer;
  box-shadow: var(--sombra-media);
  transition: var(--transicion);
}

.mobile-sidebar-toggle:hover {
  background: #003d8f;
  transform: scale(1.05);
}

/* Responsive */
@media (max-width: 768px) {
  .dashboard-main {
    margin-left: 0;
  }

  .dashboard-main.sidebar-open {
    margin-left: 0;
  }

  .mobile-sidebar-toggle {
    display: block;
  }

  .main-content {
    padding: var(--espaciado-md);
  }

  .welcome-title {
    font-size: var(--tamano-fuente-xxl);
  }

  .welcome-subtitle {
    font-size: var(--tamano-fuente-base);
  }

  .cards-grid {
    grid-template-columns: 1fr;
    gap: var(--espaciado-md);
  }
}

/* Overlay para móvil cuando sidebar está abierto */
@media (max-width: 768px) {
  .dashboard-main.sidebar-open::before {
    content: '';
    position: fixed;
    top: 70px;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    z-index: calc(var(--z-fixed) - 1);
  }
}
</style>

