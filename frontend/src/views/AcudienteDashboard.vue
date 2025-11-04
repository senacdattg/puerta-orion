<template>
  <div class="acudiente-dashboard-page">
    <Encabezado />

    <TituloClub />

    <div class="dashboard-layout">
      <div class="dashboard-main">
        <div class="main-content">
          <div class="welcome-section">
            <h1 class="welcome-title">Panel del Acudiente</h1>
            <p class="welcome-subtitle">
              Bienvenido, gestiona la información de tus acudidos y mantente al día con las actividades del club
            </p>
          </div>

          <div class="cards-grid">
            <CardDeportista
              title="Mis Acudidos"
              description="Consulta y gestiona los deportistas asociados a tu cuenta"
              icon="fas fa-users"
              to="/ver-acudidos"
            />

            <CardDeportista
              title="Mensualidades"
              description="Consulta el estado de pagos y mensualidades"
              icon="fas fa-money-bill-wave"
              to="/mensualidades"
            />

            <CardDeportista
              title="Eventos"
              description="Participa en los próximos eventos y actividades deportivas"
              icon="fas fa-calendar-check"
              :value="eventosProximosCount"
              to="/eventos"
            />

            <CardDeportista
              title="Calendario"
              description="Consulta el calendario completo de actividades"
              icon="fas fa-calendar-alt"
              to="/calendario"
            />

            <CardDeportista
              title="Galería"
              description="Explora las últimas imágenes y momentos del club"
              icon="fas fa-images"
              to="/galeria"
            />
          </div>
        </div>
      </div>
    </div>

    <FooterEnhanced />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import Encabezado from '@/components/layout/encabezado.vue'
import CardDeportista from '@/components/deportistas/CardDeportista.vue'
import TituloClub from '@/components/ui/titulo-club.vue'
import FooterEnhanced from '@/components/layout/pie.vue'
import calendarioService from '@/services/calendarioService'

defineOptions({
  name: 'AcudienteDashboard'
})

const eventosProximos = ref([])
const cargandoEventos = ref(false)

const eventosProximosCount = computed(() => {
  if (cargandoEventos.value) {
    return '...'
  }
  return eventosProximos.value.length > 0 ? eventosProximos.value.length.toString() : '0'
})

const cargarEventosProximos = async () => {
  cargandoEventos.value = true
  try {
    const eventos = await calendarioService.obtenerEventosProximos()
    eventosProximos.value = eventos || []
  } catch (error) {
    console.error('Error al cargar eventos próximos:', error)
    eventosProximos.value = []
  } finally {
    cargandoEventos.value = false
  }
}

onMounted(() => {
  console.log('✅ AcudienteDashboard montado')
  cargarEventosProximos()
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

@media (max-width: 768px) {
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
</style>

