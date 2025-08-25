<script setup>
import Encabezado from '../components/iu/encabezado.vue';
import HeroSection from '../components/ui/hero-section.vue';
import QuickNavigation from '../components/ui/quick-navigation.vue';
import FooterEnhanced from '../components/layout/footer-enhanced.vue';

// Definir nombre del componente para el linter
defineOptions({
  name: 'InicioPage'
})
</script>

<template>
  <main class="inicio-page">
    <Encabezado rol="Admin"/>
    <HeroSection />
    <QuickNavigation />
    <FooterEnhanced />
  </main>
</template>

<style scoped>
.inicio-page {
  min-height: 100vh;
  background-color: #ffffff;
}
</style>
