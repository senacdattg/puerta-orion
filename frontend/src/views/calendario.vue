<script setup>
import Encabezado from '../components/iu/encabezado.vue';
import Titulo from '../components/iu/titulo-club.vue';
import Botones from '../components/iu/botones-generales.vue';
import CalendarioComponent from '../components/admin/calendario-component.vue';
import Pie from '../components/iu/pie.vue';

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
    <CalendarioComponent rol="Admin" />
    <Pie />
  </main>
</template>
