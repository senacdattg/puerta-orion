<script setup>
import Encabezado from '../components/iu/encabezado.vue';
import RolesVista from '../components/roles/roles-registro.vue';
import Pie from '../components/iu/pie.vue';
</script>

<template>
  <main>
    <Encabezado rol="Admin"/>
    <RolesVista />
    <Pie />
  </main>
</template>
