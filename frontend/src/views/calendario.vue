<script setup>
import Encabezado from '../components/encabezado.vue';
import Titulo from '../components/titulo-club.vue';
import Botones from '../components/botones-generales.vue';
import CalendarioComponent from '../components/calendario/calendario-component.vue';
import Pie from '../components/pie.vue';

// Definir nombre del componente para evitar error del linter
defineOptions({
  name: 'CalendarioView'
});
</script>

<template>
  <main>
    <Encabezado rol="Admin"/>
    <Titulo />
    <Botones />
    <CalendarioComponent rol="Deportista" />
    <Pie />
  </main>
</template>
