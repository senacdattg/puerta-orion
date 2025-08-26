<script setup>
import Encabezado from '../components/layout/encabezado.vue';
import Titulo from '../components/ui/titulo-club.vue';
import Botones from '../components/ui/botones-generales.vue';
import Galeria from '../components/galeria/galeria.vue';
import Pie from '../components/ui/pie.vue';
</script>

<template>
  <main>
    <Encabezado rol="Admin"/>
    <Titulo />
    <Botones />
    <Galeria />
    <Pie />
  </main>
</template>
