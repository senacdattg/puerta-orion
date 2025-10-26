<script setup>
import Encabezado from '@/components/layout/encabezado.vue'
import TituloClub from '@/components/ui/titulo-club.vue'
import DashboardHome from '@/components/layout/DashboardHome.vue'
import FooterEnhanced from '@/components/layout/pie.vue'
import { useUserRole } from '@/composables/useUserRole'

// Usar el composable para obtener el rol del usuario
const { userRole } = useUserRole()

// Definir nombre del componente para el linter
defineOptions({
  name: 'InicioPage'
})
</script>

<template>
  <main class="inicio-page">
    <Encabezado :rol="userRole" />
    <TituloClub />
    <DashboardHome />
    <FooterEnhanced />
  </main>
</template>

<style scoped>
.inicio-page {
  min-height: 100vh;
  background-color: var(--color-blanco);
}
</style>
