<script setup>
import Encabezado from '../components/encabezado.vue';
import Roles from '../components/roles-usurio.vue'
import Pie from '../components/pie.vue';
</script>

<template>
  <main>
    <Encabezado rol="Admin"/>
    <Roles :usuario-roles="['Deportista', 'Entrenador']"/>
    <Pie />
  </main>
</template>
