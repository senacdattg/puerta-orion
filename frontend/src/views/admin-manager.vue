<script setup>
import Encabezado from '../components/encabezado.vue';
import Admin from '@/components/permisos-admin.vue';
import Pie from '../components/pie.vue';
</script>

<template>
  <main>
    <Encabezado rol="Aspirante"/>
    <h1 class="text-2xl font-bold mb-6">Panel de Administrador</h1>
    <Admin />
    <Pie />
  </main>
</template>
