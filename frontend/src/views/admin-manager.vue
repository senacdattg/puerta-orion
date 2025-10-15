<script setup>
import Encabezado from '../components/layout/encabezado.vue';
import adminManager from '../components/admin/panel-admin-componente.vue'
import Pie from '../components/layout/pie.vue';
</script>

<template>
  <Encabezado rol="Admin" />
  <adminManager />
  <Pie />

</template>
