<script setup>
import Encabezado from '../components/encabezado.vue';
import CalendarioComponent from '../components/calendario/calendario-component.vue';
import Pie from '../components/pie.vue';
</script>

<template>
  <main>
    <Encabezado rol="Admin"/>
    <CalendarioComponent />
    <Pie />
  </main>
</template>
