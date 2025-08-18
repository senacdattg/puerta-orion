<script setup>
import Encabezado from '../components/encabezado.vue';
import RolesVista from '../components/roles-registro.vue';
import Pie from '../components/pie.vue';
</script>

<template>
  <main>
    <Encabezado rol="Admin"/>
    <RolesVista />
    <Pie />
  </main>
</template>
