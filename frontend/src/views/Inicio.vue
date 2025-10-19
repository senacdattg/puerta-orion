<script setup>
import { ref, computed } from 'vue';
import Encabezado from '../components/layout/encabezado.vue';
import MainVista from '../components/ui/main-vista.vue';
import BotonesNavegacion from '../components/ui/botones-navegacion.vue';
import FooterEnhanced from '../components/layout/pie.vue';
import CalendarioComponent from '../components/admin/calendario-component.vue';
import { useUserRole } from '@/composables/useUserRole';
import { useAuthStore } from '@/stores/auth';

// Usar el composable para obtener el rol del usuario
const { userRole } = useUserRole();

// Store de autenticación
const authStore = useAuthStore();

// Estado para mostrar/ocultar calendario
const mostrarCalendario = ref(false);

// Determinar si el usuario es regular (no admin)
const esUsuarioRegular = computed(() => {
  return !authStore.isAdmin;
});

// Función para toggle del calendario
const toggleCalendario = () => {
  mostrarCalendario.value = !mostrarCalendario.value;
};

// Definir nombre del componente para el linter
defineOptions({
  name: 'InicioPage'
});
</script>

<template>
  <main class="inicio-page">
    <Encabezado :rol="userRole"/>
    <MainVista />
    <BotonesNavegacion />

    <!-- Botón Ver Calendario - Solo para usuarios regulares -->
    <div v-if="esUsuarioRegular" class="boton-calendario-container">
      <button
        @click="toggleCalendario"
        class="boton-ver-calendario"
        :class="{ 'activo': mostrarCalendario }"
      >
        <i class="fas fa-calendar-alt"></i>
        {{ mostrarCalendario ? 'Ocultar Calendario' : 'Ver Calendario' }}
      </button>
    </div>

    <!-- Calendario inline - Solo visible cuando se activa -->
    <div v-if="esUsuarioRegular && mostrarCalendario" class="calendario-container">
      <CalendarioComponent :rol="'Usuario'" />
    </div>

    <FooterEnhanced />
  </main>
</template>

<style scoped>
.inicio-page {
  min-height: 100vh;
  background-color: #ffffff;
}

/* Contenedor del botón de calendario */
.boton-calendario-container {
  display: flex;
  justify-content: center;
  padding: 0 0 2rem 0;
  background-color: #ffffff;
}

/* Botón Ver Calendario - Estilo más integrado */
.boton-ver-calendario {
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.875rem 1.5rem;
  background: linear-gradient(135deg, #6c757d 0%, #495057 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(108, 117, 125, 0.2);
  text-transform: none;
  letter-spacing: 0.25px;
  position: relative;
  overflow: hidden;
}

.boton-ver-calendario::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s;
}

.boton-ver-calendario:hover::before {
  left: 100%;
}

.boton-ver-calendario:hover {
  background: linear-gradient(135deg, #495057 0%, #343a40 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(108, 117, 125, 0.3);
}

.boton-ver-calendario.activo {
  background: linear-gradient(135deg, #0047ab 0%, #0066cc 100%);
  box-shadow: 0 2px 8px rgba(0, 71, 171, 0.3);
}

.boton-ver-calendario.activo:hover {
  background: linear-gradient(135deg, #003d99 0%, #005bb8 100%);
  box-shadow: 0 4px 12px rgba(0, 71, 171, 0.4);
}

.boton-ver-calendario i {
  font-size: 1.1rem;
  transition: transform 0.3s ease;
}

.boton-ver-calendario:hover i {
  transform: scale(1.1);
}

/* Contenedor del calendario */
.calendario-container {
  background-color: #f8f9fa;
  padding: 1.5rem 1rem 3rem 2rem;
  margin: 0 auto 2rem auto;
  max-width: 1200px;
  border-radius: 0 0 12px 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

/* Animación suave para mostrar/ocultar */
.calendario-container {
  animation: slideDown 0.5s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Estilos específicos para el calendario en el inicio */
.calendario-container :deep(.calendario) {
  margin: 0 auto;
  max-width: 1000px;
}

.calendario-container :deep(.calendario-header) {
  text-align: center;
  margin-bottom: 2rem;
}

.calendario-container :deep(.calendario-grid) {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 1px;
  background-color: #e9ecef;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* Responsive */
@media (max-width: 768px) {
  .boton-ver-calendario {
    padding: 0.75rem 1.25rem;
    font-size: 0.9rem;
    gap: 0.5rem;
  }

  .boton-calendario-container {
    padding: 0 1rem 1.5rem 1rem;
  }

  .calendario-container {
    padding: 1rem 0.5rem 2rem 0.5rem;
    margin: 0 auto 1.5rem auto;
    max-width: 100%;
    border-radius: 0;
  }

  .calendario-container :deep(.calendario-grid) {
    gap: 0.5px;
  }
}
</style>
