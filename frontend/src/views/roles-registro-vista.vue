<script setup>
import { useRoute } from 'vue-router'
import RolesRegistro from '../components/roles/roles-registro.vue';

const route = useRoute()
const esSeleccionRol = route.name === 'seleccionar-rol'
</script>

<template>
  <main>
    <!-- Ocultar encabezado en registro de roles -->
    <RolesRegistro />
  </main>
</template>
