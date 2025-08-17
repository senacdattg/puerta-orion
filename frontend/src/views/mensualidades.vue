<script setup>
import Encabezado from '../components/encabezado.vue';
import TablaMensualidades from '../components/tabla-mensualidades.vue';
import Pie from '../components/pie.vue';
</script>

<template>
  <main>
    <Encabezado rol="Entrenador"/>
    <TablaMensualidades />
    <Pie />
  </main>
</template>
