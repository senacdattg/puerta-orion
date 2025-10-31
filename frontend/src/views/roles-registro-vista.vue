<script setup>
import { useRoute } from 'vue-router'
import Encabezado from '../components/layout/encabezado.vue';
import RolesRegistro from '../components/roles/roles-registro.vue';
import Pie from '../components/layout/pie.vue';

const route = useRoute()
const esSeleccionRol = route.name === 'seleccionar-rol'
</script>

<template>
  <main>
    <!-- Ocultar menú, usuario y footer cuando es selección de rol -->
    <Encabezado v-if="!esSeleccionRol" />
    <RolesRegistro />
    <Pie v-if="!esSeleccionRol" />
  </main>
</template>
