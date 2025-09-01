<script setup>
import Encabezado from '../components/layout/encabezado.vue';
import RolesRegistro from '../components/roles/roles-registro.vue';
import Pie from '../components/ui/pie.vue';
</script>

<template>
  <main>
    <Encabezado rol="Admin"/>
    <RolesRegistro />
    <Pie />
  </main>
</template>
