<script setup>
import Encabezado from '../components/layout/encabezado.vue';
import MainVista from '../components/ui/main-vista.vue';
import BotonesNavegacion from '../components/ui/botones-navegacion.vue';
import FooterEnhanced from '../components/layout/pie.vue';

// Definir nombre del componente para el linter
defineOptions({
  name: 'InicioPage'
})
</script>

<template>
  <main class="inicio-page">
    <Encabezado rol="Admin"/>
    <MainVista />
    <BotonesNavegacion />
    <FooterEnhanced />
  </main>
</template>

<style scoped>
.inicio-page {
  min-height: 100vh;
  background-color: #ffffff;
}
</style>
