<script setup>
import Encabezado from '../components/encabezado.vue';
import RolesVista from '../components/roles-registro.vue';
import Pie from '../components/pie.vue';
</script>

<template>
  <main>
    <Encabezado :sin-menu="true"/>
    <RolesVista />
    <Pie />
  </main>
</template>
