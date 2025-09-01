<script setup>
import Encabezado from '../components/layout/encabezado.vue';
import Titulo from '../components/ui/titulo-club.vue';
import Botones from '../components/ui/botones-generales.vue';
import CalendarioComponent from '../components/admin/calendario-component.vue';
import Pie from '../components/layout/pie.vue';

// Definir nombre del componente para evitar error del linter
defineOptions({
  name: 'CalendarioView'
});
</script>

<template>
  <main>
    <Encabezado rol="Aspirante"/>
    <Titulo />
    <Botones />
    <CalendarioComponent rol="Aspirante" />
    <Pie />
  </main>
</template>
