<script setup>
import Encabezado from '../components/iu/encabezado.vue';
import Roles from '../components/roles-usurio.vue'
import Pie from '../components/iu/pie.vue';
</script>

<template>
  <main>
    <Encabezado rol="Admin"/>
    <Roles :usuario-roles="['Deportista', 'Entrenador']"/>
    <Pie />
  </main>
</template>
