<script setup>
import Encabezado from '../components/encabezado.vue';
import Titulo from '../components/titulo-club.vue';
import Botones from '../components/botones-generales.vue';
import Galeria from '@/components/galeria.vue';
import Pie from '../components/pie.vue';
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
