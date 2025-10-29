<template>
  <div class="deportista-dashboard-page">
    <HeaderDeportista />

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
          <div class="welcome-section">
            <h1 class="welcome-title">Panel del Deportista</h1>
            <p class="welcome-subtitle">
              Bienvenido, gestiona tu información deportiva y mantente al día con las actividades del club
            </p>
          </div>

          <div class="cards-grid">
            <CardDeportista
              title="Mis Mensualidades"
              description="Consulta el estado de tus pagos y mensualidades pendientes"
              icon="fas fa-money-bill-wave"
              :value="estadoMensualidad"
              to="/deportista/mensualidades"
            />

            <CardDeportista
              title="Eventos Próximos"
              description="Participa en los próximos eventos y actividades deportivas"
              icon="fas fa-calendar-check"
              :value="eventosProximosCount"
              to="/deportista/eventos"
            />

            <CardDeportista
              title="Galería"
              description="Explora las últimas imágenes y momentos del club"
              icon="fas fa-images"
              to="/deportista/galeria"
            />

            <CardDeportista
              title="Calendario"
              description="Consulta el calendario completo de actividades"
              icon="fas fa-calendar-alt"
              to="/deportista/calendario"
            />
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
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import HeaderDeportista from '@/components/deportistas/HeaderDeportista.vue'
import SidebarDeportista from '@/components/deportistas/SidebarDeportista.vue'
import CardDeportista from '@/components/deportistas/CardDeportista.vue'
import PerfilModal from '@/components/deportistas/PerfilModal.vue'
import TituloClub from '@/components/ui/titulo-club.vue'
import FooterEnhanced from '@/components/layout/pie.vue'

defineOptions({
  name: 'DeportistaDashboard'
})

const sidebarOpen = ref(false)
const isMobile = ref(false)
const showPerfilModal = ref(false)

const estadoMensualidad = computed(() => {
  // Aquí se podría obtener el estado real de la mensualidad desde un servicio
  return 'Al día'
})

const eventosProximosCount = computed(() => {
  // Aquí se podría obtener el conteo real de eventos próximos
  return '3'
})


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

.welcome-section {
  margin-bottom: var(--espaciado-xxl);
  text-align: center;
  animation: fadeInUp 0.6s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.welcome-title {
  font-size: var(--tamano-fuente-xxxl);
  font-weight: var(--peso-fuente-bold);
  background: linear-gradient(135deg, #004AAD 0%, #0066d6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 0 var(--espaciado-sm) 0;
  font-family: 'Poppins', sans-serif;
  letter-spacing: -0.5px;
}

.welcome-subtitle {
  font-size: var(--tamano-fuente-lg);
  color: var(--color-gris);
  margin: 0;
  line-height: 1.6;
}

.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--espaciado-lg);
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

