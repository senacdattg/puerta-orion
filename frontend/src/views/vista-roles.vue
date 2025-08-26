<script setup>
import Encabezado from '../components/layout/encabezado.vue';
import RolesUsuario from '../components/roles/roles-usurio.vue';
import Pie from '../components/ui/pie.vue';
</script>

<template>
  <main>
    <Encabezado rol="Admin"/>
    <RolesUsuario :usuario-roles="['Deportista', 'Entrenador']"/>
    <Pie />
  </main>
</template>
