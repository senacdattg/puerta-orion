<script setup>
import Encabezado from '../components/iu/encabezado.vue';
import Titulo from '../components/iu/titulo-club.vue';
import Botones from '../components/iu/botones-generales.vue';
import Galeria from '@/components/galeria/galeria.vue';
import Pie from '../components/iu/pie.vue';
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
