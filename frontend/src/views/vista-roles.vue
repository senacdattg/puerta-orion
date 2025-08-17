<script setup>
import Encabezado from '../components/encabezado.vue';
import Roles from '../components/roles.vue'
import Pie from '../components/pie.vue';
</script>

<template>
  <main>
    <Encabezado rol="Entrenador"/>
    <Roles :usuario-roles="['Deportista', 'Entrenador']"/>
    <Pie />
  </main>
</template>
