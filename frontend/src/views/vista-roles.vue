<script setup>
import Encabezado from '../components/encabezado.vue';
import Roles from '../components/roles-usurio.vue'
import Pie from '../components/pie.vue';
</script>

<template>
  <main>
    <Encabezado :sin-menu="true"/>
    <Roles :usuario-roles="['Aspirante', 'Deportista', 'Entrenador']"/>
    <Pie />
  </main>
</template>
