<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import Encabezado from '@/components/layout/encabezado.vue'
import TituloClub from '@/components/ui/titulo-club.vue'
import DashboardHome from '@/components/layout/DashboardHome.vue'
import FooterEnhanced from '@/components/layout/pie.vue'

// Definir nombre del componente para el linter
defineOptions({
  name: 'InicioPage'
})

const authStore = useAuthStore()

// Determinar si ocultar el menú (para acudientes y deportistas que tienen su propio dashboard)
const ocultarMenu = computed(() => {
  const activeRole = authStore.activeRole
  return activeRole === 'Acudiente' || activeRole === 'Deportista'
})
</script>

<template>
  <main class="inicio-page">
    <Encabezado :sinMenu="ocultarMenu" />
    <TituloClub />
    <DashboardHome />
    <FooterEnhanced />
  </main>
</template>

<style scoped>
.inicio-page {
  min-height: 100vh;
  background-color: var(--color-blanco);
  display: flex;
  flex-direction: column;
}

.inicio-page > :deep(.dashboard-home) {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.inicio-page > :deep(.dashboard-home .main-dashboard) {
  flex: 1;
}
</style>
