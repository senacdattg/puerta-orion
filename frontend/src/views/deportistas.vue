<script setup>
import Encabezado from '../components/encabezado.vue';
import TablaDeportistas from '../components/tabla-deportistas.vue';
import Pie from '../components/pie.vue';
</script>

<template>
  <main>
    <Encabezado rol="Entrenador"/>
    <TablaDeportistas />
    <Pie />
  </main>
</template>
