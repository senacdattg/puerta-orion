<script setup>
import Encabezado from '../components/layout/encabezado.vue';
import Roles from '../components/roles/roles-usurio.vue';
import Pie from '../components/layout/pie.vue';
</script>

<template>
  <main>
    <Encabezado :sin-menu="true"/>
    <Roles :usuario-roles="['Aspirante', 'Deportista', 'Entrenador']"/>
    <Pie />
  </main>
</template>
