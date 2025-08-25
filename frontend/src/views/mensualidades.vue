<script setup>
import Encabezado from '../components/iu/encabezado.vue';
import TablaMensualidades from '../components/admin/tabla-mensualidades.vue';
import Pie from '../components/iu/pie.vue';
</script>

<template>
  <main>
    <Encabezado rol="Admin"/>
    <TablaMensualidades />
    <Pie />
  </main>
</template>
